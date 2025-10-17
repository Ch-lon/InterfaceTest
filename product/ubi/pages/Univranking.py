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
        self.do = DataOperation()
        self.ru = session
        api_path = get_absolute_path("product/ubi/apis/")
        self.al = ApiLoader(api_path)

    @allure.step("获取所有学校动态排名")
    def get_all_univ_ranking(self, rankingTypeId,verNo,compareVerNo):
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