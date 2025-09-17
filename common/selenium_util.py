# InterfaceTest/common/selenium_util.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# 导入 WebDriverWait 和相关模块
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.ie.service import Service
from common.logger import get_logger

logging = get_logger(__name__)
def get_cookies_from_browser(url: str) -> dict:
    """
    使用 Selenium 访问指定 URL，并显式等待 authToken cookie 出现后再获取所有 cookies。
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(
        service=Service(executable_path="C:\Program Files\Google\Chrome\Application\chromedriver.exe"),
        options=options,
    )
    cookies_dict = {}
    try:
        print(f"Selenium 正在访问 URL: {url}")
        logging.info(f"访问URL：{url}")
        driver.get(url)

        # --- 核心修改 ---
        # 显式等待 'authToken' cookie 出现，最长等待10秒
        print("正在等待 'authToken' cookie出现...")
        WebDriverWait(driver, 10).until(
            lambda d: d.get_cookie('authToken') is not None
        )
        print("'authToken' cookie 已成功设置！")

        # 获取所有 cookie
        cookies = driver.get_cookies()
        cookies_dict = {c['name']: c['value'] for c in cookies}
        print(f"成功从浏览器获取所有 Cookies: {cookies_dict}")
        logging.info(f"获取Cookie成功：{cookies_dict}")

    except TimeoutException:
        print("错误：等待 'authToken' cookie 超时。页面可能没有按预期设置该cookie。")
        logging.error("等待Cookie超时")
        # 可以在这里增加更多的调试信息，比如打印页面源码
        print(driver.page_source)
    except Exception as e:
        print(f"使用 Selenium 获取 cookie 时出错: {e}")
        logging.error(f"使用Selenium获取Cookie时出错：{e}")
    finally:
        driver.quit()

    return cookies_dict