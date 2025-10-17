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
from common.DataOperation import DataOperation


class CGOperations:

    def __init__(self,session,config):
        api_path = get_absolute_path("product/cg/apis/")
        self.al = ApiLoader(api_path)
        self.fm = FileManager()
        self.do = DataOperation()
        self.ru = session
        # session 中已经包含了 config，直接使用
        self.config = getattr(session, 'config', config)

    def cg_login_and_get_token(self):
        """登录操作并返回token"""
        api_config = self.al.get_api('login_cg', 'login_cg','login_page')
        url = api_config['url']
        data = self.do.get_copy_key_from_dict(api_config, 'default_data')
        #data = api_config.get('default_data', {}).copy()
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

    def add_account(self,productCode,univCode):
        """添加账号"""
        api_add_account = self.al.get_api('login_cg', 'login_cg','add_account')
        url = api_add_account["url"]
        data = self.do.get_copy_key_from_dict(api_add_account, 'data')
        data.update({
            "creator": self.config['username'],
            "productCode": productCode,
            "remark": "",
            "univCode": univCode
        })
        response = self.ru.request(
            method=api_add_account['method'],
            url=url,
            json=data,
        )
        res = response.json()
        return res["code"]




# if __name__ == '__main__':
#     cg = CGOperations()
#     print(cg.get_authorization())