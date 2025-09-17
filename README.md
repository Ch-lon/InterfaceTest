# InterfaceTest
基于pytest的接口自动化
InterfaceTest /
├── common /
    ├── requests_util.py
├── data /
    ├── apis /
        ├── load_apis.yml  
    ├── pages /
        ├── login.py
├── logs /
    ├──test.log
├── config /
│   ├── config.yml
├── testcases /
│   ├── conftest.py
│   └── test_login.py
└── requirements.txt


# 检查第二步是否成功
    if userinfo_response.status_code == 200:
        print("会话建立成功！Session已自动保存必要Cookie。")
        user_info = userinfo_response.json()
        print(f"欢迎用户: {user_info['data']['UserName']}")

        #进入ubi
        ubi_url = 'https://cg-3f3ab907.gaojidata.com/api/v1/menu/list?code=ubi'
        headers = {
            'Authorization': temp_token,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN',
            'Host': 'cg-3f3ab907.gaojidata.com',
            'Referer': 'https://cg-3f3ab907.gaojidata.com/home',
         }
        api_response = session.get(ubi_url, headers=headers)  # 使用同一个session
        print(f"数据接口状态: {api_response}")

        # 尝试解析JSON，如果失败则打印文本
        try:
            api_data = api_response.json()
            print(f"数据接口响应 (JSON): {api_data}\n")
        except requests.exceptions.JSONDecodeError:
            print(f"数据接口响应 (Text): {api_response.text}\n")

        if api_response.status_code == 200:


            #进入上海交大
            shanghai_url = 'https://cg-3f3ab907.gaojidata.com/api/v1/employee-user/univ-perm/list?productCode=ubi'
            headers_1 = {
                'Authorization': temp_token,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN',
                'Host': 'cg-3f3ab907.gaojidata.com',
                'Referer': 'https://cg-3f3ab907.gaojidata.com/staff-supervise',
            }
            api_response = session.get(shanghai_url, headers=headers_1)  # 使用同一个session
            print(f"数据接口状态: {api_response}")

            # 尝试解析JSON，如果失败则打印文本
            try:
                api_data = api_response.json()
                print(f"数据接口响应 (JSON): {api_data}\n")
            except requests.exceptions.JSONDecodeError:
                print(f"数据接口响应 (Text): {api_response.text}\n")

