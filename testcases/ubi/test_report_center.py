# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : test_report_center.py
@Author  : Chlon
@Date    : 2025/11/17 11:18
@Desc    : 报告中心
"""
import pytest,allure,time,requests
from product.ubi.pages.report_center import ReportCenter
from product.cg.pages.CGOperations import CGOperations
from product.ubi.pages.report_center_ui import ReportCenterUI
from playwright.sync_api import sync_playwright, expect
from playwright.sync_api import Browser  # <--- 这里引入类型
from urllib.parse import urlparse

@allure.feature("报告中心页")
@allure.tag("API", "ReportCenter")
class TestReportCenter:

    test_data = ["RC00005","RI02727"]

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
        yield school_code  # 这里获取ubi_session的参数

    @pytest.fixture(scope="module", autouse=True)
    def load_page_api(self, ubi_session,auth_token):
        session,school_code = ubi_session
        page_api = ReportCenter(session)
        yield page_api

    @pytest.fixture(scope="module")
    def indicators_data(self, load_page_api):
        """
        获取排名趋势指标数据
        """
        rankingTypeId, verNo = load_page_api.get_version()
        list_ind_info = load_page_api.get_indicator_data_info()
        yield list_ind_info, rankingTypeId, verNo

    @pytest.fixture(scope="module")
    def setup_page_with_login(self, browser, ubi_session, config, auth_token):
        """
        使用playwright为报告中心测试准备浏览器页面
        :param browser:
        :param ubi_session:
        :param config:
        :param auth_token:
        :return:页面对象
        """
        # 1. 准备浏览器
        context = browser.new_context()
        page = context.new_page()
        # 2. 准备数据
        session, school_code = ubi_session
        cg = CGOperations(session)  # 假设 CGOperations 初始化需要 session
        # 3. 调用优化后的方法，把 page 传进去
        cg.go_to_product_page(
            page=page,  # <--- 关键点：传入 page
            productCode="ubi",
            univCode=school_code,
            page_name="报告中心",
            token=auth_token
        )
        yield page
        context.close()

    @allure.story("生成报告：ARWU世界大学学术排名指标数据分析报告")
    @allure.title("生成报告：ARWU世界大学学术排名指标数据分析报告")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("regression", "API")
    @allure.description("生成报告：ARWU世界大学学术排名指标数据分析报告")
    def test_report_center03(self, load_page_api, univCode,setup_page_with_login):
        """
        报告中心
        """
        page = setup_page_with_login
        report_page_ui = ReportCenterUI(page)
        try:
            reportType = "ranking"
            list_reports_before = load_page_api.report_list_request(reportType)
            if list_reports_before:
                report_page_ui.button_generate_report_whit_list.click()
            else:
                report_page_ui.button_generate_report_without_list.click()
            # 填写报告名称
            report_name = f"{univCode}自动化报告"
            expect(report_page_ui.REPORT_NAME).to_be_visible()
            report_page_ui.REPORT_NAME.fill(report_name)
            # 选择报告版本
            # REPORT_VERSION = page.wait_for_selector(".ant-select.ant-select-lg.text-14.ant-select-single.ant-select-show-arrow")
            # REPORT_VERSION.click()
            # REPORT_VERSION.select_option(value="2025年08月")
            expect(report_page_ui.button).to_be_visible(timeout=10000)
            report_page_ui.button.click()
            try:
                report_page_ui.message_notice.wait_for(state="visible", timeout=10000)
                # list_reports_after = load_page_api.report_list_request(reportType)
                # print(f"初始报告个数为{len(list_reports_before)}，之后个数为{len(list_reports_after)}")
                # assert len(list_reports_after) == len(list_reports_before) + 1, f"{report_name}生成后，报告个数没有+1！初始报告个数为{len(list_reports_before)}，生成后个数为{len(list_reports_after)}"
            except Exception as e:
                # 添加失败附件到 allure 报告
                allure.attach(
                    page.screenshot(),
                    name=f"报告失败截图",
                    attachment_type=allure.attachment_type.PNG
                )
                pytest.fail(f"报告【{report_name}】生成失败: {str(e)}")
        except Exception as e:
            raise Exception(f"{univCode} 报告生成测试失败: {e}")


