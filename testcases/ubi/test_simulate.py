# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : test_simulate.py
@Author  : Chlon
@Date    : 2025/11/10 17:44
@Desc    : 排名推演测试用例
"""
#from multiprocessing.connection import default_family
from product.ubi.pages.simulate import Simulate
import allure
import pytest

@allure.feature("排名推演页")
@allure.tag("API", "Simulate")
class TestSimulate:

    test_data =["RC00005"]
    # 参数化测试，为不同的 school_code 运行测试
    @pytest.fixture(scope="module", params=test_data)
    def ubi_session(self, choose_product_session, request):
        """
        创建最终用于 UBI 接口测试的、带 cookie 的 RequestUtil 实例。
        """
        school_code = request.param
        # self.cg = CGOperations(cg_session,config)
        session = choose_product_session("ubi", school_code)
        yield session

    @pytest.fixture(scope="module", params=test_data)
    def univCode(self, request):
        """从 ubi_session_data 中提取并返回 school_code。"""
        school_code = request.param
        return school_code

    @pytest.fixture(scope="module", autouse=True)
    def load_page(self, ubi_session):
        self.session = ubi_session
        page = Simulate(self.session)
        yield page

    @pytest.fixture(scope="module")
    def indicators_data(self, load_page):
        """
        获取排名趋势指标数据
        """
        rankingTypeId, verNo = load_page.get_version()
        list_ind_info = load_page.simulate_indicators(rankingTypeId, verNo)
        yield list_ind_info, rankingTypeId, verNo

    @allure.story("没改变传入参数直接点击模拟")
    @allure.title("检查没有改变传入参数模拟后，得分和排名是否改变")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("regression", "API")
    @allure.description("检查改变传入参数模拟后，得分和排名是否改变")
    def test_simulate01(self, load_page, indicators_data):
        list_ind_info, rankingTypeId, verNo = indicators_data
        # 获取所有排名指标
        list_rank_inds = load_page.get_rank_indicators(list_ind_info)

        # 用于模拟的参数
        dict_param = load_page.get_simulate_ind_indId_val(list_ind_info)
        # 模拟请求
        dict_result = load_page.simulate_request(rankingTypeId, verNo, dict_param)
        # 对请求结果进行提取
        dict_simulate_result = load_page.switch_simulate_result(dict_result, list_rank_inds)
        # 获取进入排名推演页面的默认值
        dict_init_data = load_page.simulate_default_data( list_ind_info,rankingTypeId, verNo)
        print(f"初始结果为：{dict_init_data}，\n模拟结果为：{dict_simulate_result}")
        assert dict_init_data == dict_simulate_result, f"请求模拟后得分或排名发生改变！初始结果为：{dict_init_data}，没有改变数据，模拟结果为：{dict_simulate_result}"

    @allure.story("循环以大学联盟中10个数据进行模拟")
    @allure.title("循环以大学联盟中10个数据进行模拟，学校的得分和排名是否改变")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("regression", "API")
    @allure.description("检查循环模拟大学联盟中10个数据，学校的得分和排名是否改变")
    def test_simulate02(self, load_page, indicators_data):
        list_ind_info, rankingTypeId, verNo = indicators_data
        # 获取排名指标Id
        list_rank_inds = load_page.get_rank_indicators(list_ind_info)
        # 获取大学联盟代码
        list_univ_alliance_code= load_page.get_univ_alliance_code_request("all",rankingTypeId)
        # 获取进入排名推演页面的默认值
        dict_init_data = load_page.simulate_default_data(list_ind_info, rankingTypeId, verNo)
        print(f"初始结果为：{dict_init_data}")
        # 收集失败的断言
        failed_cases = []

        for code in list_univ_alliance_code:
            try:
                # 以大学联盟数据为参数，进行模拟请求
                dict_result = load_page.get_univ_alliance_default_param_request(rankingTypeId, verNo, code)
                dict_param = load_page.switch_simulate_ind_indId_val(list_ind_info, dict_result)
                dict_simulate_result = load_page.simulate_request(rankingTypeId, verNo, dict_param)
                # 提取模拟结果
                dict_simulate_result = load_page.switch_simulate_result(dict_simulate_result, list_rank_inds)

                # 断言检查
                assert dict_init_data != dict_simulate_result, (
                    f"以 {code} 数据进行请求模拟后，得分或排名未发生改变！\n"
                    f"初始结果: {dict_init_data}\n"
                    f"模拟结果: {dict_simulate_result}"
                )
                print(f"{code} 模拟结果为：{dict_simulate_result}")

            except AssertionError as e:
                failed_cases.append(f"大学联盟代码 {code} 测试失败: {str(e)}")
                print(f"{code} 测试失败: {str(e)}")
                continue  # 继续执行下一个测试

        # 如果有失败的测试用例，则报告所有失败情况
        if failed_cases:
            pytest.fail(f"以下测试用例失败:\n" + "\n".join(failed_cases))

    @allure.story("数据导出")
    @allure.title("数据导出")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("regression", "API")
    @allure.description("数据导出")
    def test_simulate03(self, load_page, indicators_data, univCode):
        list_ind_info, rankingTypeId, verNo = indicators_data
        resp = load_page.request_data_export(list_ind_info,rankingTypeId, verNo)
        file_name = f"{univCode}-ARWU推演-{verNo}.xlsx"
        load_page.check_export_response(resp, "xlsx", file_name)

    @allure.story("指标明细请求")
    @allure.title("检查指标明细是否可以请求成功，以及是否有数据")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("regression", "API")
    @allure.description("检查指标明细是否可以请求成功，以及是否有数据")
    def test_simulate04(self, load_page, indicators_data):
        list_ind_info, rankingTypeId, verNo = indicators_data
        load_page.detail_click(list_ind_info, verNo)