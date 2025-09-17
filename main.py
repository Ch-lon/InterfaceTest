from http.client import responses
from common.logger import get_logger
import requests
import yaml
from common.path_util import get_absolute_path

config_path = get_absolute_path("config/config.yml")
api_path = get_absolute_path("product/ubi/apis/login_cg.yml")
def load_config(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)



if __name__ == '__main__':
    config = load_config(config_path)
    api_config = load_config(api_path)
    print(config)
    print(api_config)

    base_url =config['测试环境']['base_url']
    login_config = api_config['login_cg']['login_page']
    url = login_config['url']
    full_url = base_url + url
    print(full_url)

    headers = login_config["headers"]
    print(headers)

    data = login_config["default_data"]
    print(data)

    responses = requests.request(
        "post",
        url=full_url,
        #不要加请求头，Content-Type: multipart/form-data; boundary=xxxx是浏览器自动生成，不应该写死
        #requests 会自动生成正确的，服务器就能解析
        #headers=headers,
        data=data)
    logger = get_logger()
    logger.info(f"请求：{full_url} {data}")
    print(responses.status_code)
    print(responses.reason)
    print(responses.json()["code"])
    print(responses.text)
    logger.info(f"响应：{responses.status_code} {responses.reason} {responses.json()}")