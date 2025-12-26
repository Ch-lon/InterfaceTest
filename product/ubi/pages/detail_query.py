# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : detail_query.py
@Author  : Chlon
@Date    : 2025/12/26 10:24
@Desc    : 
"""
import concurrent.futures.thread
from datetime import datetime
import allure,pytest
from _pytest.outcomes import Failed
from product.ubi.pages.UbiCommon import UbiCommon

class DetailQuery(UbiCommon):

    @allure.step("数据查询标杆学校获取")
    def get_benchmark_code(self)->list[ str]:
        """
        获取标杆学校code，不包括本校
        :return: 标杆学校code组成的列表
        """
        api_benchmarkcode = self.al.get_api('detail_query', 'detail_query', 'benchmark_code')
        url = api_benchmarkcode['url']
        response = self.ru.request(
            method=api_benchmarkcode['method'],
            url=url,
            headers=api_benchmarkcode.get('headers')
        )
        response_json = response.json()
        assert response_json['code'] == api_benchmarkcode["expected"]["code"],f"指标查询页标杆学校code获取失败，响应为{response_json}"
        return response_json['data']['univCodes']

    @allure.step("数据查询接口请求")
    def detail_query_request(self,
                             benchmarkdata:list[str],
                             instcode: str,
                             searchvalue:str,
                             pageindex: int = 1,
                             pagesize:int = 30):
        """
        数据查询接口请求
        :param benchmarkdata: 标杆学校code列表
        :param instcode: 学校code
        :param searchvalue: 搜索内容
        :param pageindex: 页码
        :param pagesize: 每页数量
        :return:数据查询结果
        """
        api_search_detail = self.al.get_api('detail_query', 'detail_query', 'search_detail')
        url = api_search_detail['url']
        payload = self.do.get_copy_key_from_dict(api_search_detail, 'payload')
        payload.update(
            {
                "benchmarkdata": benchmarkdata,
                "instcode": instcode,
                "searchvalue": searchvalue,
                "pageindex": pageindex,
                "pagesize": pagesize
            }
        )
        response = self.ru.request(
            method=api_search_detail['method'],
            url=url,
            headers=api_search_detail.get('headers'),
            json=payload,
           # timeout = (10, 250)
        )
        response_json = response.json()
        assert response_json['code'] == api_search_detail["expected"]["code"],f"数据查询搜索{searchvalue}请求失败，响应为{response_json}"
        return response_json["data"]

    @allure.step("并发请求所有指标的数据查询接口")
    def request_all_indicator_detail_query_by_Concurrent(self, benchmarkdata, instcode,list_searchvalue,max_workers = 10):
        """
        并发请求所有指标的数据查询接口
        :param benchmarkdata: 标杆学校code列表
        :param instcode: 学校code
        :param list_searchvalue:所有指标列表
        :param max_workers:最大线程数
        :return:
        """
        list_success = []
        list_fail = []
        list_exception = []
        # 构造单个请求
        def single_query(ind_name):
            """
            单个指标搜索
            """
            try:
                self.detail_query_request(benchmarkdata, instcode, ind_name)
                return {"type": "success", "request": ind_name}
            except AssertionError as e:
                return {"type": "fail", "request": ind_name, "error": str(e)}
            except Exception as e:
                return {"type": "exception", "request": ind_name, "error": str(e)}
        start_time = datetime.now()
        # 线程池
        with concurrent.futures.thread.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_ind_name = {executor.submit(single_query, ind_name): ind_name for ind_name in list_searchvalue}
            # 获取结果
            for future in concurrent.futures.as_completed(future_to_ind_name):
                ind_name = future_to_ind_name[future]
                try:
                    with allure.step(f"指标【{ind_name}】数据查询结果："):
                        try:
                            result = future.result()
                            if result["type"] == "success":
                                allure.attach(str(result),name=f"【{ind_name}】查询成功", attachment_type=allure.attachment_type.TEXT)
                                list_success.append(result)
                            if result["type"] == "fail":
                                allure.attach(str(result),name=f"【{ind_name}】查询接口失败", attachment_type=allure.attachment_type.TEXT)
                                pytest.fail(f"【{ind_name}】查询接口失败",pytrace=True)
                                list_fail.append(result)
                            if result["type"] == "exception":
                                allure.attach(str(result),name=f"【{ind_name}】查询时发生其他异常", attachment_type=allure.attachment_type.TEXT)
                                list_exception.append(result)
                                pytest.fail(f"【{ind_name}】查询时发生其他异常",pytrace=True)
                        except Exception as e:
                            allure.attach(str(e),name=f"【{ind_name}】查询时发生线程异常", attachment_type=allure.attachment_type.TEXT)
                            list_exception.append(ind_name)
                            raise e
                except Failed:
                    pass
                except Exception:
                    pass
        end_time = datetime.now()
        # ================= 测试结论输出 =================
        total = len(list_searchvalue)
        success = len(list_success)
        fail = len(list_fail)
        exception = len(list_exception)
        # # chr(10)生成换行符
        conclusion = f"""
        【数据查询接口自动化测试结论】
          总耗时:{end_time - start_time},线程数量:{max_workers},
          请求总数:{total},
          成功:{success},
          失败:{fail},
          异常:{exception},
          失败指标:{chr(10).join(list_fail) if list_fail else '无'}
        """
        allure.attach(conclusion, name="【数据查询接口自动化测试结论】", attachment_type=allure.attachment_type.TEXT)
        return {
            "success": list_success,
            "fail": list_fail,
            "exception": list_exception,
        }
