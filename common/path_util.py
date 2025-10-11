# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : path_util.py
@Author  : Chlon
@Date    : 2025/8/28 13:23
@Desc    : 路径类的工具
"""
import os
from pathlib import Path

# --- 核心优化 ---
# 1. 将项目根目录定义为一个常量。
#    Path(__file__) -> 获取当前文件(path_util.py)的绝对路径
#    .parent -> 获取父目录 (common)
#    .parent -> 再次获取父目录 (InterfaceTest)，这就是我们的项目根目录
PROJECT_ROOT = Path(__file__).parent.parent # 路径从 InterfaceTest/

def get_absolute_path(relative_path_from_root: str) -> str:
    """
    将一个相对于【项目根目录】的路径转换为绝对路径。
    Args:
        relative_path_from_root (str): 相对于项目根目录(InterfaceTest/)的路径。
    Returns:
        str: 转换后的绝对路径字符串。
    """
    # 2. 使用 os.path.join 将根目录和相对路径拼接起来
    #    os.path.normpath 会规范化路径，处理掉多余的斜杠或点
    absolute_path = os.path.normpath(os.path.join(PROJECT_ROOT, relative_path_from_root))
    return absolute_path