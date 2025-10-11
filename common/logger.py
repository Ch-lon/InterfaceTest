import logging, os
from datetime import datetime
from common.path_util import get_absolute_path
from common.FileManager import FileManager
def get_logger(name="接口自动化测试"):
    # 获取一个指定名称的日志器
    logger = logging.getLogger(name)
    """
    设置日志器处理的最低级别为INFO
    日志级别从低到高：DEBUG < INFO < WARNING < ERROR < CRITICAL
    设置为INFO表示会记录INFO及更高级别（WARNING、ERROR等）的日志
    """
    logger.setLevel(logging.DEBUG)
    #log_path = get_absolute_path("../logs/test.log")
    # 如果日志器所有的处理器列表为空，则添加处理器
    if not logger.handlers:

        # --- 动态生成日志文件名 ---
        # 1. 获取当前日期并格式化
        today = datetime.now().strftime("%Y-%m-%d")
        # 2. 拼接日志文件名
        log_file_name = f"{today}.log"
        # 3. 获取日志文件的绝对路径
        log_path = get_absolute_path(f"logs/{log_file_name}")

        # --- 修改结束 ---
        # 确保日志目录存在
        # os.path.dirname() 函数从完整的日志文件路径 log_path 中提取出目录部分
        # 即D:\PycharmProject\InterfaceTest\logs
        log_dir = os.path.dirname(log_path)
        fm = FileManager()
        fm.create_directory_if_not_exists(log_dir)
        # 创建一个文件处理器，将日志写入到文件：encoding="utf-8"：指定文件编码为UTF-8，确保中文正常显示
        fh = logging.FileHandler(log_path, encoding="utf-8")
        # 创建一个流处理器，将日志输出到控制台（标准输出）：既可以输出到文件，也可以输出到控制台
        sh = logging.StreamHandler()
        # 定义日志的输出格式：[2023-10-27 14:30:25,123] INFO: 用户登录成功
        formatter = logging.Formatter("[%(asctime)s] [%(module)s] %(levelname)s: %(message)s")
        # 确保文件和控制台的日志格式一致
        fh.setFormatter(formatter)
        sh.setFormatter(formatter)
        # 将两个处理器添加到日志器中
        logger.addHandler(fh)
        logger.addHandler(sh)
    return logger

if __name__ == '__main__':
    log_path = get_absolute_path("../config/settings.json")
    print(log_path)