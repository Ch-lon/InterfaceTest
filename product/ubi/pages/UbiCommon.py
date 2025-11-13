# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : UbiCommon.py
@Author  : Chlon
@Date    : 2025/8/29 13:49
@Desc    : 国际360测试基类
"""
# InterfaceTest/product/ubi/pages/Login.py
from common.ApiLoader import ApiLoader
from common.path_util import get_absolute_path
from common.logger import get_logger
from common.FileManager import FileManager
from common.DataOperation import DataOperation
import allure


class UbiCommon:
    download_files_path = get_absolute_path('download_files')
    def __init__(self, session):
        super().__init__()
        self.ru = session
        self.fm = FileManager()
        self.do = DataOperation()
        api_path = get_absolute_path("product/ubi/apis/")
        self.al = ApiLoader(api_path)
        self.logging = get_logger(__name__)

    @allure.step("获取当前最新版本信息及排名类型")
    def get_version(self):
        """
        """
        api_config = self.al.get_api('Overview', 'Overview','version')
        # 1. 格式化URL，将路径参数填充进去
        url = api_config['url']
        # 2. 准备查询参数
        #params = api_config.get('default_data', {}).copy()
        #params.update(kwargs)
        headers = api_config.get('headers')
        # 4. 【修改】: 发送请求时，同时传入 params 和 headers
        # params - 将参数放入URL
        # headers - 手动指定Content-Type，即使请求体为空
        response = self.ru.request(
            method=api_config['method'],
            url=url,
            #data=params,
            headers=headers  # 核心改动：将YML中定义的headers传入
        )
        response_json = response.json()
        assert response_json["code"] == api_config["expected"]["code"], f"获取最新版本信息失败，响应信息为：{response_json}"
        verNo = response_json["data"][0]["verNo"]
        rankingTypeId = response_json["data"][0]["rankingTypeId"]
        self.logging.info(f"排名类型为：{rankingTypeId},当前最新版本为：{verNo}")
        return rankingTypeId,verNo

    @allure.step("获取总体定位页面的学校得分及排名相关信息")
    def get_overview_data(self, verNo, rankingTypeId):
        """获取并返回整个概览页面的数据"""
        api_config = self.al.get_api('Overview', 'Overview', 'range')
        origin_url = api_config['url']
        url = self.do.format_url(origin_url,verNo=verNo,rankingTypeId=rankingTypeId)
              # .format(verNo=verNo, rankingTypeId=rankingTypeId))
        response = self.ru.request(
            method=api_config['method'],
            url=url,
            headers=api_config.get('headers')
        )
        response_json = response.json()
        assert response_json["code"] == api_config["expected"]["code"], f"获取总定位数据失败，响应信息为：{response_json}"
        # 同排名区间的学校数据
        ubi_school_data = response_json["data"]["typ"]
        # 本校的数据
        school_data = ubi_school_data["overall"]
        assert response_json["code"] == api_config["expected"]["code"]
        # 获取本校中文名
        school_name = school_data["nameCn"]
        # 获取本校的全球排名
        ranking = int(school_data["ranking"])
        assert ranking > 0, f"{school_name}的全球排名应 > 0,当前排名为：{ranking}"
        # 获取国家/地区排名
        countryRank = int(school_data["countryRank"])
        assert countryRank > 0, f"{school_name}的国家排名应 > 0,当前排名为：{countryRank}"
        # 获取精确得分
        score = float(school_data["score"])
        assert score >= 0, f"{school_name}的精确得分应 >= 0,当前得分为：{score}"
        # 获取发布得分
        pubScore = float(school_data["pubScore"])
        assert pubScore >= 0, f"{school_name}在{verNo}版发布得分应 >= 0,当前得分为：{pubScore}"
        self.logging.info(f"{school_name} 在{verNo}版本中，全球排名为：{ranking},国家/地区排名:{countryRank},精确得得分为：{score},发布得分为：{pubScore}")
        return ubi_school_data

    @allure.step("获取当前院校的同排名区间")
    def get_ranking_range(self, overview_data):
        """从已获取的概览数据中提取排名区间"""
        range_val = overview_data["overall"]["range"]
        self.logging.info(f"当前院校同排名区间为：{range_val}")
        return range_val[0], range_val[1]

    @allure.step("获取当前院校的各指标信息")
    def get_indicators_info(self,rankingTypeId,verNo ) -> list :
        """从已获取的总体定位数据中提取各指标信息"""
        api_indicators = self.al.get_api('Overview', 'Overview', 'indicators_info')
        origin_url = api_indicators['url']
        url = self.do.format_url(origin_url,rankingTypeId=rankingTypeId,verNo=verNo)
        response = self.ru.request(
            method=api_indicators['method'],
            url=url
        )
        response_json = response.json()
        assert response_json["code"] == api_indicators["expected"]["code"], f"指标信息获取失败，响应信息为：{response_json}"
        # 指标信息是个列表
        indicators = response_json["data"]
        all_ind_info: list = self.extract_partial_level_3_data(indicators)
        return all_ind_info

    def extract_partial_level_3_data(self,data_list):
        """
        递归遍历指标对象列表，查找所有 "level": 3 的项，并只提取部分关键数据。
        Args:
            data_list (list): 一个包含字典对象的列表，代表指标。
        Returns:
            list: 一个列表，其中每个元素都是一个包含 level 3 指标部分数据的新字典。类似[{},{},{}]
        """
        level_3_results = []
        def find_recursively(nodes):
            """一个用于执行递归搜索的辅助函数。"""
            if not isinstance(nodes, list):
                return
            for node in nodes:
                if not isinstance(node, dict):
                    continue
                # 当找到 level 为 3 的节点时，执行以下操作
                if node.get("level") == 3:
                    # =================== 修改核心 ===================
                    # 1. 创建一个新的空字典来存放我们想要的数据
                    partial_data = {}
                    # 2. 从原始 node 字典中提取我们需要的字段，并存入新字典
                    #    使用 .get() 方法可以安全地获取数据，即使某个键不存在也不会报错
                    # 指标ID,这里对ID 进行字符串转换，因为作为后续字典的键必须为字符串
                    partial_data['id'] = str(node.get('id',{}))
                    # 指标名
                    partial_data['name'] = node.get('name')
                    # 指标Code
                    partial_data['code'] = node.get('code')
                    # Detail：明细类；val:数值类
                    partial_data['editable'] = node.get('editable')
                    # 指标明细定义ID
                    partial_data['detailDefId'] = node.get('detailDefId')
                    # 是否是排名指标
                    partial_data['isRank'] = node.get('isRank')
                    # 是否进行模拟
                    partial_data['isSim'] = node.get('isSim')
                    # 指标数据
                    partial_data['indData'] = node.get('indData', {})
                    # 安全地提取嵌套在 indData 中的 value
                    # .get('indData', {}) 会在 'indData' 不存在时返回一个空字典，避免了错误
                    # ind_data = node.get('indData', {})
                    # partial_data['value'] = ind_data.get('value', '无数据')
                    # 3. 将这个只包含部分数据的新字典添加到结果列表中
                    level_3_results.append(partial_data)
                    # ===============================================
                # 递归逻辑保持不变
                if "children" in node and node["children"]:
                    find_recursively(node["children"])
                if "refInds" in node and node["refInds"]:
                    find_recursively(node["refInds"])
        find_recursively(data_list)
        self.logging.info(f"共获取 {len(level_3_results)} 个指标信息：{level_3_results}")
        print(f"共获取 {len(level_3_results)} 个指标信息：{level_3_results}")
        return level_3_results


    @allure.step("数据导出相关断言")
    def check_export_response(self,resp, file_type, filename):
        """
        检查数据导出的响应是否符合预期
        :param resp: 响应对象
        :param file_type: 文件类型，如"xlsx"
        :param filename: 文件名
        """
        # 1️⃣ 响应状态码检查
        #assert resp.status_code == 200,f"返回状态码异常,实际响应为：{resp}"
        # 2️⃣ Content-Type 检查，应为二进制流
        ctype = resp.headers.get("Content-Type", "")
        assert "application/octet-stream" in ctype, f"错误的Content-Type: {ctype}"
        # 3️⃣ 文件类型检查，应为Excel
        disposition = resp.headers.get("Content-Disposition", "")
        # disposition输出类似：attachment; filename=Up-To-Date%20Ranking.xlsx
        assert file_type in disposition, f"文件类型错误，应为 {file_type}: {disposition}"
        # 4️⃣ 文件保存检查
        self.fm.clear_directory(self.download_files_path)
        file_path = self.fm.write_binary_file_and_save(resp.content, self.download_files_path, filename)
        assert file_path is not None, "文件未能成功保存"
        # 5️⃣ 检查文件大小是否符合要求（例如，大于1KB）
        file_size = self.fm.get_file_size(file_path)
        # 设定一个合理的最小文件大小阈值，例如1024字节 (1KB)
        # 一个空的Excel文件也占用一定空间，所以这个值通常比0大
        assert file_size > 1 * 1024, f"文件大小 {file_size} 字节, 小于预期的最小值 1 KB"

    @allure.step("指标明细请求")
    def detail_request(self,indValId,verNo,detailDefId):
        api_ind_detail = self.al.get_api('UbiCommon', 'UbiCommon', 'detail_click')
        origin_url = api_ind_detail['url']
        url = self.do.format_url(origin_url,indValId=indValId,verNo=verNo,detailDefId=detailDefId)
        response = self.ru.request(
            method=api_ind_detail['method'],
            url=url,
            #headers=api_ind_detail.get('headers')
        )
        response_json = response.json()
        assert response_json["code"] == api_ind_detail["expected"]["code"], f"{detailDefId} 明细请求失败，响应为:{response_json}"
        return response_json

    @allure.step("多个指标明细点击")
    def detail_click(self,list_ind_data,verNo):
        list_fail_indicators = []
        for dict_indicators in list_ind_data:
            # 列表直接解包到变量
            ind_name, editable, detailDefId, ind_data = self.do.get_value_from_dict(dict_indicators, "name",
                                                                                         "editable", "detailDefId",
                                                                                         "indData")
            # 指标：明细类和数值类
            indValId = self.do.get_value_from_dict(ind_data, "indValId")
            if editable != "val" and indValId != 0 and indValId is not None and detailDefId != 0:
                print(f"指标 {ind_name} 的明细类指标ID为：{indValId}")
                response = self.detail_request(indValId, verNo, detailDefId)
                list_ind_detail = response["data"]["details"]
                # 增加明细弹窗可以打开，但是获取的明细数据为空的情况
                if list_ind_detail is None or len(list_ind_detail) == 0  :
                    list_fail_indicators.append(ind_name)
        assert not list_fail_indicators, f"共有 {len(list_fail_indicators)} 个指标明细请求失败。失败的指标有：{list_fail_indicators}"
