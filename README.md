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




