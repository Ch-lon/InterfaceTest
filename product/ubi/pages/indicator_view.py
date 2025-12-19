# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : indicator_view.py
@Author  : Chlon
@Date    : 2025/12/12 10:12
@Desc    : 指标查看测试类
"""
import time
import traceback
import pytest
from _pytest.outcomes import Failed
from asyncio import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime
from product.ubi.pages.UbiCommon import UbiCommon
import allure
import concurrent.futures

class IndicatorView(UbiCommon):

    @allure.step("获取指标查看页当前版本的指标体系")
    def get_indicator_view_info(self):
        """
        获取指标查看页当前版本的指标体系
        :return:类似[{},{},{}]
        """
        api_indicator_info = self.al.get_api('indicator_view', 'indicator_view', 'indicator_info')
        url = api_indicator_info['url']
        response = self.ru.request(
            method=api_indicator_info['method'],
            url=url,
            headers=api_indicator_info.get('headers')
        )
        response_json = response.json()
        assert response_json["code"] == api_indicator_info["expected"]["code"], f"指标查看页指标体系请求失败！请求响应:{response_json}"
        # 指标信息是个列表
        indicators = response_json["data"]["indList"]
        all_ind_info: list = self.extract_partial_level_3_data(indicators)
        return all_ind_info

    @allure.step("从全部指标列表中只提取指标名，并组成一个列表")
    def extract_all_indicator_name(self, all_ind_info: list):
        """
        从全部指标列表中只提取指标名，并组成一个列表
        :param all_ind_info: 全部指标列表
        :return:
        """
        ind_info: list = []
        for dict_indicators in all_ind_info:
            ind_name = dict_indicators["name"]
            ind_info.append(ind_name)
        return ind_info

    @allure.step("从全部指标列表中提取指标Code和监测年份")
    def extract_indCode_and_year(self, all_ind_info: list)->list[dict]:
        """
        从全部指标列表中提取指标Code和监测年份
        :param all_ind_info: 全部指标列表
        :return:[{},{},{}]
        """
        list_ind_info = []
        for dict_indicators in all_ind_info:
            ind_name,ind_code,targetVerName = self.do.get_value_from_dict(dict_indicators, "name", "code", "targetVerName")
            # 去掉没在指标查看里的指标：SCIE论文，SSCI论文，被SCIE或SSCI收录的论文数。
            if ind_code in ["ind230","ind231","ind232"]:
                continue
            list_ind_info.append({"name": ind_name, "code": ind_code, "year": targetVerName})
        # self.logging.info(f"指标信息：{list_ind_info}")
        # print(list_ind_info)
        return list_ind_info


    @allure.step("搜索指标")
    def search_single_indicator(self, value):
        """
        搜索指标
        :param value: 指标名称
        :return:
        """
        # 需要将value进行url编码
        value_encode = self.do.url_encode(value)
        api_search_indicator = self.al.get_api('indicator_view', 'indicator_view', 'search_indicator')
        origin_url = api_search_indicator['url']
        url = self.do.format_url(origin_url, value=value_encode)
        try:
            response = self.ru.request(
                method=api_search_indicator['method'],
                url=url,
                headers=api_search_indicator.get('headers'),
            )
            response_json = response.json()
            result = response_json["data"]["indList"]
            if response_json.get("code") != api_search_indicator["expected"]["code"]:
                return {"type":"request_fail","request":value}
            if result is None:
                return {"type":"no_reason","request":value}
            else:
                return {"type":"success","request":value}
        except Exception:
            # 捕获其他非预期的异常（如网络连接错误、JSON解析错误等）
            # 使用 traceback.format_exc() 获取完整的堆栈信息
            return {'type': 'exception', 'request': value, 'error': traceback.format_exc()}

    @allure.step("使用线程池对所有指标进行并发搜索请求（submit + 重试）")
    def search_all_indicator_by_concurrent(
            self,
            list_all_only_indicators,
            max_workers=5,
            retry_times=2
    ):
        """
        使用线程池对所有指标进行搜索请求（submit + 重试）
        :param list_all_only_indicators: 只包含指标的列表
        :param max_workers: 最大线程数
        :param retry_times: 失败重试次数
        :return:
        """
        start_time = datetime.now()

        list_fail_empty_data = []  # 请求成功但数据为空（业务失败）
        list_unsearchable = []  # 多次重试仍失败（不可搜索指标）
        list_success = [] # 请求成功（业务成功）

        def task_with_retry(ind_name):
            """
            单个指标搜索 + 重试封装
            """
            # rang(1,4)即1,2,3，没有第4次循环。 range() 函数的左闭右开区间特性：[start, stop)
            for attempt in range(1, retry_times + 2):  # 第一次 + 重试
                result = self.search_single_indicator(ind_name)
                if result["type"] == "success":
                    return result
                # 数据为空，不重试
                if result["type"] == "no_reason":
                    return result
                # 接口失败，重试
                if attempt <= retry_times:
                    print(f"⚠️ 指标 [{ind_name}] 第 {attempt}/{retry_times} 次失败，开始重试...")
                    time.sleep(0.3)
                else:
                    return {
                        "type": "retry_fail",
                        "request": ind_name,
                        "detail": result
                    }
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Future = “一个正在执行或即将执行的任务”，类似快递单号
            # future_to_ind是个字典推导式：键为 Future 对象，值为对应指标名称。如:
            # {
            # <Future at 0x7f8a1c01a1c0 state=running>: "高被引",
            # <Future at 0x7f8a1c01a280 state=pending>: "人工智能",
            # }
            future_to_ind = {
                executor.submit(task_with_retry, ind): ind
                for ind in list_all_only_indicators
            }
            # concurrent.futures.as_completed（）：不按提交顺序，而是按任务实际完成的顺序进行接下的操作
            # 不加 as_completed，则是会按照提交的顺序获取结果，需要等待所有任务完成后才能开始处理结果
            # as_completed 返回的是一个可迭代对象，而非列表。for循环一个字典，只遍历键。类似as_completed([future1, future2, future3])
            for future in concurrent.futures.as_completed(future_to_ind):
                # 从future_to_ind字典中获取对应指标名称
                ind_name = future_to_ind[future]
                # 🔥 修改点：try...except 放到 allure.step 外面
                try:
                    with allure.step(f"指标【{ind_name}】搜索结果校验"):
                        try:
                            result = future.result()

                            # 1. 成功情况
                            if result["type"] == "success":
                                list_success.append(ind_name)
                                allure.attach(str(result), name=f"【{ind_name}】搜索成功",
                                              attachment_type=allure.attachment_type.TEXT)

                            # 2. 业务失败（无数据）
                            elif result["type"] == "no_reason":
                                list_fail_empty_data.append(ind_name)
                                allure.attach(str(result), name=f"【{ind_name}】搜索无结果",
                                              attachment_type=allure.attachment_type.TEXT)
                                # 这里抛出异常，会中断 step，使其变红
                                pytest.fail(f"指标【{ind_name}】请求成功但无数据", pytrace=False)

                            # 3. 接口/重试失败
                            else:
                                list_unsearchable.append(ind_name)
                                allure.attach(
                                    f"指标【{ind_name}】多次重试仍失败",
                                    name="失败原因",
                                    attachment_type=allure.attachment_type.TEXT
                                )
                                # 这里抛出异常，会中断 step，使其变红
                                pytest.fail(f"指标【{ind_name}】请求失败：{result.get('error')}", pytrace=False)

                        except Exception as e:
                            # 这是为了捕获 future.result() 自身可能抛出的线程内部未捕获的异常
                            # 如果上面的 pytest.fail 被触发，实际上抛出的是 Failed 异常，属于 BaseException 的子类（在 pytest 中），
                            # 但为了保险，通常 Exception 捕获不到 Failed (取决于 pytest 版本)，
                            # 所以这里主要是捕获代码逻辑错误
                            list_unsearchable.append(ind_name)
                            allure.attach(str(e), name="线程异常", attachment_type=allure.attachment_type.TEXT)
                            raise e  # 抛出异常让外层 allure 感知到失败

                except Failed:
                    # 🔥 关键点：在这里捕获 pytest.fail 抛出的 Failed 异常
                    # 此时 allure.step 已经结束并标记为 Failed，我们吞掉异常让循环继续
                    pass

                except Exception:
                    # 捕获其他非断言类的异常，防止整个测试中断
                    # 同样，此时 allure.step 已经因为异常穿透而变红
                    pass

        end_time = datetime.now()

        # ================= 测试结论输出 =================

        total = len(list_all_only_indicators)
        success = len(list_success)
        empty = len(list_fail_empty_data)
        fail = len(list_unsearchable)

        conclusion = f"""
            【搜索指标接口自动化测试结论】
            并发请求总耗时：{end_time - start_time}，线程数：{max_workers}
            总指标数：{total}
            成功指标数：{success}
            无数据指标数：{empty}
            不可搜索指标数：{fail}
    
            不可搜索指标清单：
            {chr(10).join(list_unsearchable) if list_unsearchable else '无'}
            """

        allure.attach(
            conclusion,
            name="📊 测试结论",
            attachment_type=allure.attachment_type.TEXT
        )

        print(conclusion)

        return {
            "success": list_success,
            "empty_data": list_fail_empty_data,
            "unsearchable": list_unsearchable
        }

    @allure.step("同步请求搜索所有指标")
    def search_all_indicator_sync(self, all_ind_info):
        """
        同步请求搜索所有指标
        :param all_ind_info: 所有指标列表
        :return:
        """
        start_time = datetime.now()
        # 用于收集并发结果的列表
        list_fail_empty_data = []  # 请求成功但数据为空的失败
        list_fail_api_error = []  # API请求失败或意外异常
        for dict_indicators in all_ind_info:
            ind_name = self.do.get_value_from_dict(dict_indicators, "name")
            result = self.search_single_indicator(ind_name)
            if result['type'] == 'success':
                print(f"✅️ 搜索指标 {ind_name} 的数据成功！")
            elif result['type'] == 'no_reason':
                list_fail_empty_data.append(ind_name)
                print(f"❌️ 搜索指标 {ind_name} 的数据成功，但明细数据为空！")
            elif result['type'] in ('request_fail', 'exception'):
                list_fail_api_error.append(ind_name)
                error_msg = result['error']
                print(f"❌️ 搜索指标 {ind_name} 的数据失败！错误信息：{error_msg}")
        end_time = datetime.now()
        print(f"同步请求搜索全部指标 {len(all_ind_info)} 条数据完毕，共耗时：{end_time - start_time}")

    @allure.step("请求当前指标的各学校数据接口")
    def request_indicator_data(self, indName:str,indCode: str, year: str, pageIndex: int = 1,
                       pageSize: int = 100, showOurCompare: bool = False):
        """
        请求当前指标的各学校数据
        :param indName:指标名称
        :param indCode: 指标code
        :param year:指标监测年份
        :param pageIndex:页面个数
        :param pageSize:每个页面放多少数据
        :param showOurCompare:是否查看本校和标杆
        :return:当前指标的响应数据
        """
        api_indicator_data = self.al.get_api('indicator_view', 'indicator_view', 'single_indicator_data')
        url = api_indicator_data["url"]
        payload  = self.do.get_copy_key_from_dict(api_indicator_data, "payload")
        payload .update(
            {
            "indCode": indCode,
            "pageIndex": pageIndex,
            "pageSize": pageSize,
            "showOurCompare": showOurCompare,
            "year": year
            }
        )
        response = self.ru.request(
            method=api_indicator_data["method"],
            url=url,
            json=payload ,
            headers=api_indicator_data.get('headers')
        )
        response_json = response.json()
        assert response_json["code"] == 200, f"请求【{indName}】数据接口异常！错误信息：{response_json['message']}"
        return response_json

    @allure.step("并发请求所有指标的各个院校数据")
    def get_all_indicator_data_concurrently(self,list_all_indicators_with_code_and_year: list[dict],max_workers: int = 5):
        """
        并发请求所有指标的各个院校数据
        :param list_all_indicators_with_code_and_year:一个[{}{}],包含指标名，指标Code和指标监测年份
        :param max_workers:线程组
        :return:字典：包含请求成功，请求失败，请求成功但是数据为空
        """
        list_fail = []
        list_success = []
        list_empty_data = []
        def _request_single_indicator(dict_indicator):
            "单个指标数据请求任务"
            ind_name, indCode, year = self.do.get_value_from_dict(dict_indicator, "name", "code", "year")
            try:
                resp = self.request_indicator_data(ind_name, indCode, year)
                univIndData = resp["data"].get("univIndData")
                # 请求成功，但数据为空
                if univIndData is None:
                    return {
                        "type": "no_reason",
                        "request": dict_indicator
                    }
                else:
                    return {
                        "type": "success",
                        "request": dict_indicator,
                    }
            except AssertionError as e:
                return {
                    "type": "request_fail",
                    "request": dict_indicator,
                    "error": str(e)
                }
            except Exception:
                return {
                    "type": "exception",
                    "request": dict_indicator,
                    "error": traceback.format_exc()
                }
        # 记录并发请求开始时间
        start_time = datetime.now()
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_indicator = {executor.submit(_request_single_indicator, dict_indicator):dict_indicator
                                       for dict_indicator in list_all_indicators_with_code_and_year}
            for future in concurrent.futures.as_completed(future_to_indicator):
                # future_to_indicator[future]即为每个循环的dict_indicator
                indName = future_to_indicator[future]["name"]
                try:
                    with allure.step(f"指标【{indName}】搜索结果校验"):
                        try:
                            result = future.result()

                            if result["type"] =="success":
                                list_success.append(indName)
                                allure.attach(str(result),name=f"【{indName}】数据请求成功",attachment_type=allure.attachment_type.TEXT)
                            elif result["type"] == "no_reason":
                                list_empty_data.append(indName)
                                allure.attach(str(result),name=f"【{indName}】数据请求成功，但无数据",attachment_type=allure.attachment_type.TEXT)
                                pytest.fail(f"指标【{indName}】数据请求成功，但无数据！",pytrace=True)
                            else:
                                list_fail.append(indName)
                                allure.attach(str(result),name=f"【{indName}】数据请求失败",attachment_type=allure.attachment_type.TEXT)
                                pytest.fail(f"指标【{indName}】数据请求失败！错误信息：{result['error']}",pytrace=True)
                        except Exception as e:
                            allure.attach(str(e), name="线程异常", attachment_type=allure.attachment_type.TEXT)
                            list_fail.append(indName)
                            raise  e
                except Failed:
                    pass
                except Exception as e:
                    pass

        end_time = datetime.now()
        # ================= 测试结论输出 =================

        total = len(list_all_indicators_with_code_and_year)
        success = len(list_success)
        empty = len(list_empty_data)
        fail = len(list_fail)

        conclusion = f"""
        【请求指标数据接口自动化测试结论】
        并发请求总耗时：{end_time - start_time}，线程数：{max_workers}
        总指标数：{total}
        成功指标数：{success}
        无数据指标数：{empty}
        指标请求失败数：{fail}

        指标请求失败清单：
        {chr(10).join(list_fail) if list_fail else '无'}
        """

        allure.attach(conclusion,name="📊 测试结论",attachment_type=allure.attachment_type.TEXT)
        print(conclusion)
        # 返回所有可能的结果
        return {
            "success": list_success,
            "empty_data": list_empty_data,
            "fail": list_fail
        }