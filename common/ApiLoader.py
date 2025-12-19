# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : ApiLoader.py
@Author  : Chlon
@Date    : 2025/9/1 11:50
@Desc    : api配置文件处理
"""
from pathlib import Path
from common.FileManager import FileManager
from common.path_util import get_absolute_path


class ApiLoader:
    def __init__(self, api_dir):
        """
        :param api_dir:apis配置文件所在目录，如：InterfaceTest/product/ubi/apis/
        初始化ApiLoader，采用懒加载方式。
        只记录api目录，不立即加载文件。
        """
        self.api_dir = Path(api_dir)
        self.apis = {}
        # 用于记录已经加载过的模块名的集合，防止重复加载
        self._loaded_modules = set()
        self.fm = FileManager()

    def _load_api_file(self, api_file_name):
        """
        加载单个指定的API配置文件。
        如果Overview.py未加载，则会把Overview.py中的配置加载到apis字典中，并把Overview名记录在集合_loaded_modules中；
        如果已加载，则可以直接调用apis字典即可
        :param api_file_name:配置文件名，如需要加载Overview.py配置文件，只需输入Overview
        """
        # 如果该模块已经加载过，则直接返回，避免重复IO操作
        if api_file_name in self._loaded_modules:
            return
        # 构建对应的.yml文件路径
        yaml_file_path = self.api_dir / f"{api_file_name}.yml"
        # 检查文件是否存在
        if not yaml_file_path.exists():
            # 如果文件不存在，则不执行任何操作
            # 在 get_api 中会因为找不到 key 而自然报错
            return
        # 打开并加载YAML文件,yaml_file_path是path对象需要转换为str
        api_data = self.fm.load_yaml_file(str(yaml_file_path))
        # 将解析出的API数据更新到 self.apis 字典中
        self.apis.update(api_data)
        # 将模块名添加到已加载集合中
        self._loaded_modules.add(api_file_name)

    def get_api(self, api_file_name,module_name, api_name):
        """
        获取指定API配置。
        如果对应的模块配置尚未加载，则先触发加载。
        :param api_file_name:配置文件名，如需要加载Overview.py配置文件，只需输入Overview
        :param module_name:具体配置文件中的模块名，如Overview.py中的Overview
        :param api_name;module_name中的具体api名，如Overview.py-Overview中的version
        """
        # 1. 检查所需模块是否已存在于apis字典中
        if api_file_name not in self._loaded_modules:
            # 2. 如果不存在，尝试加载对应的.yml文件
            self._load_api_file(api_file_name)

        # 3. 再次检查并获取API配置
        try:
            # 创建并返回数据副本,避免直接返回原始数据引用
            return self.apis[module_name][api_name].copy()
        except KeyError:
            # 如果加载后依然找不到，说明配置确实不存在
            raise ValueError(f"API配置 {api_file_name}.yml 中不存在: {module_name}.{api_name}")

    def get_url(self,api_file_name, module_name, api_name, **path_params):
        """获取完整的URL（处理路径参数）"""
        api_config = self.get_api(api_file_name,module_name, api_name)
        url = api_config['url']
        # 替换路径参数
        if path_params:
            url = url.format(**path_params)
        return url

# # 创建全局实例

if __name__=="__main__":
    path = get_absolute_path("product/ubi/apis/")
    print(path)
    api_loader = ApiLoader(path)
    print(api_loader.api_dir)
    x= api_loader.get_api('Overview', 'Overview','version')
    y = x.get("description")
    print(x,y)
