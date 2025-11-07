# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : Univranking.py
@Author  : Chlon
@Date    : 2025/10/17 13:16
@Desc    : 动态排名类
"""
from product.ubi.pages.UbiCommon import UbiCommon
from common.ApiLoader import ApiLoader
from common.path_util import get_absolute_path
from common.DataOperation import DataOperation
import allure

class Univranking(UbiCommon):
    def __init__(self, session):
        super().__init__(session)
        #self.do = DataOperation()
        #self.ru = session
        ##self.al = ApiLoader(api_path)

    @allure.step("获取所有学校动态排名")
    def get_all_univ_ranking(self, rankingTypeId,verNo,compareVerNo):
        """
        获取所有学校动态排名
        :param rankingTypeId: 排行榜类型id
        :param verNo: 排行榜版本号
        :param compareVerNo: 比较版本号
        :return:
        """
        if not compareVerNo:
            raise ValueError("请输入需要进行比较的版本号！")
        api_univranking =  self.al.get_api('Univranking', 'Univranking', 'rank')
        origin_url = api_univranking['url']
        url = self.do.format_url(origin_url,rankingTypeId=rankingTypeId,verNo=verNo,compareVerNo=compareVerNo)
         #   api_univranking['url'].format(rankingTypeId=rankingTypeId,verNo=verNo,compareVerNo=compareVerNo)
        response = self.ru.request(
            method=api_univranking['method'],
            url=url,
            headers=api_univranking.get('headers')
        )
        res = response.json()
        assert res["code"] == api_univranking["expected"]["code"], f"请求失败！请求响应:{res}"

    @allure.step("导出动态排名数据")
    def export_univ_ranking(self, rankingTypeId,verNo,compareVerNo):
        api_export_univranking = self.al.get_api('Univranking', 'Univranking', 'data_export')
        origin_url = api_export_univranking['url']
        url = self.do.format_url(origin_url,rankingTypeId=rankingTypeId,verNo=verNo,compareVerNo=compareVerNo)
        response = self.ru.request(
            method=api_export_univranking['method'],
            url=url,
            headers=api_export_univranking.get('headers')
        )
        return  response