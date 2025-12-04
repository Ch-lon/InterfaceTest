# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : report_center.py
@Author  : Chlon
@Date    : 2025/11/17 11:16
@Desc    : 报告中心
"""

from product.ubi.pages.UbiCommon import UbiCommon

class ReportCenter(UbiCommon):

    def report_list_request(self) -> list:
        """
        获取报告列表
        """
        api_report_list = self.al.get_api('report_center', 'report_center', 'report_list')
        url = api_report_list['url']

        response = self.ru.request(
            method=api_report_list['method'],
            url=url,
            headers=api_report_list.get('headers'),
            json = api_report_list.get("data")
        )
        response_json = response.json()
        assert response_json["code"] == api_report_list["expected"]["code"], f"报告列表请求失败，请求响应:{response_json}"
        return response_json["data"]

    def report_request(self, report_id) :
        """
        获取报告详情
        """
        api_report_path = self.al.get_api('report_center', 'report_center', 'report_path')
        url = self.do.format_url(api_report_path['url'],id=report_id)

        response = self.ru.request(
            method=api_report_path['method'],
            url=url,
            headers=api_report_path.get('headers'),
        )
        response_json = response.json()
        assert response_json["code"] == api_report_path["expected"]["code"], f"报告详情请求失败，请求响应:{response_json}"
        return response_json["data"]