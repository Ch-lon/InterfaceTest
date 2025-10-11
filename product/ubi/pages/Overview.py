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

class Overview(UbiCommon):
    def __init__(self, session):
        super().__init__(session)
        self.fm = FileManager()
        self.ru = session
        api_path = get_absolute_path("product/ubi/apis/")
        self.al = ApiLoader(api_path)

    def data_export(self,verNo,rankingTypeId,range_start,range_end):
        api_data_export = self.al.get_api('Overview', 'Overview', 'data_export')
        url = api_data_export['url']
        url_params = {
            "rankingTypeId": rankingTypeId,
            "verNo": verNo,
            "range_start": range_start,
            "range_end": range_end
        }
        response = self.ru.request(
            method=api_data_export['method'],
            url=url.format(**url_params),
            headers=api_data_export.get('headers')
        )
        return response

    def test(self):
        response = 1