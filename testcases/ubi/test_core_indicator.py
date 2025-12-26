# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : test_core_indicator.py
@Author  : Chlon
@Date    : 2025/11/18 16:50
@Desc    : 核心指标测试用例
"""
import allure
import pytest
from product.ubi.pages.core_indicator import CoreIndicator


class TestCoreIndicator:
    test_data = ["RI02727"]

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
        #self.session = ubi_session
        page = CoreIndicator(ubi_session)
        yield page

    @pytest.fixture(scope="module")
    def indicators_data(self, load_page):
        """
        获取排名趋势指标数据
        """
        rankingTypeId, verNo = load_page.get_version()
        list_ind_info = load_page.get_core_indicator_info(rankingTypeId, verNo)
        yield list_ind_info, rankingTypeId, verNo

    @allure.step("核心指标数据导出")
    @allure.title("核心指标数据导出功能及文件是否正常")
    @allure.tag("regression")
    @allure.description("核心指标数据导出功能及文件是否正常")
    def test_core_indicator01(self, indicators_data, load_page, univCode):
        """
        核心指标数据导出
        """
        _, rankingTypeId, verNo = indicators_data
        response = load_page.export_data_core_indicator_request(rankingTypeId, verNo)
        filename = f"{univCode}_核心指标_{verNo}.xlsx"
        load_page.check_export_response(response, "xlsx", filename)

    @allure.step("指标明细请求")
    @allure.title("检查指标明细是否可以请求成功，以及是否有数据")
    @allure.tag("regression")
    @allure.description("检查指标明细是否可以请求成功，以及是否有数据")
    def test_core_indicator02(self, indicators_data, load_page):
        """
        指标明细请求
        """
        list_ind_info, rankingTypeId, verNo = indicators_data
        load_page.detail_click(list_ind_info, verNo)

    @allure.step("核心指标数据及排名形式验证")
    @allure.title("核心指标数据及排名形式验证")
    @allure.tag("regression")
    @allure.description("1、该指标权重为0时：若数据为0，得分和百分比得分为'-'，排名为N+;数据不为0，得分有数值，但百分比得分均为0.0%，排名为N"
                        "2、指标权重不为0时：数据为0，得分为0，百分比得分为0.0%，排名为N+;数据不为0，得分和百分比得分均有数值，排名为N")
    def test_core_indicator03(self, indicators_data, load_page):
        """
        核心指标数据及排名形式验证
        """
        list_ind_info, _, _ = indicators_data
        for ind_info in list_ind_info:
            name, weight, indData = load_page.do.get_value_from_dict(ind_info, "name", "weight", "indData")
            value, score, percentScore, rankTyp = load_page.do.get_value_from_dict(indData, "value", "score",
                                                                                   "pencentScore", "rankTyp")
            print(
                f"指标 {name} 权重为 {weight}，数据为 {value}，得分为 {score}，百分比得分为 {percentScore}，排名为 {rankTyp}")
            # 缓存字符串操作结果
            is_plus_ranking = rankTyp.endswith("+")
            if weight == 0:
                if value == 0:
                    assert is_plus_ranking, (f"指标 {name} 展示形式有误,请检查， "
                                             f"权重为 {weight}，数据为 {value}时，得分为 {score}，百分比得分为 {percentScore}，排名为 {rankTyp}")
                else:
                    assert score != 0 and percentScore == '0.0%' and not is_plus_ranking, (
                        f"指标 {name} 展示形式有误,请检查， "
                        f"权重为 {weight}，数据为 {value}，得分为 {score}，百分比得分为 {percentScore}，排名为 {rankTyp}")
            else:
                if value == 0:
                    assert score == 0 and percentScore == '0.0%' and is_plus_ranking, (
                        f"指标 {name} 展示形式有误,请检查， "
                        f"权重为 {weight}，数据为 {value}，得分为 {score}，百分比得分为 {percentScore}，排名为 {rankTyp}")
                else:
                    assert score != 0 and percentScore.endswith("%") and not is_plus_ranking, (
                        f"指标 {name} 展示形式有误,请检查， "
                        f"权重为 {weight}，数据为 {value}，得分为 {score}，百分比得分为 {percentScore}，排名为 {rankTyp}")
