import requests
import selenium
from selenium import webdriver
from selenium.webdriver.ie.service import Service
from selenium.webdriver.support.ui import WebDriverWait

cg_url = "https://cg-3f3ab907.gaojidata.com/api/v1/sso/login/loginByPwd"
test_url = "https://ubi-3f3ab907.gaojidata.com/login?loginTypeId=2&univCode={univCode}&loginName=chenglong.yu&token={token}"
login_url = "https://ubi-3f3ab907.gaojidata.com/ubi-api/v1/auth/login"
#test_url1 = "https://ubi-3f3ab907.gaojidata.com/login?loginTypeId=2&univCode=RC00005&loginName=chenglong.yu&token=dsBGXN2pBOsjN2FHj5XQ3brp_oknJzhERDOa6JtG1lw="

response = requests.post(cg_url, data={"LoginName": "chenglong.yu", "Password": "shanghai1008"})
print(response.json())
auth = response.json()["data"]
print(auth)

params = {
    "loginTypeId": 2,
    "univCode": "RC00005",
    "loginName": "chenglong.yu",
    "token": auth
}

headers = {
    "Content-Type": "application/json",
    "Origin": "https://ubi-3f3ab907.gaojidata.com",
    "Referer": "https://ubi-3f3ab907.gaojidata.com/login?loginTypeId=2&univCode=RC00119&loginName=chenglong.yu",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}
session = requests.Session()
res = session.post(login_url, json=params)

print("登录响应：", res.status_code, res.text)
print("登录后的 cookies：", session.cookies.get_dict())
