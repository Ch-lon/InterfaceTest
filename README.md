# InterfaceTest
基于pytest的接口自动化
遵循了 Page Object 设计模式，并且将配置、测试用例和业务逻辑代码进行了有效的分离。
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

pytest -q testcases/ubi --alluredir=reports/allure_results 
pytest -q testcases/ubi/test_indicator_view.py/test_IndicatorView01 --alluredir=reports/allure_results
pytest -q testcases/ubi/test_indicator_view.py::TestIndicatorView::test_IndicatorView02 --alluredir=reports/allure_results
allure serve reports/allure_reports
allure-combine reports/allure_reports
# 下载playwright install
 $env:PLAYWRIGHT_DOWNLOAD_HOST="https://npmmirror.com/mirrors/playwright/"; playwright install
Ctrl+Alt+L
开启临时服务器： 在生成报告的目录（reports/allure_reports）下，打开命令行，运行：
# 端口号 8000 可以自己改
python -m http.server 8000
配置
  report_url: "http://192.168.0.49:8000"  # 你的IP + 端口


