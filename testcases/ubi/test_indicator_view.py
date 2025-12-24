# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : test_indicator_view.py
@Author  : Chlon
@Date    : 2025/12/12 10:13
@Desc    : 指标查看测试用例
"""
import pytest
import allure,random,time
from common.logger import get_logger
from product.ubi.pages.indicator_view import IndicatorView

class TestIndicatorView:

    logging = get_logger(__name__)
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
        self.session = ubi_session
        page = IndicatorView(self.session)
        yield page

    @pytest.fixture(scope="module")
    def indicators_data(self, load_page):
        """
        获取排名趋势指标数据
        """
        #rankingTypeId, verNo = load_page.get_version()
        list_ind_info = load_page.get_indicator_view_info()
        yield list_ind_info

    @allure.story("搜索指标接口校验")
    @allure.title("检查指标是否可以在指标查看被搜索")
    @allure.tag("regression")
    @allure.description("检查当前学校搜索指标接口")
    def test_IndicatorView01(self, load_page, indicators_data):
        list_ind_info= indicators_data
        # 方法一：并发请求搜索所有指标
        list_all_indicators_name = load_page.extract_all_indicator_name(list_ind_info)
        results = load_page.search_all_indicator_by_concurrent(list_all_indicators_name)
        # 2. 分别提取 "请求失败" 和 "数据为空" 的指标列表
        failed_indicators = results.get("unsearchable", [])
        empty_indicators = results.get("empty_data", [])
        # 只要任意一个列表不为空，就视为测试不通过
        if failed_indicators or empty_indicators:
            error_details = []
            if failed_indicators:
                error_details.append(f"❌ 搜索失败的指标 ({len(failed_indicators)}个): {failed_indicators}")
            if empty_indicators:
                error_details.append(f"⚠️ 搜索无结果的指标 ({len(empty_indicators)}个): {empty_indicators}")
            # 将列表转换为字符串，用换行符分隔
            final_error_msg = "\n".join(error_details)

            # 附加到 Allure 报告
            allure.attach(final_error_msg, name="异常指标汇总", attachment_type=allure.attachment_type.TEXT)

            # 4. 触发测试失败，打印汇总信息
            pytest.fail(f"指标查看页面搜索请求失败！异常指标：\n{final_error_msg}")

        # 方法二：同步请求搜索所有指标
        #load_page.search_all_indicator_sync(list_ind_info)

    @allure.story("指标查看指标数据接口请求校验")
    @allure.title("检查指标数据接口请求")
    @allure.tag("regression")
    @allure.description("检查当前学校指标数据接口请求")
    def test_IndicatorView02(self, load_page, indicators_data):
        list_ind_info= indicators_data
        list_all_indicators_code_and_year = load_page.extract_indCode_and_year(list_ind_info)
        # 1. 调用方法并接收返回的汇总结果
        result_summary = load_page.get_all_indicator_data_concurrently(list_all_indicators_code_and_year)

        # 2. 分别提取 "请求失败" 和 "数据为空" 的指标列表
        failed_indicators = result_summary.get("fail", [])
        empty_indicators = result_summary.get("empty_data", [])

        # 3. 组装错误信息
        # 只要任意一个列表不为空，就视为测试不通过
        if failed_indicators or empty_indicators:
            error_details = []

            if failed_indicators:
                error_details.append(f"❌ 请求失败的指标 ({len(failed_indicators)}个): {failed_indicators}")

            if empty_indicators:
                error_details.append(f"⚠️ 请求成功但是数据为空的指标 ({len(empty_indicators)}个): {empty_indicators}")

            # 将列表转换为字符串，用换行符分隔
            final_error_msg = "\n".join(error_details)

            # 附加到 Allure 报告
            allure.attach(final_error_msg, name="异常指标汇总", attachment_type=allure.attachment_type.TEXT)

            # 4. 触发测试失败，打印汇总信息
            pytest.fail(f"指标查看数据请求失败！发现异常指标：\n{final_error_msg}")

    @allure.story("收藏和取消收藏指标校验")
    @allure.title("收藏或取消收藏指标，并查看收藏列表中是否存在")
    @allure.tag("regression")
    @allure.description("若收藏列表中已存在该指标，则请求取消收藏接口；若不存在，则请求收藏接口")
    def test_IndicatorView03(self, load_page, indicators_data):
        # 获取包含指标名称和指标代码的字典
        dict_all_indicators_with_name_and_code = load_page.extract_indicator_with_name_and_code(indicators_data)
        # 随机选择一个指标
        random_indName,random_indCode =load_page.do.get_random_key_and_value_from_dict(dict_all_indicators_with_name_and_code) #"获权威奖项教师","indt"
        print("随机选中指标：", random_indName)
        # 获取未收藏指标前的收藏列表
        list_indName_before_collect = load_page.getCollectInds_request ()
        print("已收藏列表：", list_indName_before_collect)
        # 如果随机选的指标在已收藏列表中，则进行取消收藏操作
        if random_indName in list_indName_before_collect:
            print("已收藏列表中已存在该指标，将取消收藏该指标")
            # 取消收藏
            load_page.removeCollectInds_request (random_indCode)
            # 获取取消收藏后的列表
            list_indName_after_removeCollectInds = load_page.getCollectInds_request()
            print("取消收藏后的已收藏列表：", list_indName_after_removeCollectInds)
            assert random_indName not in list_indName_after_removeCollectInds, f"取消收藏指标{random_indName}后，收藏列表{list_indName_after_removeCollectInds}中仍存在该指标！"
        else:
            print("已收藏列表中未存在该指标，将收藏该指标")
            # 否则进行收藏操作
            load_page.addCollectInds_request (random_indCode)
            # 获取进行添加收藏后的收藏列表
            list_indName_after_addCollectInds = load_page.getCollectInds_request ()
            print("添加收藏后的已收藏列表：", list_indName_after_addCollectInds)
            assert random_indName in list_indName_after_addCollectInds, f"添加收藏指标{random_indName}后，收藏列表{list_indName_after_addCollectInds}中不存在该指标！"








