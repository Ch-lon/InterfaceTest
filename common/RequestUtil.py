# common/RequestUtil.py
import requests
from common.logger import get_logger
from urllib.parse import urljoin




class RequestUtil:
    def __init__(self,base_url=None):
        # 创建一个Session对象
        self.session = requests.Session()
        # 每次实例化时就接收并保存 base_url。
        self.base_url = base_url
        self.logger = get_logger(__name__)

    def request(self,method, url, **kwargs):
        if not self.base_url:
            raise ValueError("请先在config.yml中设置ubi_base_url")
        """发送HTTP请求"""
        full_url = self._build_full_url(url)

        self.logger.info(f"发送请求: {method} {full_url}")
        self.logger.debug(f"请求参数: {kwargs}")

        try:
            response = self.session.request(method, full_url, **kwargs)
            self.logger.info(f"响应状态码: {response.status_code}")
            # 记录更详细的响应体
            try:
                self.logger.debug(f"响应内容 (JSON): {response.json()}")
            except ValueError:
                self.logger.debug(f"响应内容 (Text): {response.text}")

            return response
        except Exception as e:
            self.logger.error(f"请求失败: {str(e)}")
            raise

    def _build_full_url(self,url):
        """构建完整的URL"""
        if url.startswith(('http://', 'https://')):
            return url
        # urljoin 会根据URL规则正确处理路径拼接,避免斜杠问题
        return urljoin(self.base_url,url)

if __name__ == '__main__':
    x = "https://cg-3f3ab907.gaojidata.com"
    y = "/api/v1/sso/login/loginByPwd"
