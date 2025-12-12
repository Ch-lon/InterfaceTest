# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : ranking_monitor.py
@Author  : Chlon
@Date    : 2025/12/11 11:18
@Desc    : 排名监测页面类
"""

import allure
from product.ubi.pages.UbiCommon import UbiCommon

class RankingMonitor(UbiCommon):
    """
    排名监测页面类
    """

    @allure.step("排名监测数据导出")
    def ranking_monitor_data_export(self):
        """
        排名监测数据导出
        """
        api_ranking_monitor_data_export = self.al.get_api('ranking_monitor', 'ranking_monitor', 'data_export')
        url = api_ranking_monitor_data_export['url']
        response = self.ru.reuest(
            method=api_ranking_monitor_data_export['method'],
            url=url,
            headers=api_ranking_monitor_data_export.get('headers')
        )
        assert response.status_code == api_ranking_monitor_data_export["expected"]["code"], f"排名监测页面数据导出请求失败！请求响应:{response.text}"
        return response

    @allure.step("各类排名数据")
    def get_ranking_data(self):
        """
        各类排名数据
        """
        api_ranking_data = self.al.get_api('ranking_monitor', 'ranking_monitor', 'ranking_data')
        url = api_ranking_data['url']
        response = self.ru.request(
            method=api_ranking_data['method'],
            url=url,
            headers=api_ranking_data.get('headers')
        )
        response_json = response.json()
        assert response_json["code"] == api_ranking_data["expected"]["code"], f"各类排名数据请求失败！请求响应:{response_json}"
        return response_json["data"]["rankings"]