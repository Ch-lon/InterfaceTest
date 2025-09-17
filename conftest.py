# InterfaceTest/conftest.py
import pytest
import yaml
from urllib.parse import urljoin
from common.request_util import RequestUtil
from common.selenium_util import get_cookies_from_browser
# 从新的、正确的位置导入 CGLoginPage
from product.ubi.pages.Login import LoginPage


@pytest.fixture(scope="session", autouse=True)
def config():
    """全局配置初始化"""
    config_path = 'config/config.yml'
    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)
    return config_data['测试环境']


@pytest.fixture(scope="session")
def cg_session(config):
    """为 CG 平台创建一个 RequestUtil 实例"""
    cg_base_url = config.get('cg_base_url')
    print(f"创建 CG Session，Base URL: {cg_base_url}")
    cg_session = RequestUtil(cg_base_url)
    return cg_session


@pytest.fixture(scope="session")
def auth_token(cg_session,config):
    """登录 CG 平台并获取 auth token"""
    login_page = LoginPage(cg_session, config)
    token = login_page.login_and_get_token()
    assert token, "未能获取到 auth token"
    return token


# @pytest.fixture(scope="session")
# def ubi_request_session(config, auth_token):
#     """
#     创建最终用于 UBI 接口测试的、带 cookie 的 RequestUtil 实例。
#     """
#     ubi_base_url = config.get('ubi_base_url')
#     print(f"创建 UBI Session，Base URL: {ubi_base_url}")
#     ru = RequestUtil(ubi_base_url)
#     default_school_code = "RC00005"
#     login_name = config.get('username')
#     login_type_id = config.get('loginTypeId', 2)
#
#     # 拼接需要用 Selenium 访问的 URL
#     jump_path = f"/login?loginTypeId={login_type_id}&univCode={default_school_code}&loginName={login_name}&token={auth_token}"
#     jump_url = urljoin(ubi_base_url, jump_path)
#
#     # 使用 Selenium 获取 cookie
#     cookies = get_cookies_from_browser(jump_url)
#     if not cookies:
#         pytest.fail(f"未能从 {jump_url} 获取到 cookie。")
#
#     # 将 cookie 注入到 requests session 中
#     ru.session.cookies.update(cookies)
#
#     # 同样可以将 token 设置到请求头中
#     ru.session.headers.update({'Authorization': auth_token})
#
#     yield ru