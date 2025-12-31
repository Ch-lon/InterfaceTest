# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : date_format.py
@Author  : Chlon
@Date    : 2025/12/29 11:01
@Desc    : 日期处理
"""
from datetime import datetime
import re

class DateFormat:

    @staticmethod
    def format_date_string(date):
        """
        将 '202508' 转换为 '2025年08月' 格式
        使用datetime验证日期有效性
        参数:
            date:格式为 'YYYYMM'

        返回:
            格式化后的日期字符串 'YYYY年MM月'
        """
        try:
            # 将字符串解析为datetime对象
            date_obj = datetime.strptime(str(date), "%Y%m")
            # 格式化为中文年月
            return date_obj.strftime("%Y年%m月")
        except ValueError as e:
            raise ValueError(f"无效的日期格式: {date}") from e
