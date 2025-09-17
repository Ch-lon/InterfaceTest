# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : cg_operations.py
@Author  : Chlon
@Date    : 2025/9/4 17:32
@Desc    : 获取Authorization和cookie
"""
from common.apis_loader import ApiLoader
from common.path_util import get_absolute_path
from common.request_util import RequestUtil
from common.FileManager import FileManager
import requests

class CGOperations:
    def __init__(self):
        self.base_config = get_absolute_path("../../config/config.yml")
        api_path = get_absolute_path("../apis")
        self.ru = RequestUtil ()
        self.al = ApiLoader(api_path)
        self.fm = FileManager()

    # 选择产品
    def choose_product(self,product_name:str):
        return







# if __name__ == '__main__':
#     cg = CGOperations()
#     print(cg.get_authorization())