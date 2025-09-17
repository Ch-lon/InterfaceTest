import os
import yaml

class FileManager:
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


    def load_yaml_file(self,filepath):
        """
        加载 YAML 文件。
        Args:
            filepath (str): 要加载的 YAML 文件路径。
        Returns:
            dict: 加载的 YAML 文件内容。
        """
        try:
            with open(filepath, encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"文件 '{filepath}' 不存在")
        except yaml.YAMLError as e:
            print(f"加载 YAML 文件 '{filepath}' 时出错: {e}")
