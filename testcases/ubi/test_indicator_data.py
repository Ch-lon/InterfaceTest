# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : test_indicator_data.py
@Author  : Chlon
@Date    : 2025/12/9 13:19
@Desc    : 全部指标测试用例
"""

import pytest
import allure
from common.logger import get_logger
from product.ubi.pages.indicator_data import IndicatorData

class TestIndicatorData:

    test_data = ["RI02727"]

    @pytest.fixture(scope="module", params=test_data)
    def ubi_session(self, choose_product_session, request):
        """
        创建最终用于 UBI 接口测试的、带 cookie 的 RequestUtil 实例。
        """
        school_code = request.param
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
        page = IndicatorData(self.session)
        yield page

    @pytest.fixture(scope="module")
    def indicators_data(self, load_page):
        """
        获取排名趋势指标数据
        """
        #rankingTypeId, verNo = load_page.get_version()
        dict_indicators_details = load_page.get_all_school_indicator_data()
        list_ind_info = load_page.get_indicator_data_info()
        yield list_ind_info, dict_indicators_details

    @allure.story("对所有指标明细进行请求")
    @allure.title("请求全部指标页面所有明细")
    @allure.tag("regression")
    @allure.description("请求全部指标页面所有明细，查看是否请求成功")
    def test_IndicatorData01(self, load_page, indicators_data):
        list_ind_info, dict_indicators_details = indicators_data
        # 同步请求全部指标明细
        #load_page.request_all_indicator_data_by_Synchronization(list_ind_info, dict_indicators_details)
        # 并发请求全部指标明细
        load_page.request_all_indicator_data_by_Concurrent(list_ind_info, dict_indicators_details)

    @allure.story("导出全部指标页面所有学校的所有指标明细数据")
    @allure.title("导出全部指标页面所有学校的所有指标明细数据")
    @allure.tag("regression")
    @allure.description("导出全部指标页面所有学校的所有指标明细数据，查看是否请求成功")
    def test_IndicatorData02(self, load_page, univCode):
        response = load_page.export_all_indicator_data(univCode)
        filename = f"{univCode}_全部指标.zip"
        load_page.check_export_response(response, "zip", filename)


