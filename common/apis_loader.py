# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : apis_loader.py
@Author  : Chlon
@Date    : 2025/9/1 11:50
@Desc    : api配置文件处理类
"""
import yaml
from pathlib import Path


class ApiLoader:
    def __init__(self, api_dir):
        # 将API路径转换为 Path 对象存储在 self.api_dir 中
        self.api_dir = Path(api_dir)
        # 创建空字典用于存储 API 信息
        self.apis = {}
        # 加载所有API配置
        self.load_all_apis()

    # def __init__(self):
    #     self.apis = {}

    def load_all_apis(self):

        """加载所有API配置文件"""
        # 查找 api_dir 目录下所有 .yml 文件
        for yaml_file in self.api_dir.glob("*.yml"):
            with open(yaml_file, 'r', encoding='utf-8') as f:
                # 解析YAML内容为Python对象
                api_data = yaml.safe_load(f)
                # 将解析出的API数据更新到 self.apis 字典中
                self.apis.update(api_data)

    def get_api(self, module_name, api_name):
        """
        获取指定API配置
        module_name:页面模块名，如login_cg
        api_name:api名，如login_page
        """
        try:
            # 创建并返回数据副本,避免直接返回原始数据引用，防止外部修改影响原始API配置数据。
            return self.apis[module_name][api_name].copy()
        except KeyError:
            raise ValueError(f"API配置不存在: {module_name}.{api_name}")

    def get_url(self, module_name, api_name, **path_params):
        """获取完整的URL（处理路径参数）"""
        api_config = self.get_api(module_name, api_name)
        url = api_config['url']

        # 替换路径参数
        if path_params:
            url = url.format(**path_params)

        return url

# # 创建全局实例

if __name__=="__main__":
    api_loader = ApiLoader('../product/ubi/apis/')
    print(api_loader.apis)