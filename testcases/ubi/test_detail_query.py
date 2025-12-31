# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : test_detail_query.py
@Author  : Chlon
@Date    : 2025/12/26 10:24
@Desc    : 
"""
import allure
import pytest
from product.ubi.pages.detail_query import DetailQuery

@allure.feature("数据查询页")
@allure.tag("API", "DetailQuery")
class TestDetailQuery:
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
        yield session,school_code

    @pytest.fixture(scope="module")
    def univCode(self, ubi_session):
        """从 ubi_session 中提取并返回 school_code。"""
        # 直接从ubi_session的请求参数中获取
        # 注意：由于ubi_session可能被跳过，这个fixture只有在ubi_session成功创建时才会被调用
        _, school_code = ubi_session
        return school_code  # 这里获取ubi_session的参数

    @pytest.fixture(scope="module", autouse=True)
    def load_page(self, ubi_session):
        session,_ = ubi_session
        page = DetailQuery(session)
        yield page

    @pytest.fixture(scope="module")
    def indicators_data(self, load_page):
        """
        获取排名趋势指标数据
        """
        #rankingTypeId, verNo = load_page.get_version()
        list_ind_info = load_page.get_indicator_data_info()
        yield list_ind_info

    @allure.story("数据查询搜索校验")
    @allure.title("数据查询搜索校验")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("regression", "API")
    @allure.description("检查是否搜索接口是否正常")
    def test_detail_query01(self, indicators_data, univCode,load_page):
        """
        数据查询搜索校验
        """
        list_fail = []
        # 获取标杆学校code
        list_benchmark_code = load_page.get_benchmark_code()
        for ind_info in indicators_data:
            ind_name,detailDefId = load_page.do.get_value_from_dict(ind_info, "name","detailDefId")
            try:
                # 跳过数值类指标
                if detailDefId == 0:
                    print(f"❌️指标 {ind_name} 是数值类")
                    continue
                search_data = load_page.detail_query_request(list_benchmark_code,univCode, ind_name)
                if not search_data["searchdata"]:
                    print(f"❌️❌️指标 {ind_name} 数据查询无数据")
                else:
                    print(f"✅️指标 {ind_name} 数据查询有数据")
            except AssertionError as e:
                list_fail.append(ind_name)
                pass
        assert not list_fail, f"共有{len(list_fail)} 个指标数据查询失败！失败的指标数据为：{list_fail}"

        # # 并发请求数据查询
        # list_error = []
        # list_ind_name = load_page.extract_indicator_name_list(indicators_data)
        # result = load_page.request_all_indicator_detail_query_by_Concurrent(list_benchmark_code,univCode,list_ind_name)
        # fail = result.get("fail", [])
        # exception = result.get("exception", [])
        # if fail:
        #     list_error.append(f"❌️共有{len(fail)} 个指标数据查询请求失败！失败的指标数据为：{fail}")
        # if exception:
        #     list_error.append(f"❌️共有{len(exception)} 个指标数据查询发生其他异常！异常的指标数据为：{exception}")
        # assert not list_error, "\n".join(list_error)




