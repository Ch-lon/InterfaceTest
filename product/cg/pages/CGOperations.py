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
import allure
from playwright.sync_api import Playwright,Page,sync_playwright


class CGOperations:

    def __init__(self,session):
        api_path = get_absolute_path("product/cg/apis/")
        route_path = get_absolute_path("config/")
        self.route = ApiLoader(route_path)
        self.cg_api = ApiLoader(api_path)
        self.fm = FileManager()
        self.do = DataOperation()
        self.ru = session
        # session 中已经包含了 config，直接使用
        self.config = getattr(session, 'config')

    def cg_login_and_get_token(self):
        """登录操作并返回token"""
        api_config = self.cg_api.get_api('login_cg', 'login_cg','login_page')
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
        api_add_account = self.cg_api.get_api('login_cg', 'login_cg','add_account')
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



    @allure.step("使用playwright进入相应页面")
    def go_to_product_page(self, page: Page, productCode, univCode, page_name, token):
        """
        page: 由 pytest fixture 传入的、活跃的页面对象
        """
        # 1. URL 拼接逻辑 (保持你原有的逻辑不变)
        page_route = self.route.get_api('route', f'{productCode}', f'{page_name}')
        school_url = self.cg_api.get_url('login_cg', 'login_cg', 'school_route')

        # 这里的 self.do.format_url 和 config 需要确保能访问到
        url = self.do.format_url(
            school_url,
            loginTypeId=self.config["loginTypeId"],
            univCode=univCode,
            loginName=self.config["username"],
            token=token
        )

        base_url = self.config.get(f"{productCode}_base_url")
        full_url = base_url + url

        print(f"  -> [CGOperations] 正在访问页面: {full_url}")
        page.goto(full_url, wait_until="networkidle")
        # 2. 使用传入的 page 对象进行跳转
        # 不需要 with sync_playwright()，也不需要 launch
        try:
            # 检查当前页面是否已经跳转到目标页面
            if not page.url.endswith(page_route):
                target_page_url = f"{base_url}/{page_route}"
                page.goto(target_page_url, wait_until="networkidle")
        except Exception as e:
            print(f"  -> 跳转 {page_name} 页面失败: {e}")
            raise e  # 建议抛出异常，让测试用例知道前置步骤失败了

        # 不需要 return page，因为传入的 page 是引用传递，状态已经改变


#
# if __name__ == '__main__':
#     cg = CGOperations()
#     print(cg.get_authorization())