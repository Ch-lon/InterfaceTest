# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : simulate_test_data.py
@Author  : Chlon
@Date    : 2025/11/11 11:35
@Desc    : 排名推演测试参数文件
"""
PAYLOAD_DEFAULT = {
    "list": [
        {"indId": 16254, "val": 0}, {"indId": 16266, "val": 0}, {"indId": 16267, "val": 0},
        {"indId": 16255, "val": 0}, {"indId": 16268, "val": 0}, {"indId": 16269, "val": 0},
        {"indId": 16256, "val": 33}, {"indId": 16257, "val": 51.15}, {"indId": 16270, "val": 28.95},
        {"indId": 16271, "val": 22.2}, {"indId": 16258, "val": 21416}, {"indId": 16424, "val": 20020},
        {"indId": 16425, "val": 1049}, {"indId": 16426, "val": 20601}, {"indId": 16265, "val": 6.01313513},
        {"indId": 16259, "val": 0}, {"indId": 16260, "val": 0}, {"indId": 16261, "val": 0.00820487},
        {"indId": 16262, "val": 0.01271755}, {"indId": 16263, "val": 5.32471407}, {"indId": 16264, "val": 4022}
    ],
    "suffix": "Typ"
}

# 在这里添加你的“其他情况”，例如，一个“全零”的 payload
PAYLOAD_ALL_ZEROS = {
    "list": [
        {"indId": 16254, "val": 0}, {"indId": 16266, "val": 0}, {"indId": 16267, "val": 0},
        {"indId": 16255, "val": 0}, {"indId": 16268, "val": 0}, {"indId": 16269, "val": 0},
        {"indId": 16256, "val": 0}, {"indId": 16257, "val": 0}, {"indId": 16270, "val": 0},
        # ... (您可以把所有 val 都设为 0)
    ],
    "suffix": "Typ"
}