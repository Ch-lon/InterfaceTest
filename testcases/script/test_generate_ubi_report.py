# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : test_generate_ubi_report.py
@Author  : Chlon
@Date    : 2025/11/17 11:24
@Desc    : 为国际360批量生成报告PDF
"""

import pytest
import allure
from product.ubi.pages.report_center import ReportCenter

class TestGenerateUbiReport:
    test_data = ["RC00005"]

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

    @pytest.fixture(scope="module", autouse=True)
    def load_page(self, ubi_session):
        #self.session = ubi_session
        page = ReportCenter(ubi_session)
        yield page

    @pytest.fixture(scope="module")
    def indicators_data(self, load_page):
        """
        获取总定位数据
        """
        rankingTypeId, verNo = load_page.get_version()
        #list_ind_data = load_page.get_indicators_info(rankingTypeId, verNo)
        yield verNo

    @allure.story("报告生成")
    @allure.title("批量生成报告")
    @allure.tag("regression")
    @allure.description("批量生成报告")
    def test_generate_ubi_report_for_each_school(self, load_page):
        """
        批量生成报告
        """
        list_report_id = load_page.report_list_request()
        for report_id in list_report_id:
            report_detail = load_page.report_request(report_id)
            print(report_detail)