# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : test_report_center.py
@Author  : Chlon
@Date    : 2025/11/17 11:18
@Desc    : 报告中心
"""
import pytest,allure
from product.ubi.pages.report_center import ReportCenter

class TestReportCenter:
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
        yield session, school_code

    @pytest.fixture(scope="module")
    def univCode(self, ubi_session):
        """从 ubi_session 中提取并返回 school_code。"""
        # 直接从ubi_session的请求参数中获取
        # 注意：由于ubi_session可能被跳过，这个fixture只有在ubi_session成功创建时才会被调用
        _, school_code = ubi_session
        return school_code  # 这里获取ubi_session的参数

    @pytest.fixture(scope="module", autouse=True)
    def load_page(self, ubi_session):
        session, _ = ubi_session
        page = ReportCenter(session)
        yield page

    @pytest.fixture(scope="module")
    def indicators_data(self, load_page):
        """
        获取排名趋势指标数据
        """
        # rankingTypeId, verNo = load_page.get_version()
        list_ind_info = load_page.get_indicator_data_info()
        yield list_ind_info

    def test_report_center01(self,load_page):
        """
        报告中心
        """
        x = load_page.upload_report_images ()
        print(x)