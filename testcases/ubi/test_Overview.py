# InterfaceTest/testcases/test_Overview.py
import pytest
from product.ubi.pages.Overview import Overview
import allure
import os
from openpyxl import load_workbook
from product.cg.pages.CGOperations import CGOperations

@allure.feature("总体定位页")
@allure.tag("API","Overview")
class TestOverview:

    test_data = ["RI02727"]

    # 参数化测试，为不同的 school_code 运行测试
    @pytest.fixture(scope="module",params=test_data)
    def ubi_session(self,choose_product_session,request):
        """
        创建最终用于 UBI 接口测试的、带 cookie 的 RequestUtil 实例。
        """
        school_code = request.param
        #self.cg = CGOperations(cg_session,config)
        session = choose_product_session("ubi",school_code)
        yield session

    @pytest.fixture(scope="module",params=test_data)
    def univCode(self, request):
        """从 ubi_session_data 中提取并返回 school_code。"""
        school_code = request.param
        return school_code

    @pytest.fixture(scope="module", autouse=True)
    def load_page(self,ubi_session):
        self.session= ubi_session
        page = Overview(self.session)
        yield page

    @pytest.fixture(scope="module")
    def indicators_data(self,load_page):
        """
        获取总定位数据
        """
        rankingTypeId, verNo = load_page.get_version()
        list_ind_data = load_page.get_indicators_info(rankingTypeId, verNo)
        yield list_ind_data,rankingTypeId,verNo

    @allure.story("数据导出校验")
    @allure.title("检查数据导出的响应")
    @allure.tag("regression")
    @allure.description("检查数据导出的响应是否符合预期")
    def test_Overview01(self, load_page,indicators_data,univCode):
        # 获取版本及排名类型信息
        _,rankingTypeId, verNo = indicators_data
        # 获取该版本下的该校数据
        overview_data = load_page.get_overview_data(verNo, rankingTypeId)
        # 提取同排名区间
        range_start, range_end = load_page.get_ranking_range(overview_data)
        # 数据导出请求
        response = load_page.data_export(verNo, rankingTypeId, range_start, range_end)
        # 设置导出文件命名
        filename = f"{univCode}_总体定位_{verNo}.xlsx"
        load_page.check_export_response(response,"xlsx",filename)

    @allure.story("总体定位指标排名校验")
    @allure.title("检查指标排名数值")
    @allure.tag("regression")
    @allure.description("指标排名不会为0或0+")
    def test_Overview02(self, load_page,indicators_data):
        list_ind_data,rankingTypeId, verNo = indicators_data
        #list_ind_data = load_page.get_indicators_info(rankingTypeId,verNo)
        # 断言指标排名为不能为0
        for dict_indicators in list_ind_data:
            #ind_data是一个字典
            ind_name,ind_data = load_page.do.get_value_from_dict(dict_indicators, "name","indData")
            ind_rank = load_page.do.get_value_from_dict(ind_data, "rankTyp")
            assert ind_rank not in ["0", "0+"], f"指标 {ind_name} 的指标排名为 {ind_rank},与逻辑不符！"

    @allure.story("总体定位明细点击校验")
    @allure.title("点击指标明细")
    @allure.tag("regression")
    @allure.description("查看指标明细是否有数据")
    def test_Overview03(self, load_page,indicators_data):
        list_ind_data,rankingTypeId, verNo = indicators_data
        list_fail_indicators = []
        for dict_indicators in list_ind_data:
            # 列表直接解包到变量
            ind_name,editable,detailDefId,ind_data = load_page.do.get_value_from_dict(dict_indicators, "name","editable","detailDefId","indData")
            # 指标：明细类和数值类
            indValId = load_page.do.get_value_from_dict(ind_data, "indValId")
            if editable != "val" and indValId != 0 and detailDefId != 0:
                print(f"指标 {ind_name} 的明细类指标ID为：{indValId}")
                response = load_page.detail_click(indValId, verNo,detailDefId)
                list_ind_detail = response["details"]
                if len(list_ind_detail) == 0:
                    list_fail_indicators.append(ind_name)
        assert not list_fail_indicators, f"共有 {len(list_fail_indicators)} 个指标明细点击后为空：{list_fail_indicators}"