# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : Overview.py
@Author  : Chlon
@Date    : 2025/9/2 13:23
@Desc    : 
"""
from product.ubi.pages.UbiCommon import UbiCommon
from common.ApiLoader import ApiLoader
from common.path_util import get_absolute_path
from common.FileManager import FileManager
from common.DataOperation import DataOperation

class Overview(UbiCommon):
    def __init__(self, session):
        super().__init__(session)
        self.fm = FileManager()
        self.do = DataOperation()
        self.ru = session
        api_path = get_absolute_path("product/ubi/apis/")
        self.al = ApiLoader(api_path)

    def data_export(self,verNo,rankingTypeId,range_start,range_end):
        api_data_export = self.al.get_api('Overview', 'Overview', 'data_export')
        origin_url = api_data_export['url']
        url = self.do.format_url(origin_url,rankingTypeId=rankingTypeId,verNo=verNo,range_start=range_start,range_end=range_end)
        response = self.ru.request(
            method=api_data_export['method'],
            url=url,
            headers=api_data_export.get('headers')
        )
        assert response.status_code == api_data_export["expected"]["code"], f"总体定位数据导出请求失败！实际请求响应:{response}"
        return response

    # def detail_click(self,indValId,verNo,detailDefId):
    #     api_ind_detail = self.al.get_api('Overview', 'Overview', 'ind_detail')
    #     origin_url = api_ind_detail['url']
    #     url = self.do.format_url(origin_url,indValId=indValId,verNo=verNo,detailDefId=detailDefId)
    #
    #     response = self.ru.request(
    #         method=api_ind_detail['method'],
    #         url=url,
    #         #headers=api_ind_detail.get('headers')
    #     )
    #     response_json = response.json()
    #     assert response_json["code"] == api_ind_detail["expected"]["code"], f"明细请求响应:{response_json}"
    #     return response_json["data"]