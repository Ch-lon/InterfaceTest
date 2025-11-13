# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : simulate.py
@Author  : Chlon
@Date    : 2025/11/10 17:36
@Desc    : 排名推演
"""
import allure
from product.ubi.pages.UbiCommon import UbiCommon

class Simulate(UbiCommon):

    @allure.step("排名推演指标体系")
    def simulate_indicators(self, rankingTypeId, verNo):
        api_simulate_indicators = self.al.get_api('simulate', 'simulate', 'simulate_indicators')
        url = self.do.format_url(api_simulate_indicators['url'],rankingTypeId=rankingTypeId,verNo=verNo)
        response = self.ru.request(
            method=api_simulate_indicators['method'],
            url=url,
            headers=api_simulate_indicators.get('headers')
        )
        response_json = response.json()
        assert response_json["code"] == api_simulate_indicators["expected"]["code"], f"排名推演指标请求失败！请求响应:{response_json}"
        # 指标信息是个列表
        indicators = response_json["data"]
        all_ind_info: list = self.extract_partial_level_3_data(indicators)
        return all_ind_info

    @allure.step("从排名推演指标体系中获取排名指标")
    def get_rank_indicators(self, list_ind_info:list ) -> list:
        """
        从排名推演指标体系中获取排名指标
        :param list_ind_info: 获取的总的指标体系
        :return: 一个列表，包含所有排名指标Id
        """
        list_rank_indicators = []
        for dict_ind_info in list_ind_info:
            indId, name,isRank = self.do.get_value_from_dict(dict_ind_info, "id", "name", "isRank")
            if isRank:
                list_rank_indicators.append(indId)
        return list_rank_indicators

    @allure.step("排名推演指标默认页面数据获取")
    def simulate_default_data_request(self, rankingTypeId, verNo):
        api_simulate_default_data = self.al.get_api('simulate', 'simulate', 'origin_simulate_data')
        url = self.do.format_url(api_simulate_default_data['url'], rankingTypeId=rankingTypeId, verNo=verNo)
        response = self.ru.request(
            method=api_simulate_default_data['method'],
            url=url,
            headers=api_simulate_default_data.get('headers')
        )
        response_json = response.json()
        assert response_json["code"] == api_simulate_default_data["expected"]["code"], f"排名推演指标默认数据请求失败！请求响应:{response_json}"
        return response_json["data"]

    # @allure.step("排名推演指标初始数据")
    # def simulate_default_data(self, dict_default_data: dict)-> dict:


    @allure.step("获取排名推演页面指标默认的indId和val值，用于模拟参数")
    def get_simulate_ind_indId_val(self, list_ind_info) -> dict:
        """
        获取排名推演页面指标默认的indId和val值，用于模拟参数
        :param list_ind_info: 获取的总的指标体系
        :return: 一个字典，用于推演的参数：形式如：{"list":[{}，{}，{}。。。],"suffix": "Typ"}
        """
        # 存放整个参数的字典，需要加默认值"suffix": "Typ"
        dict_param : dict = {"suffix": "Typ"}
        # 存放每个指标的indId和val的列表，最后添加到dict_param中
        list_simulate_ind_indId_val = []
        # 循环指标体系（体系中有指标默认值）
        for dict_ind_info in list_ind_info:
            indId,indData = self.do.get_value_from_dict(dict_ind_info, "id", "indData")
            # 获取指标默认值
            val = self.do.get_value_from_dict(indData, "value")
            # 存放每个指标的indId和val
            dict_ind_indId_val = {"indId": int(indId), "val": val}
            # 添加到列表中
            list_simulate_ind_indId_val.append(dict_ind_indId_val)
        self.logging.info(f"共获取排名推演页面{len(list_simulate_ind_indId_val)}个指标默认的indId和val值，用于模拟参数为：{list_simulate_ind_indId_val}")
        dict_param.update({"list": list_simulate_ind_indId_val})
        return dict_param

    @allure.step("排名推演模拟")
    def simulate_request(self, rankingTypeId, verNo, dict_param):
        api_simulate = self.al.get_api('simulate', 'simulate', 'simulate_with_param')
        url = self.do.format_url(api_simulate['url'], rankingTypeId=rankingTypeId, verNo=verNo)
        response = self.ru.request(
            method=api_simulate['method'],
            url=url,
            json=dict_param,
            headers=api_simulate.get('headers')
        )
        response_json = response.json()
        assert response_json["code"] == api_simulate["expected"]["code"], f"排名推演模拟请求失败！请求响应:{response_json}"
        return response_json["data"]

    @allure.step("使用默认参数进行排名推演，得出默认推演结果")
    def simulate_default_data(self, list_ind_info,rankingTypeId, verNo) -> dict:
        """
        使用默认参数进行排名推演，得出默认推演结果
        :param rankingTypeId: 排行榜类型id
        :param verNo: 排行榜版本号
        :return:一个字典，包含当前模拟结果的得分和排名，以及各排名指标的模拟得分:{,,,,}
        """
        # 初始值
        dict_default_data = self.simulate_default_data_request(rankingTypeId, verNo)
        # 默认的univ字典部分
        dict_univ_default_data = self.do.get_value_from_dict(dict_default_data, "univ")
        # 默认的indScore字典部分
        dict_indScore = dict_default_data["indScore"]
        # 初始得分与排名
        init_score, init_rank = self.do.get_value_from_dict(dict_univ_default_data, "score", "rank")
        # 存放初始得分与排名的字典
        dict_init_data = ({"score": init_score, "rank": init_rank})
        list_rank_inds = self.get_rank_indicators(list_ind_info)
        for ind in list_rank_inds:
            # 初始结果
            init_value = self.do.get_value_from_dict(dict_indScore, ind)
            dict_init_data.update({ind: init_value})
        return dict_init_data

    @allure.step("获取10个大学联盟code")
    def get_univ_alliance_code_request(self,suffix,rankingTypeId)-> list :
        """
        获取10个大学联盟code
        :return:[{},{},{}...]
        """
        # 存放大学联盟code
        list_univ_alliance_code = []
        api_univ_alliance = self.al.get_api('simulate', 'simulate', 'univ_alliance')
        origin_url = api_univ_alliance['url']
        url = self.do.format_url(origin_url, suffix=suffix,rankingTypeId=rankingTypeId)
        response = self.ru.request(
            method=api_univ_alliance['method'],
            url=url,
            headers=api_univ_alliance.get('headers')
        )
        response_json = response.json()
        assert response_json["code"] == api_univ_alliance["expected"]["code"], f"大学联盟code请求失败！请求响应:{response_json}"
        # 从每个大学联盟中获取对应code
        list_all_univ_alliance = response_json["data"]["list"]
        for dict_univ_alliance in list_all_univ_alliance:
            code = self.do.get_value_from_dict(dict_univ_alliance, "code")
            list_univ_alliance_code.append(code)
        return list_univ_alliance_code

    @allure.step("获取10个大学联盟中单个默认数据")
    def get_univ_alliance_default_param_request(self,rankingTypeId,verNo,code)-> dict:
        """
        获取10个大学联盟中单个数据
        :param rankingTypeId: 排行榜类型id
        :param verNo: 排行榜版本号
        :param code:大学联盟code
        :return:一个字典，包含当前模拟结果的得分和排名，以及各排名指标的模拟得分:{"16424":{},"16425":{},}
        """
        api_univ_alliance_default_param = self.al.get_api('simulate', 'simulate', 'univ_alliance_default_param')
        url = self.do.format_url(api_univ_alliance_default_param['url'], rankingTypeId=rankingTypeId, verNo=verNo,bg=code)
        response = self.ru.request(
            method=api_univ_alliance_default_param['method'],
            url=url,
            headers=api_univ_alliance_default_param.get('headers')
        )
        response_json = response.json()
        assert response_json["code"] == api_univ_alliance_default_param["expected"]["code"], f"大学联盟 {code} 默认数据请求失败！请求响应:{response_json}"
        dict_ind_data = response_json["data"]["ind"]
        return dict_ind_data

    @allure.step("将单个大学联盟的响应数据转换成可以被用于模拟请求的参数")
    def switch_simulate_ind_indId_val(self,list_ind_info, dict_ind_data: dict) -> dict:
        """
        将单个大学联盟的响应数据转换成可以被用于模拟请求的参数
        :param list_ind_info:指标体系
        :param dict_ind_data:大学联盟响应数据,response_json["data"]["ind"]部分,即{"16424":{},"16425":{},}
        :return:一个字典，用于推演的参数：形式如：{"list":[{}，{}，{}。。。],"suffix": "Typ"}
        """
        # 存放整个参数的字典，需要加默认值"suffix": "Typ"
        dict_param: dict = {"suffix": "Typ"}
        # 存放每个指标的indId和val的列表，最后添加到dict_param中
        list_simulate_ind_indId_val = []
        for dict_ind_info in list_ind_info:

            indId, indData = self.do.get_value_from_dict(dict_ind_info, "id", "indData")
            # 获取指标默认值
            init_val = self.do.get_value_from_dict(indData, "value")

            # 获取模拟值
            sim_val = self.do.get_value_from_dict(dict_ind_data[f"{indId}"], "avgVal")
            # 存放每个指标的indId和val
            values = [v for v in [init_val, sim_val] if v is not None]
            dict_ind_indId_val = {
                "indId": int(indId),
                "val": max(values) if values else 0  # 如果都为None则使用默认值0
            }
            # 添加到列表中
            list_simulate_ind_indId_val.append(dict_ind_indId_val)

        dict_param.update({"list": list_simulate_ind_indId_val})
        return dict_param

    @allure.step("将模拟的结果重新提取成一个字典")
    def switch_simulate_result(self, dict_result: dict,list_rank_indicators:list) -> dict:
        """
        将模拟的结果重新提取成一个字典
        :param dict_result:模拟结果,response_json["data"]
        :param list_rank_indicators:排名指标Id
        :return:一个字典，包含当前模拟结果的得分和排名，以及各排名指标的模拟得分:{"16424":{},"16425":{},}
        """
        # univ部分
        score,rank = self.do.get_value_from_dict(dict_result["univ"], "score","rank")
        dict_univ = {"score": score, "rank": rank}
        dict_inds = self.do.get_value_from_dict(dict_result, "inds")
        for rank_ind in list_rank_indicators:
            dict_ind = dict_inds[f"{rank_ind}"]
            finalScore = self.do.get_value_from_dict(dict_ind, "finalScore")
            dict_univ.update({rank_ind: round(finalScore, 1)})
        return dict_univ

    @allure.step("排名推演数据导出请求")
    def request_data_export(self,list_ind_info,rankingTypeId,verNo) -> bytes:
        # 获取默认参数
        dict_default_param = self.get_simulate_ind_indId_val(list_ind_info)
        # 移除默认参数中的"suffix"，# 第二个参数是默认值，防止KeyError。pop():移除并返回被删除的值
        dict_default_param.pop("suffix",None)
        # 构造数据导出请求的参数
        # update（）后不能直接赋值，会返回None，如x= {}.update({}),x会变成None
        dict_default_param.update(
            {"target1Param": {
                "bg": "",
                "start": 1,
                "end": 100,
                "regionId": 0,
                "countryId": 0,
                "target": 0
            },
            "target2Param": {
                "bg": "IVY_LEAGUE",
                "start": 0,
                "end": 0,
                "regionId": 0,
                "countryId": 0,
                "target": 0
            },
            "target3Param": {
                "bg": "985",
                "start": 0,
                "end": 0,
                "regionId": 0,
                "countryId": 0,
                "target": 0
            }})
        param = dict_default_param
        print(f"数据导出请求参数为：{param}")
        api_data_export = self.al.get_api('simulate', 'simulate', 'data_export')
        url = self.do.format_url(api_data_export['url'], rankingTypeId=rankingTypeId, verNo=verNo)
        response = self.ru.request(
            method=api_data_export['method'],
            url=url,
            json = param,
            headers=api_data_export.get('headers')
        )
        assert response.status_code == api_data_export["expected"]["code"], f"排名推演数据导出请求失败！请求响应:{response.text}"
        return response