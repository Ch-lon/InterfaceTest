# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : core_indicator.py
@Author  : Chlon
@Date    : 2025/11/18 16:38
@Desc    : 核心指标
"""

import allure
from product.ubi.pages.UbiCommon import UbiCommon


class CoreIndicator(UbiCommon):

    @allure.step("获取核心指标指标体系")
    def get_core_indicator_info(self,rankingTypeId, verNo):
        """
        获取核心指标指标体系
        :return:
        """
        api_core_indicator= self.al.get_api('core_indicator', 'core_indicator', 'core_indicator_info')
        url = self.do.format_url(api_core_indicator["url"], rankingTypeId=rankingTypeId, verNo=verNo,suffix="Typ")
        response = self.ru.request(
            method=api_core_indicator['method'],
            url=url,
            headers=api_core_indicator.get('headers')
        )
        response_json = response.json()
        assert response_json['code'] == api_core_indicator["expected"]["code"],f"核心指标页面指标体系获取失败，响应为{response_json}"

        # 判断每个指标的排名形式
        zero_score_issues = []
        non_zero_score_issues =[]
        indChartList = response_json["data"]["indChartList"]
        for indChart in indChartList:
            indName,univScore,univRanking = self.do.get_value_from_dict(indChart, "indName", "univScore", "univRanking")
            # 缓存字符串操作结果
            is_plus_ranking = univRanking.endswith("+")
            if univScore == 0 and not is_plus_ranking:
                zero_score_issues.append(indName)
            elif univScore != 0  and is_plus_ranking:
                non_zero_score_issues.append(indName)

        # 构建错误信息
        error_messages = []
        if zero_score_issues:
            error_messages.append(
                f"共有{len(zero_score_issues)}个指标得分为0,但排名不是N+格式: {zero_score_issues}"
            )
        if non_zero_score_issues:
            error_messages.append(
                f"共有{len(non_zero_score_issues)}个指标得分不为0,但排名是N+格式: {non_zero_score_issues}"
            )
        if error_messages:
            raise AssertionError("; ".join(error_messages))

        # 指标信息是个列表
        indicators = response_json["data"]["indInfoList"]
        all_ind_info: list = self.extract_partial_level_3_data(indicators)
        return all_ind_info

    @allure.step("核心指标数据导出请求")
    def export_data_core_indicator_request(self, rankingTypeId, verNo):
        """
        核心指标数据导出请求
        :param rankingTypeId:
        :param verNo:
        :return:
        """
        api_core_indicator = self.al.get_api('core_indicator', 'core_indicator', 'data_export')
        url = self.do.format_url(api_core_indicator["url"], rankingTypeId=rankingTypeId, verNo=verNo, suffix="Typ")
        response = self.ru.request(
            method=api_core_indicator['method'],
            url=url,
            headers=api_core_indicator.get('headers')
        )
        assert response.status_code == api_core_indicator["expected"]["code"], f"核心指标数据导出请求失败，响应为{response.text}"
        return response