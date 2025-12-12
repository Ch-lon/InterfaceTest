# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : indicator_data.py
@Author  : Chlon
@Date    : 2025/12/9 13:18
@Desc    : 全部指标页面类
"""
from datetime import datetime

from product.ubi.pages.UbiCommon import UbiCommon
import allure
from typing import Dict,List
import concurrent.futures
import traceback

class IndicatorData(UbiCommon):
    """
    指标数据页面类
    """

    @allure.step("获取全部指标页面的指标")
    def get_indicator_data_info(self ) -> list:
        """
        获取排名趋势页当前版本的指标体系
        :return:类似[{},{},{}]
        """
        api_indicator_data = self.al.get_api('indicator_data', 'indicator_data', 'indicators_info')
        url = api_indicator_data['url']
        response = self.ru.request(
            method=api_indicator_data['method'],
            url=url,
            headers=api_indicator_data.get('headers')
        )
        response_json = response.json()
        assert response_json["code"] == api_indicator_data["expected"]["code"], f"全部指标页指标体系请求失败！请求响应:{response_json}"
        # 指标信息是个列表
        indicators = response_json["data"]
        all_ind_info: list = self.extract_partial_level_3_data(indicators)
        return all_ind_info

    @allure.step("全部指标页面所有学校的指标数据")
    def get_all_school_indicator_data(self) -> dict:
        """
        获取全部指标页面所有学校的指标数据
        :return:
        """
        api_indicator_data = self.al.get_api('indicator_data', 'indicator_data', 'ind_collection')
        url = api_indicator_data['url']
        response = self.ru.request(
            method=api_indicator_data['method'],
            url=url,
            headers=api_indicator_data.get('headers')
        )
        response_json = response.json()
        assert response_json["code"] == api_indicator_data["expected"]["code"], f"全部指标页面所有学校的指标数据请求失败！请求响应:{response_json}"
        dict_indicators_details = response_json["data"]["detail"]
        return dict_indicators_details


    @allure.step("通过指标Code获取学校代码和指标的indValId，并组成包含所有请求所需数据的字典")
    def generate_all_requests(self,list_ind_info: list,dict_indicators_details, ) -> List[Dict]:
        """
        根据指标代码获取学校代码和对应的 indValId
        :param dict_indicators_details:包含指标Code和indValId的多个字典
        :param list_ind_info: 指标代码，如 'indt', 'indscience_all', 'pcp'
        :return: 学校信息列表，包含学校代码和 indValId
        """
        all_requests = []
        for indicator in list_ind_info:
            name,code,detailDefId = self.do.get_value_from_dict(indicator, "name", "code", "detailDefId")
            # 从 details 中获取对应指标的数据
            dict_indicator_data = dict_indicators_details.get(code)
            if not dict_indicator_data:
                print(f"未能从details中找到指标代码 {code} 的数据")
                return all_requests

            # 遍历指标下的所有学校/分组
            for school_code, data in dict_indicator_data.items():
                # 过滤出以 RC 或 RI 开头的学校代码
                if school_code.startswith(('RC', 'RI')):
                    indValId = data.get('indValId')

                    # 只收集有效的 indValId（非0且非None）
                    if indValId and indValId != 0 and detailDefId != 0:
                        school_info = {
                            'ind_name': name,
                            'school_code': school_code,
                            'indValId': indValId,
                            'detailDefId': detailDefId
                        }
                        all_requests.append(school_info)
        print(f"共获取到 {len(all_requests)} 个可点击的指标数据：{all_requests}")
        return all_requests

    @allure.step("同步请求所有指标数据接口")
    def request_all_indicator_data_by_Synchronization(self, list_ind_info: list, dict_indicators_details) :
        """
        请求所有指标数据接口
        :param list_ind_info: 列表，包含指标信息
        :param dict_indicators_details: 包含指标代码和indValId的多个字典
        :return: 所有指标数据列表
        """
        start_time = datetime.now()
        list_fail = []
        list_fail_indicators = []
        all_requests = self.generate_all_requests(list_ind_info, dict_indicators_details)
        for request in all_requests:
            ind_name,school_code,indValId,detailDefId = self.do.get_value_from_dict(request, "ind_name", "school_code", "indValId", "detailDefId")
            try:
                response = self.detail_request(indValId,detailDefId,ind_name,verNo="latest")
                # print(f"✅️ 请求学校 {school_code} 指标 {ind_name} 的数据成功！")
                list_ind_detail = response["data"]["details"]
                # 增加明细弹窗可以打开，但是获取的明细数据为空的情况
                if list_ind_detail is None or len(list_ind_detail) == 0:
                    list_fail_indicators.append(request)
            except AssertionError as e:
                print(f"❌️ 请求学校 {school_code} 指标 {ind_name} 的数据失败！错误信息：{e}")
                list_fail.append(request)
                continue
        end_time = datetime.now()
        print(f"同步请求全部指标数据耗时：{end_time - start_time}")
        list_fail_all = []
        if list_fail_indicators:
            list_fail_all.append(
                f"全部指标页面共有{len(list_fail_indicators)} 个指标数据请求成功，但是获取的明细数据为空！失败的指标数据为：{list_fail_indicators}"
            )
        if list_fail:
            list_fail_all.append(
                f"全部指标页面共有{len(list_fail)} 个指标数据请求失败！失败的指标数据为：{list_fail}"
            )
        if list_fail_all:
            raise AssertionError("\n".join(list_fail_all))

    @allure.step("请求单个指标数据接口")
    def _fetch_indicator_detail(self, request_data: Dict):
        """[私有方法] 用于并发执行单个指标明细请求的 worker 函数。"""
        ind_name, school_code, indValId, detailDefId = self.do.get_value_from_dict(
            request_data, "ind_name", "school_code", "indValId", "detailDefId"
        )
        try:
            # 调用原本同步的请求方法
            response = self.detail_request(indValId, detailDefId, ind_name, verNo = "latest")
            list_ind_detail = response["data"]["details"]

            # 检查 API 返回码和数据内容 (模拟原有的成功后检查逻辑)
            if response.get("code") != 200:
                return {'type': 'api_fail', 'request': request_data, 'error': f"API返回码非200: {response.get('code')}"}

            if list_ind_detail is None or len(list_ind_detail) == 0:
                # 成功请求但数据为空，记录为一种失败类型
                return {'type': 'empty_data_fail', 'request': request_data}
            else:
                # 请求成功且有数据
                return {'type': 'success', 'request': request_data}

        except AssertionError as e:
            # 捕获预期的断言失败（如 detail_request 内部的 status_code/json/code 检查失败）
            return {'type': 'api_fail', 'request': request_data, 'error': str(e)}
        except Exception:
            # 捕获其他非预期的异常（如网络连接错误、JSON解析错误等）
            # 使用 traceback.format_exc() 获取完整的堆栈信息
            return {'type': 'exception', 'request': request_data, 'error': traceback.format_exc()}

    @allure.step("并发请求所有指标数据接口")
    def request_all_indicator_data_by_Concurrent(self, list_ind_info: list, dict_indicators_details):
        """
        请求所有指标数据接口
        :param list_ind_info: 列表，包含指标信息
        :param dict_indicators_details: 包含指标代码和indValId的多个字典
        :return: 无返回值，通过断言报告结果
        """
        list_all_requests = self.generate_all_requests(list_ind_info, dict_indicators_details)

        MAX_WORKERS = 5  # 最大并发线程数（可根据网络和服务器压力调整）
        start_time = datetime.now()
        # 用于收集并发结果的列表
        list_fail_empty_data = []  # 请求成功但数据为空的失败
        list_fail_api_error = []  # API请求失败或意外异常

        print(f"开始并发请求 {len(list_all_requests)} 个指标明细，最大并发数: {MAX_WORKERS}")

        # 使用 ThreadPoolExecutor 实现并发（适用于 I/O 密集型任务，如网络请求）
        # ThreadPoolExecutor：线程池管理器：自动创建 / 复用 / 销毁线程，避免手动创建线程的繁琐（如 threading.Thread），同时限制最大并发数，防止线程过多导致系统资源耗尽。
        # with 语句：上下文管理器，自动管理线程池生命周期 —— 进入with时初始化线程池，退出时自动关闭线程池（等待所有线程执行完成），无需手动调用shutdown()。

        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # 使用 executor.map 将任务分发给线程池，即 对 all_requests 中的每个元素 req，调用 _fetch_indicator_detail(req)
            # results 将按提交顺序返回结果，结果为结构化的字典
            # executor.map() 返回的是迭代器，list(results) 会阻塞主线程，直到所有任务执行完成（无论成功 / 失败）；
            # 如果某个线程执行 _fetch_indicator_detail 时抛出异常，调用 list(results) 时会直接抛出该异常（需在 _fetch_indicator_detail 内部捕获所有异常情况，避免整个并发任务中断）。
            results = list(executor.map(self._fetch_indicator_detail, list_all_requests))

        # 处理并发结果
        for result in results:
            request_data = result['request']
            ind_name, school_code = self.do.get_value_from_dict(request_data, "ind_name", "school_code")

            if result['type'] == 'success':
                pass
                #print(f"✅️ 请求学校 {school_code} 指标 {ind_name} 的数据成功且有数据！")
            elif result['type'] == 'empty_data_fail':
                print(f"❌️ 请求学校 {school_code} 指标 {ind_name} 的数据成功，但明细数据为空！")
                list_fail_empty_data.append(request_data)
            elif result['type'] in ('api_fail', 'exception'):
                error_msg = result['error']
                print(f"❌️ 请求学校 {school_code} 指标 {ind_name} 的数据失败！错误信息：{error_msg}")
                list_fail_api_error.append(request_data)
        end_time = datetime.now()
        print(f"并发请求全部指标 {len(results)} 条数据完毕，共耗时：{end_time - start_time}")

        # 最终断言：如果有任何失败，则抛出 AssertionError
        list_fail_all = []
        if list_fail_empty_data:
            list_fail_all.append(
                f"全部指标页面共有{len(list_fail_empty_data)} 个指标数据请求成功，但是获取的明细数据为空！失败的指标数据为：{list_fail_empty_data}"
            )
        if list_fail_api_error:
            list_fail_all.append(
                f"全部指标页面共有{len(list_fail_api_error)} 个指标数据请求失败！失败的指标数据为：{list_fail_api_error}"
            )
        if list_fail_all:
            raise AssertionError("\n".join(list_fail_all))

    @allure.step("获取当前学校的标杆学校")
    def get_benchmark_univ_code(self):
        api_benchmark_univ_code = self.al.get_api('indicator_data', 'indicator_data', 'benchmark_univ')
        url = api_benchmark_univ_code["url"]
        response = self.ru.request(
            method=api_benchmark_univ_code["method"],
            url=url,
            headers = api_benchmark_univ_code.get('headers')
        )
        response_json =  response.json()
        assert response.status_code == api_benchmark_univ_code["expected"]["code"], f"标杆学校请求失败！实际请求响应:{response_json}"
        return  response_json["data"]

    @allure.step("将获取的标杆学校响应提取并组成全部学校Code列表")
    def extract_benchmark_univ_and_return_all_code_list(self, univ_code):
        # 存放标杆学校code,一定会存在本校code
        list_all_univ_code = [univ_code]
        list_benchmark_univ= self.get_benchmark_univ_code()
        if list_benchmark_univ is None:
            print(f"当前学校的标杆学校为：{list_all_univ_code}")
            return list_all_univ_code
        for benchmark_univ in list_benchmark_univ:
            benchmark_univ_code = self.do.get_value_from_dict(benchmark_univ, "code")
            list_all_univ_code.append(benchmark_univ_code)
        print(f"当前学校的标杆学校为：{list_all_univ_code}")
        return list_all_univ_code


    @allure.step("全部指标页面数据导出：选择所有学校，所有指标，并导出明细数据")
    def export_all_indicator_data(self,univ_code):
        params_univCodes = self.extract_benchmark_univ_and_return_all_code_list(univ_code)
        api_IndicatorData_export = self.al.get_api('indicator_data', 'indicator_data', 'data_export')
        url = api_IndicatorData_export["url"]
        params = self.do.get_copy_key_from_dict(api_IndicatorData_export, "params")
        params.update(
            {
                # 值更新需要导出的学校的参数列表
            "univCodes" : params_univCodes
            }
        )
        response = self.ru.request(
            method=api_IndicatorData_export["method"],
            url=url,
            json=params,
            headers = api_IndicatorData_export.get('headers'),
            # 设置超时时间为 300 秒,避免后端返回504 Gateway Time-out “后端响应慢于网关超时“
            # 拆分超时：连接超时10秒，读取超时250秒（更合理）
            timeout=(10, 250)
        )
        assert response.status_code == api_IndicatorData_export["expected"]["code"], f"全部指标页面数据导出请求失败！实际请求响应:{response.text}"
        return response

