from selenium import webdriver
import time
from selenium.webdriver.chrome.options import  Options
import yaml
from selenium.webdriver.ie.service import Service

options = webdriver.ChromeOptions()
options.add_argument("--headless")  # 可不显示浏览器
driver = webdriver.Chrome(
        service=Service(executable_path="C:\Program Files\Google\Chrome\Application\chromedriver.exe"),
        options=options,
    )

# 打开主登录页
#driver.get("https://cg-3f3ab907.gaojidata.com/login")

# 这里可以通过 send_keys 填充用户名密码，或直接跳过登录，访问 jumpUrl 带 token
jump_url = "https://ubi-3f3ab907.gaojidata.com/login?loginTypeId=2&univCode=RC00021&loginName=chenglong.yu&token=GKPOKIxuqSL_GNcn_1bzvMvQYEfQsXDI8e4pCFWIgiE="
driver.get(jump_url)

# 等待页面 JS 执行完成

# 如果新窗口打开了，需要切换
#driver.switch_to.window(driver.window_handles[-1])
x = driver.get_cookie
print(x)
# 获取所有 cookie
cookies = {c['name']: c['value'] for c in driver.get_cookies()}
print()
print("UBI cookies:", cookies)

driver.quit()
