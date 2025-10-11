# common/RequestUtil.py
import requests
from common.logger import get_logger
from urllib.parse import urljoin




class RequestUtil:
    """
    每次实例化，需要传入各个产品的base_url,如：ubi_base_url: "https://ubi-3f3ab907.gaojidata.com"
    封装requests库，提供更方便的HTTP请求方法。
    """
    def __init__(self,base_url=None):
        # 创建一个Session对象
        self.session = requests.Session()
        # 每次实例化时就接收并保存 base_url。
        self.base_url = base_url
        self.logger = get_logger(__name__)

    def request(self,method, url, **kwargs):
        if not self.base_url:
            raise ValueError("请先在config.yml中设置当前产品的base_url")
        """发送HTTP请求"""
        full_url = self._build_full_url(url)

        self.logger.info(f"发送请求: {method} {full_url}")
        self.logger.debug(f"请求参数: {kwargs}")

        try:
            response = self.session.request(method, full_url, **kwargs)
            self.logger.info(f"响应状态码: {response.status_code}")

            # --- 核心修改：智能记录响应体 ---
            #从响应头中获取 Content-Type，并将其转换为小写以方便后续的字符串匹配。
            content_type = response.headers.get('Content-Type', '').lower()
            # 检查是否为常见的文本类型
            if 'application/json' in content_type:
                try:
                    self.logger.debug(f"响应内容 (JSON): {response.json()}")
                except ValueError:
                    # 如果解析JSON失败，回退到记录文本
                    self.logger.debug(f"响应内容 (Text, JSON解析失败): {response.text}")
            elif 'text/' in content_type:
                self.logger.debug(f"响应内容 (Text): {response.text}")
            else:
                # 对于所有其他类型（二进制文件如xlsx, jpg, pdf等）
                # 只记录元信息，不记录具体内容，避免乱码
                #从响应头获取文件的大小（Content-Length），否则默认为未知
                content_length = response.headers.get('Content-Length', '未知')
                self.logger.debug(f"响应内容 (二进制): 类型 '{content_type}', 大小: {content_length} 字节")

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
