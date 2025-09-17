# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : Overview.py
@Author  : Chlon
@Date    : 2025/9/2 13:23
@Desc    : 
"""
from product.ubi.pages.UbiCommon import UbiCommon
from common.apis_loader import ApiLoader
from common.path_util import get_absolute_path
from common.FileManager import FileManager

class Overview(UbiCommon):
    def __init__(self, session):
        super().__init__(session)
        self.fm = FileManager
        self.ru = session
        api_path = get_absolute_path("../apis/")
        self.al = ApiLoader(api_path)

    def get_version(self,**kwargs):
        """
        数据导出接口
        Args:
            company_id (str): 公司ID，会填充到URL路径中
            date (str): 日期，会填充到URL路径中
            **kwargs: 查询参数，例如 start=21, end=30
        """
        api_config = self.al.get_api('Overview', 'version')

        # 1. 格式化URL，将路径参数填充进去
        url = api_config['url']

        # 2. 准备查询参数
        #params = api_config.get('default_data', {}).copy()
        #params.update(kwargs)
        headers = api_config.get('headers')

        # 4. 【修改】: 发送请求时，同时传入 params 和 headers
        # params - 将参数放入URL
        # headers - 手动指定Content-Type，即使请求体为空
        response = self.ru.request(
            method=api_config['method'],
            url=url,
            #data=params,
            headers=headers  # 核心改动：将YML中定义的headers传入
        )
        return response