# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : report_center_ui.py
@Author  : Chlon
@Date    : 2025/12/31 13:49
@Desc    : 
"""
from playwright.sync_api import Page, Locator
class ReportCenterUI:
    def __init__(self, page: Page):
        self.page = page
        self.button_generate_report_whit_list=page.locator(".create-report.px-12.py-10.cursor-pointer")
        self.button_generate_report_without_list=page.locator(".ant-btn.ant-btn-primary.immediately_report")
        self.REPORT_NAME = page.locator(".ant-input.ant-input-lg")
        self.button=page.locator(".ant-btn.ant-btn-primary")
        self.message_notice = page.locator(".ant-message-notice")