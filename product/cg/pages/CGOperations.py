# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : CGOperations.py
@Author  : Chlon
@Date    : 2025/9/4 17:32
@Desc    : 获取Authorization和cookie
"""
from common.ApiLoader import ApiLoader
from common.path_util import get_absolute_path
from common.RequestUtil import RequestUtil
from common.FileManager import FileManager
from common.SeleniumUtil import get_cookies_from_browser
import pytest

class CGOperations:
    def __init__(self,session,config):
        api_path = get_absolute_path("product/cg/apis/")
        self.al = ApiLoader(api_path)
        self.fm = FileManager()
        self.ru = session
        # session 中已经包含了 config，直接使用
        self.config = getattr(session, 'config', config)

    def login_and_get_token(self):
        """登录操作并返回token"""
        api_config = self.al.get_api('login_cg', 'login_cg','login_page')
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


    # 选择产品
    def choose_product_session(self, product_name: str, school_code: str, token: str):
        """
        根据产品名称、学校代码和token，选择产品并获取会话cookie。
        :param product_name: 产品名称，例如 "ubi", "ub", "vub"
        :param school_code: 学校代码
        :param token: 登录后获取的认证token
        :return: requests的Response对象
        """
        # 1. 根据产品名称获取对应的 base_url
        base_url_key = f"{product_name}_base_url"
        product_base_url = self.config.get(base_url_key)
        if not product_base_url:
            raise ValueError(f"在 config.yml 中未找到产品 '{product_name}' 对应的 base_url ('{base_url_key}')")
        # 2. 使用获取到的 base_url 初始化 RequestUtil
        product_session = RequestUtil(product_base_url)
        # 3. 从 api yml文件中加载 school_cookie 的API配置
        product_cookies_config = self.al.get_api("login_cg", "login_cg","school_cookie")
        url_template = product_cookies_config["url"]
        # 4. 准备URL的参数
        # 注意：这里的key需要和 aip yml 文件中URL模板里的占位符完全对应
        url_params = {
            "loginTypeId": self.config.get("loginTypeId"),
            "school_code": school_code,
            "loginName": self.config.get("username"),
            "auth": token  # login_cg.yml中使用的是{auth}
        }
        # 5. 使用参数格式化URL
        full_url =product_base_url + url_template.format(**url_params)
        cookies = get_cookies_from_browser(full_url)
        if not cookies:
            pytest.fail(f"未能从 {full_url} 获取到 cookie。")
        # 将 cookie 注入到 requests session 中
        product_session.session.cookies.update(cookies)
        # 同样可以将 token 设置到请求头中
        product_session.session.headers.update({'Authorization': token})
        return product_session





# if __name__ == '__main__':
#     cg = CGOperations()
#     print(cg.get_authorization())