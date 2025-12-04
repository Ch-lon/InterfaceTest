# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : benchmark.py
@Author  : Chlon
@Date    : 2025/11/20 13:54
@Desc    : 标杆对比页面
"""

import allure
from product.ubi.pages.UbiCommon import UbiCommon

class Benchmark(UbiCommon):

    @allure.step("获取标杆对比指标体系")
    def get_benchmark_indicators(self,rankingTypeId, verNo):
        api_benchmark_indicators = self.al.get_api('benchmark', 'benchmark', 'benchmark_indicators')
        url = self.do.format_url(api_benchmark_indicators["url"], rankingTypeId=rankingTypeId, verNo=verNo)
        response = self.ru.request(
            method=api_benchmark_indicators['method'],
            url=url,
            headers=api_benchmark_indicators.get('headers')
        )
        response_json = response.json()
        assert response_json['code'] == api_benchmark_indicators["expected"]["code"],f"标杆对比页面指标体系获取失败，响应为{response_json}"
        indicators = response_json["data"]
        all_ind_info: list = self.extract_partial_level_3_data(indicators)
        return all_ind_info

    @allure.step("获取标杆对比全部学校的指标信息")
    def get_compare_univ_indicators_info(self, rankingTypeId, verNo)->dict:
        api_compare_univ_indicators_info = self.al.get_api('benchmark', 'benchmark', 'compare_univ_indicators_info')
        url = self.do.format_url(api_compare_univ_indicators_info["url"], rankingTypeId=rankingTypeId, verNo=verNo)
        response = self.ru.request(
            method=api_compare_univ_indicators_info['method'],
            url=url,
            headers=api_compare_univ_indicators_info.get('headers')
        )
        response_json = response.json()
        assert response_json['code'] == api_compare_univ_indicators_info["expected"]["code"],f"标杆对比页面全部学校的指标信息获取失败，响应为{response_json}"
        return response_json["data"]


    @allure.step("从全部学校的指标信息中提取indValId，用于明细请求")
    def extract_ind_val_id(self, compare_univ_indicators_info: dict)->dict:
        """
        从全部学校的指标信息中提取indValId，用于明细请求
        :param compare_univ_indicators_info:格式是{data:{self:{},list:[{},{}]}}。其中list[]中的每个字典是一个对比学校，如果没有对比学校，则没有list[]
        :return:
        """
        result= {}

        #处理本校数据
        dict_self = compare_univ_indicators_info["self"]
        dict_self_new = {
            "univCode": dict_self["univCode"],
            "univName": dict_self["univName"],
            "details": {}
        }
        # 提取 self 的 details 中的 indValId
        for key, detail in dict_self['details'].items():
            dict_self_new['details'][key] = detail['indValId']
        # 将 self 添加到结果中
        result[dict_self_new['univCode']] = dict_self_new

        # 提取对比学校的数据
        if not compare_univ_indicators_info.get("list"):
            return result
        list_all_compare_univ = compare_univ_indicators_info["list"]
        for dict_compare_univ in list_all_compare_univ:
            dict_compare_univ_new = {
                "univCode": dict_compare_univ["univCode"],
                "univName": dict_compare_univ["univName"],
                "details": {}
            }
            for key, detail in dict_compare_univ['details'].items():
                dict_compare_univ_new['details'][key] = detail['indValId']
            result[dict_compare_univ_new['univCode']] = dict_compare_univ_new
        return  result