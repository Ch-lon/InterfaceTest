# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : test_benchmark.py
@Author  : Chlon
@Date    : 2025/11/20 13:55
@Desc    : 标杆对比测试用例
"""
import allure
import pytest
from product.ubi.pages.benchmark import Benchmark

class TestBenchmark:
    test_data = ["RI02727"]

    #test_data = ["RC00005"]

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
        # self.session = ubi_session
        page = Benchmark(ubi_session)
        yield page

    @pytest.fixture(scope="module")
    def indicators_data(self, load_page):
        """
        获取标杆对比指标数据
        """
        rankingTypeId, verNo = load_page.get_version()
        list_ind_info = load_page.get_benchmark_indicators(rankingTypeId, verNo)
        yield list_ind_info, rankingTypeId, verNo

    @allure.step("指标明细请求")
    @allure.title("检查指标明细是否可以请求成功，以及是否有数据")
    @allure.tag("regression")
    @allure.description("检查指标明细是否可以请求成功，以及是否有数据")
    def test_benchmark01(self, indicators_data, load_page):
        """
        指标明细请求
        """
        list_fail_indicators = []
        list_ind_info, rankingTypeId, verNo = indicators_data
        compare_univ_indicators_info = load_page.get_compare_univ_indicators_info(rankingTypeId, verNo)
        dict_all_univ= load_page.extract_ind_val_id(compare_univ_indicators_info)
        for key_univ, dict_univ_info in dict_all_univ.items():
            univName = dict_univ_info["univName"]
            for key_ind_id, indValId in dict_univ_info["details"].items():
                for  dict_ind_info in list_ind_info:
                    if key_ind_id == dict_ind_info["id"]:
                        ind_name,editable,detailDefId = load_page.do.get_value_from_dict(dict_ind_info, "name", "editable","detailDefId")
                        if editable != "val" and indValId != 0 and indValId is not None and detailDefId != 0:
                            print(f"请求学校 {univName} 指标 {ind_name} 的明细类指标ID为：{indValId}")
                            response = load_page.detail_request(indValId, verNo, detailDefId, ind_name)
                            list_ind_detail = response["data"]["details"]
                            # 增加明细弹窗可以打开，但是获取的明细数据为空的情况
                            if response["code"] != 200 or list_ind_detail is None or len(list_ind_detail) == 0:
                                list_fail_indicators.append(ind_name({univName}))
        assert not list_fail_indicators, f"{verNo}  下标杆对比共有 {len(list_fail_indicators)} 个指标明细请求失败。失败的指标有：{list_fail_indicators}"


