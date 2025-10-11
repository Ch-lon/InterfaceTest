# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : UbiCommon.py
@Author  : Chlon
@Date    : 2025/8/29 13:49
@Desc    : 国际360测试基类
"""
# InterfaceTest/product/ubi/pages/Login.py
from common.ApiLoader import ApiLoader
from common.path_util import get_absolute_path
from common.logger import get_logger
import allure


class UbiCommon:
    download_files_path = get_absolute_path('download_files')
    def __init__(self, session):
        super().__init__()
        self.ru = session
        #self.config = config
        api_path = get_absolute_path("product/ubi/apis/")
        self.al = ApiLoader(api_path)
        self.logging = get_logger(__name__)

    @allure.step("获取当前最新版本信息及排名类型")
    def get_version(self):
        """
        """
        api_config = self.al.get_api('Overview', 'Overview','version')

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
        response_json = response.json()
        assert response_json["code"] == api_config["expected"]["code"]
        verNo = response_json["data"][0]["verNo"]
        rankingTypeId = response_json["data"][0]["rankingTypeId"]
        self.logging.info(f"排名类型为：{rankingTypeId},当前最新版本为：{verNo}")
        return rankingTypeId,verNo

    @allure.step("获取总体定位页面的详细数据")
    def get_overview_data(self, verNo, rankingTypeId):
        """获取并返回整个概览页面的数据"""
        api_config = self.al.get_api('Overview', 'Overview', 'range')
        url = api_config['url'].format(verNo=verNo, rankingTypeId=rankingTypeId)
        response = self.ru.request(
            method=api_config['method'],
            url=url,
            headers=api_config.get('headers')
        )
        response_json = response.json()
        assert response_json["code"] == api_config["expected"]["code"]
        return response_json.get("data")

    @allure.step("获取当前院校的同排名区间")
    def get_ranking_range(self, overview_data):
        """从已获取的概览数据中提取排名区间"""
        range_val = overview_data["typ"]["overall"]["range"]
        self.logging.info(f"当前院校同排名区间为：{range_val}")
        return range_val[0], range_val[1]