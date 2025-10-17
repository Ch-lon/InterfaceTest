# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : database.py
@Author  : Chlon
@Date    : 2025/10/16 13:10
@Desc    : 数据库操作，用于获取测试所需的univCode和univName
"""

import pymysql
from common.path_util import get_absolute_path
from common.FileManager import FileManager

class Database:

    config_path = get_absolute_path("config/config.yml")
    fm = FileManager()

    def mysql_connect(self):
        config = self.fm.load_yaml_file(self.config_path)
        db = pymysql.connect(host="192.168.1.2", user="root", password="<PASSWORD>", database="univ360", charset="utf8")
