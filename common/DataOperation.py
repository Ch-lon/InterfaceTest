# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : DataOperation.py
@Author  : Chlon
@Date    : 2025/10/17 14:40
@Desc    : 数据处理的通用操作
"""
import copy
import random
import urllib.parse

class DataOperation:

    def get_value_from_dict(self,dictionary, *keys) -> list:
        """
        从字典中获取多个键的值，并组成一个列表
        Args:
            dictionary: 要查询的字典
            *keys: 一个或多个键名
        Returns:
            list_value: 包含所有键对应值的列表
        """
        #list_value = [dictionary.get(key, None) for key in keys]
        list_value = [dictionary.get(key, f"该键{key}获取失败") for key in keys]
        if len(keys) == 1:
            # 如果只有一个键，确保返回该键对应的值，而不是一个列表,以便后续直接解包
            return list_value[0]
        return list_value

    def format_url(self, url, **kwargs):
        """
        格式化URL，将参数替换为对应的值
        Args:
            url: 要格式化的URL
            **kwargs: 参数字典，顺序与url中的参数一致
        Returns:
            str: 格式化后的URL
        """
        try:
            return url.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"在 {url} 中缺少参数 {kwargs}:{e}")


    def get_copy_key_from_dict(self,dictionary, key):
        """
        从字典中获取键对应的值，并返回键值的副本，键为原字典的键，值为原字典的值
        Args:
            dictionary: 要查询的字典
            key: 要查询的键
        Returns:
            dict: 键值的副本，避免污染原始数据.即与dictionary一样的字典{，，}
        """
        if key not in dictionary:
            raise ValueError(f"字典 {dictionary} 中不存在键 {key}")
        value = dictionary[key]
        #copy.copy() (浅拷贝) 会智能地处理所有类型：
        #对于 list 或 dict，它会创建一个浅拷贝。
        #对于 int 或 str 等不可变类型，它会直接返回原对象（因为没必要复制）。
        return copy.copy(value)

    def url_encode(self, value: str) -> str:
        """
        将文本编码为URL格式
        Args:
            value: 中文文本
        Returns:
            百分号编码结果
        Raises:
            TypeError: 当value不是字符串类型时
            AttributeError: 当value为None时
        """
        if value is None:
            raise AttributeError(f"传入的编码参数 {value} 不能为空！")

        if not isinstance(value, str):
            raise TypeError(f"{value} 必须是字符串类型")

        return urllib.parse.quote(value)

    def get_random_key_and_value_from_dict(self, dict_values: dict):
        """
        从字典中随机获取一个键值对
        Args:
            dict_values: 字典
        Returns:
            str: 随机获取的键和值
        """
        if not dict_values:
            raise ValueError("字典不能为空！")
        key = random.choice(list(dict_values.keys()))
        value = dict_values[key]
        return key, value