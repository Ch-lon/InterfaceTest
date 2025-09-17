# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : UbiCommon.py
@Author  : Chlon
@Date    : 2025/8/29 13:49
@Desc    : 国际360测试基类
"""
# InterfaceTest/product/ubi/pages/Login.py
from common.apis_loader import ApiLoader
from common.path_util import get_absolute_path
from selenium import webdriver
from selenium.webdriver.ie.service import Service



class UbiCommon:
    def __init__(self, request_util):
        super().__init__()
        self.ru = request_util
        #self.config = config
        api_path = get_absolute_path("../apis/")
        self.al = ApiLoader(api_path)


    # def get_cookie(self, token, school_code):
    #     """使用token获取cookie"""
    #     api_config = self.al.get_api('login_cg', 'cookie')
    #
    #     options = webdriver.ChromeOptions()
    #     options.add_argument("--headless")  # 可不显示浏览器
    #     driver = webdriver.Chrome(
    #         service=Service(executable_path="C:\Program Files\Google\Chrome\Application\chromedriver.exe"),
    #         options=options,
    #     )
    #     # 格式化URL，替换路径参数
    #     url =self.config.get("ubi_base_url") + api_config['url'].format(school_code=school_code, auth=token)
    #     driver.get(url)
    #     # 发送请求，注意这里我们期望重定向，并且requests的session会自动处理cookie
    #
    #     # 确认cookie已经设置在session中
    #     #assert response.cookies, "未能从响应中获取cookie"
    #
    #     # 返回session对象，其中包含了cookie
    #     return self.ru.session


