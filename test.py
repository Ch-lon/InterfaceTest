
code = x["code"]
print(code)
# url_params = {"univCode": "RC00119", "token": auth}
# test_full_url = test_url.format(**url_params)
# options = webdriver.ChromeOptions()
# options.add_argument("--headless")
# options.add_argument("--disable-gpu")
# options.add_argument("--no-sandbox")
# driver = webdriver.Chrome(
#     service=Service(executable_path="C:\Program Files\Google\Chrome\Application\chromedriver.exe"),
#     options=options,
# )
#
# driver.get(test_full_url)
#
# WebDriverWait(driver, 10).until(
#             lambda d: d.get_cookie('authToken') is not None
#         )
# cookies = driver.get_cookies()
# cookies_dict = {c['name']: c['value'] for c in cookies}
# print(cookies_dict)
# driver.quit()

# test_response = requests.get(test_full_url, cookies=cookies_dict)
# print(test_response.text)