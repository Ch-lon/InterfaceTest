# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : test_Univranking.py
@Author  : Chlon
@Date    : 2025/10/17 13:17
@Desc    : 动态排名测试基类
"""
import pytest
import allure
from product.ubi.pages.Univranking import Univranking

@allure.feature("动态排名页")
@allure.tag("API", "Univranking")
class TestUnivranking:

    test_data =["RI02727"]

    @pytest.fixture(scope="module",params=test_data)
    def ubi_session(self,choose_product_session, request):
        """
        创建最终用于 UBI 测试的、带 cookie 的 RequestUtil 实例。
        """
        school_code = request.param
        session = choose_product_session("ubi",school_code)
        yield session

    @pytest.fixture(scope="module",params=test_data)
    def univCode(self, request):
        """从 ubi_session_data 中提取并返回 school_code。"""
        school_code = request.param
        return school_code

    @pytest.fixture(scope="module")
    def load_page(self,ubi_session):
        session= ubi_session
        page = Univranking(session)
        yield page

    @pytest.fixture(scope="module")
    def indicators_data(self, load_page):
        """
        获取总定位数据
        """
        rankingTypeId, verNo = load_page.get_version()
        #list_ind_data = load_page.get_indicators_info(rankingTypeId, verNo)
        yield rankingTypeId, verNo

    @allure.story("动态排名校验")
    @allure.title("检查各学校当前版本的排名")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("regression", "API")
    @allure.description("检查各学校当前版本的排名")
    def test_Univranking01(self, load_page, indicators_data):
        rankingTypeId, verNo = indicators_data
        load_page.get_all_univ_ranking( rankingTypeId,verNo,"202508")

    @allure.story("动态排名数据导出校验")
    @allure.title("导出各学校当前版本的排名")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("regression", "API")
    @allure.description("导出各学校当前版本的排名")
    def test_Univranking02(self, load_page, indicators_data, univCode):
        rankingTypeId, verNo = indicators_data
        res = load_page.export_univ_ranking(rankingTypeId, verNo, "202508")
        file_name = f"{univCode}-动态排名-{verNo}.xlsx"
        load_page.check_export_response(res, "xlsx", file_name)