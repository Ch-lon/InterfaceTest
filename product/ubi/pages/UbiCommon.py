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
from common.RequestUtil import RequestUtil
from selenium import webdriver
from selenium.webdriver.ie.service import Service



class UbiCommon:
    def __init__(self, session):
        super().__init__()
        self.ru = session
        #self.config = config
        api_path = get_absolute_path("product/ubi/apis/")
        self.al = ApiLoader(api_path)


