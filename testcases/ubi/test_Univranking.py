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

class TestUnivranking:

    test_data =["RC00005"]

    @pytest.fixture(scope="module",params=test_data)
    def ubi_session(self,choose_product_session, request):
        """
        创建最终用于 UBI 测试的、带 cookie 的 RequestUtil 实例。
        """
        school_code = request.param
        session = choose_product_session("ubi",school_code)
        yield session

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
        list_ind_data = load_page.get_indicators_info(rankingTypeId, verNo)
        yield list_ind_data, rankingTypeId, verNo

    @allure.story("动态排名校验")
    @allure.title("检查各学校当前版本的排名")
    @allure.tag("regression")
    @allure.description("检查各学校当前版本的排名")
    def test_Univranking01(self, load_page, indicators_data):
        _, rankingTypeId, verNo = indicators_data
        load_page.get_all_univ_ranking( rankingTypeId,verNo,"202508")
