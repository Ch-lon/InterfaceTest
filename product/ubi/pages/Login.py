# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : Login.py
@Author  : Chlon
@Date    : 2025/9/1 13:25
@Desc    : 
"""
# product/pages/login.py
from common.apis_loader import ApiLoader
from product.ubi.pages.UbiCommon import UbiCommon
from common.path_util import get_absolute_path
from common.FileManager import FileManager


class LoginPage(UbiCommon):
    def __init__(self, session,config):
        """
        初始化LoginPage
        Args:
            request_util: 配置好的RequestUtil实例
            config (dict): 包含环境配置的字典，例如base_url, username, password
        """
        super().__init__(session)
        #self.ru = RequestUtil()
        #使用在初始化时接收一个已经配置好的实例
        self.ru = session
        self.config =  config
        api_path = get_absolute_path("../apis/")
        #self.config_path = get_absolute_path("../../../config/config.yml")
        self.al = ApiLoader(api_path)
        self.fm = FileManager()
        #self.config = self.fm.load_yaml_file(self.config_path)

    def login_and_get_token(self):
        """登录操作并返回token"""
        api_config = self.al.get_api('login_cg', 'login_page')
        url = api_config['url']
        data = api_config.get('default_data', {}).copy()

        data['LoginName'] = self.config['username']
        data['Password'] = self.config['password']

        response = self.ru.request(
            method=api_config['method'],
            url=url,
            data=data,
        )

        assert response.status_code == 200
        response_json = response.json()
        assert response_json["code"] == api_config["expected"]["code"]
        assert response_json["message"] == api_config["expected"]["message"]
        return response_json.get("data")

