import os
from typing import Any
import yaml
import shutil
import allure
import time
import pytest


class FileManager:

    @allure.step("加载 YAML 文件")
    def load_yaml_file(self,filepath : str)-> Any | None:
        """
        加载 YAML 文件。
        Args:
            filepath (str): 要加载的 YAML 文件路径。
        Returns:
            dict: 加载的 YAML 文件内容。
        """
        try:
            with open(filepath,"r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"文件 '{filepath}' 不存在")
        except yaml.YAMLError as e:
            print(f"加载 YAML 文件 '{filepath}' 时出错: {e}")

    @allure.step("如果文件夹不存在，则创建，否则忽略")
    def create_directory_if_not_exists(self,filepath):
        """
        使用 os.makedirs 的 exist_ok 参数来创建文件夹，如果已存在则忽略。
        Args:
            filepath (str): 要创建的文件夹路径。
        """
        try:
            os.makedirs(filepath, exist_ok=True)
        except OSError as e:
            print(f"创建文件夹 '{filepath}' 时出错: {e}")

    @allure.step("检查文件是否存在")
    def check_file_exists(self,file_path: str,timeout = 10):
        """
        在指定时间内轮询检查文件是否存在。
        Args:
            file_path (str): 要检查的文件的完整路径。
            timeout (int): 最大等待时间（秒）。默认为10秒。
        Returns:
            bool: 如果文件在超时前存在，则返回 True，否则返回 False。
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if os.path.exists(file_path):
                return True
            time.sleep(0.5)  # 每隔0.5秒检查一次，避免CPU占用过高
        pytest.fail(f"在 {timeout} 秒后仍未找到文件: {file_path}")
        return False

    @allure.step("清空指定目录下的所有文件")
    def clear_directory(self,directory_path:str):
        """
        清空指定目录下的所有文件。
        Args:
            directory_path (str): 要清空的目录路径。
        """
        self.create_directory_if_not_exists(directory_path)
        for filename in os.listdir(directory_path):
            filepath = os.path.join(directory_path, filename)
            try:
                if os.path.isfile(filepath) or os.path.islink(filepath):
                    os.unlink(filepath)
                elif os.path.isdir(filepath):
                    shutil.rmtree(filepath)
            except Exception as e:
                print(f"清空目录 '{directory_path}' 时出错: {e}")

    @allure.step("将二进制内容写入文件，并保存到指定路径下")
    def write_binary_file_and_save(self, response_content : bytes, download_dir:str, file_name:str):
        """
        将二进制内容保存为文件。
        Args:
            response_content (bytes): 接口返回的二进制内容。一般为response.content
            download_dir (str): 要保存到的文件夹路径。
            file_name (str): 文件名,需要指定一个带文件类型后缀的命名。如：总体定位.xlsx。
        Returns:
            str: 完整的该文件路径。
        """
        # 移入函数内部，避免模块级循环导入，因为logger中也导入FileManager
        from common.logger import get_logger
        logging = get_logger(__name__)
        # 确保目录存在
        #self.create_directory_if_not_exists(download_dir)
        # 创建文件的路径
        file_path = os.path.join(download_dir, file_name)
        # 将二进制内容写入文件
        try:
            with open(file_path, 'wb') as f:
                f.write(response_content)
            self.check_file_exists(file_path)
            logging.info(f"文件已成功保存到: {file_path}")
            return file_path
        except Exception as e:
            logging.error(f"保存文件时出错: {e}")
            return None

    @allure.step("获取文件的大小")
    def get_file_size(self,file_path:str):
        """
        获取文件的大小。
        Args:
            file_path (str): 完整文件路径。
        Returns:
            int: 文件大小（字节）。
        """
        try:
            return os.path.getsize(file_path)
        except FileNotFoundError:
            print(f"文件 '{file_path}' 不存在")
        except Exception as e:
            print(f"获取文件大小时出错: {e}")
