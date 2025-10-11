# InterfaceTest/conftest.py
import pytest
import yaml
from common.RequestUtil import RequestUtil
from product.cg.pages.CGOperations import CGOperations
from common.FileManager import FileManager
from common.path_util import get_absolute_path
from common.logger import get_logger
from common.ApiLoader import ApiLoader

logging = get_logger(__name__)

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
    token = cg.cg_login_and_get_token()
    assert token, "未能从CG平台获取到 auth token"
    return token


# 登录对应的产品页面
@pytest.fixture(scope="session")
def choose_product_session(auth_token, config):
    """
    这是一个工厂 fixture，它返回一个内部函数。
    你可以调用这个返回的函数并传入 product_name 和 school_code。
    """
    def _choose_product_session(product_name: str, school_code: str):
        """
        根据产品名称、学校代码和token进行登录，将cookies更新到session中。
        :param product_name: 产品名称，例如 "ubi", "ub", "vub"
        :param school_code: 学校代码
        :return: 带有该产品cookies的session
        """
        api_path = get_absolute_path("product/cg/apis/")
        al = ApiLoader(api_path)

        # 1. 根据产品名称获取对应的 base_url
        base_url_key = f"{product_name}_base_url"
        product_base_url = config.get(base_url_key)
        if not product_base_url:
            raise ValueError(f"在 config.yml 中未找到产品 '{product_name}' 对应的 base_url ('{base_url_key}')")

        # 2. 使用获取到的 base_url 初始化 RequestUtil
        product_session = RequestUtil(product_base_url)

        # 3. 从 api yml文件中加载 school_cookie 的API配置
        product_cookies_config = al.get_api("login_cg", "login_cg", f"{product_name}_login")
        url_template = product_cookies_config["url"]

        # 4. 准备URL的参数
        # 注意：这里的key需要和 aip yml 文件中URL模板里的占位符完全对应
        data = {
            "loginTypeId": config.get("loginTypeId"),
            "univCode": school_code,
            "loginName": config.get("username"),
            "token": auth_token
        }
        # # 5. 请求产品的登录接口并获取cookies，更新到session中
        full_url = product_base_url + url_template
        res = product_session.request(
            method=product_cookies_config["method"],
            url=url_template,
            json=data,
        )
        response = res.json()
        # 记录在log中
        logging.debug(f"{product_name}的登录响应：{response}")
        assert response["code"] == 200, f"登录{product_name}预期的状态码为 200，实际返回的状态码为 {response['code']}"
        cookies = res.cookies.get_dict()
        if not cookies:
            pytest.fail(f"未能从 {full_url} 获取到 cookie。")
        # 将 cookie 注入到 requests session 中
        product_session.session.cookies.update(cookies)
        # 同样可以将 token 设置到请求头中
        product_session.session.headers.update({'Authorization': auth_token})
        return product_session

    # 外层 fixture 返回内部函数
    return _choose_product_session
