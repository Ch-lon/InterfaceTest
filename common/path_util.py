# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : path_util.py
@Author  : Chlon
@Date    : 2025/8/28 13:23
@Desc    : 路径类的工具
"""
import os
import sys

# # 项目根目录（假设 common 是根目录下的文件夹）
# PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# def get_absolute_path(relative_path):
#     return os.path.join(PROJECT_ROOT, relative_path)


def get_absolute_path(relative_path: str):
    """
    将一个相对路径转换为绝对路径。
    Args:
        relative_path (str): 相对于调用此函数文件的相对路径。
    Returns:
        str: 转换后的绝对路径。
    """
    # 获取调用此函数的脚本的绝对路径
    # sys._getframe(1) 访问上一层栈帧，即调用者的信息。你当前所在文件的绝对路径
    caller_path = os.path.abspath(sys._getframe(1).f_code.co_filename)
    # 获取调用者所在的目录
    caller_dir = os.path.dirname(caller_path)
    # 拼接目录和相对路径，得到最终的绝对路径
    absolute_path = os.path.join(caller_dir, relative_path)
    return absolute_path