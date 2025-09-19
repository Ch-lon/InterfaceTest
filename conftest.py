# InterfaceTest/conftest.py
import pytest
import yaml
from common.RequestUtil import RequestUtil
from product.cg.pages.CGOperations import CGOperations
from common.FileManager import FileManager
from common.path_util import get_absolute_path


@pytest.fixture(scope="session", autouse=True)
def config():
    """全局配置初始化"""
    config_path = get_absolute_path('config/config.yml')
    fm = FileManager()
    config_data = fm.load_yaml_file(config_path)
    return config_data['测试环境']


@pytest.fixture(scope="session")
def cg_session(config):
    """为 CG 平台创建一个 RequestUtil 实例"""
    cg_base_url = config.get('cg_base_url')
    print(f"创建 CG Session，Base URL: {cg_base_url}")
    cg_session = RequestUtil(cg_base_url)
    # 将config附加到session实例上，方便后续调用
    cg_session.config = config
    return cg_session


@pytest.fixture(scope="session")
def auth_token(cg_session,config):
    """登录 CG 平台并获取 auth token"""
    cg = CGOperations(cg_session,config)
    token = cg.login_and_get_token()
    assert token, "未能获取到 auth token"
    return token

