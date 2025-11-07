# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : DevelopTrend.py
@Author  : Chlon
@Date    : 2025/10/21 13:12
@Desc    : 排名趋势类
"""

from product.ubi.pages.UbiCommon import UbiCommon
import allure

class DevelopTrend(UbiCommon):
    # def __init__(self, session):
    #     super().__init__(session)

    @allure.step("获取排名趋势页当前版本的指标体系")
    def get_developtrend_indicators(self, rankingTypeId, verNo):
        """
        获取排名趋势页当前版本的指标体系
        :param rankingTypeId: 排行榜类型id
        :param verNo: 排行榜版本号
        :return:类似[{},{},{}]
        """
        api_dt_indicators = self.al.get_api('DevelopTrend', 'DevelopTrend', 'developtrend_indicators')
        origin_url = api_dt_indicators['url']
        url = self.do.format_url(origin_url,rankingTypeId=rankingTypeId,verNo=verNo)
        response = self.ru.request(
            method=api_dt_indicators['method'],
            url=url,
            headers=api_dt_indicators.get('headers')
        )
        response_json = response.json()
        assert response_json["code"] == api_dt_indicators["expected"]["code"], f"排名趋势页指标体系请求失败！请求响应:{response_json}"
        # 指标信息是个列表
        indicators = response_json["data"]
        all_ind_info: list = self.extract_partial_level_3_data(indicators)
        return all_ind_info

    @allure.step("获取学校当前版本与对比版本的数据")
    def get_developtrend_data(self, rankingTypeId, verNo,compareVerNo):
        """
        获取学校排名趋势页指标数据
        :param rankingTypeId: 排行榜类型id
        :param verNo: 排行榜版本号
        :return:
        """
        api_developtrend = self.al.get_api('DevelopTrend', 'DevelopTrend', 'indicators_data')
        origin_url = api_developtrend['url']
        url = self.do.format_url(origin_url,rankingTypeId=rankingTypeId,verNo=verNo,compareVerNo=compareVerNo)
        response = self.ru.request(
            method=api_developtrend['method'],
            url=url,
            headers=api_developtrend.get('headers')
        )
        res = response.json()
        assert res["code"] == api_developtrend["expected"]["code"], f"排名趋势页请求失败！请求响应:{res}"
        return res["data"]["rankType"]

    @allure.step("获取指标当前版本与比对版本的得分与排名，并组成一个字典")
    def get_ind_rank_and_score(self,dictionary, key) ->  dict:
        """获取指定键的排名信息"""
        if key not in dictionary:
            raise ValueError(f"字典 {dictionary} 中不存在键 {key}")

        item = dictionary[key]
        return {
            'rank': item.get('rank'),
            'rankComp': item.get('rankComp'),
            'score': item.get('score'),
            'scoreComp': item.get('scoreComp'),
        }

    @allure.step("图片下载校验")
    def check_image_download(self):
        """
        图片下载校验
        """
        api_image_download = self.al.get_api('DevelopTrend', 'DevelopTrend', 'image_download')
        origin_url = api_image_download['url']
        response = self.ru.request(
            method=api_image_download['method'],
            url=origin_url,
            headers=api_image_download.get('headers')
        )
        assert response.status_code == api_image_download["expected"]["code"], f"图片下载请求失败！请求响应:{response.text}"
        return response

    @allure.step("对比分析-数据导出校验")
    def data_export(self,rankingTypeId,verNo,compareVerNo):
        """
        对比分析-数据导出校验
        """
        api_export_data = self.al.get_api('DevelopTrend', 'DevelopTrend', 'data_export')
        origin_url = api_export_data['url']
        url = self.do.format_url(origin_url,rankingTypeId=rankingTypeId,verNo=verNo,compareVerNo=compareVerNo)
        response = self.ru.request(
            method=api_export_data['method'],
            url=url,
            headers=api_export_data.get('headers')
        )
        assert response.status_code == api_export_data["expected"]["code"], f"名次对比数据导出请求失败！实际请求响应:{response}"
        return response

    @allure.step("趋势分析数据请求")
    def request_rankingAnalysis(self,indId,verNo,compUnivCode):
        """
        趋势分析数据请求
        """
        api_rankingAnalysis = self.al.get_api('DevelopTrend', 'DevelopTrend', 'rankingAnalysis')
        url = api_rankingAnalysis['url']
        params = self.do.get_copy_key_from_dict(api_rankingAnalysis, 'data')
        params.update(
            {
            "indId":int(indId),
            "verNo":verNo,
            "compUnivCode":compUnivCode
            }
        )
        response = self.ru.request(
            method=api_rankingAnalysis['method'],
            url=url,
            json=params,
            headers=api_rankingAnalysis.get('headers')
        )
        response_json = response.json()
        assert response_json["code"] == api_rankingAnalysis["expected"]["code"], f"趋势分析数据请求失败！请求响应:{response_json}"
        # 指标趋势分析data部分是个列表
        return response_json["data"]


    @allure.step("排名趋势-对比分析：指标排名展示形式是否为N+")
    def check_indicators_rank_form(self,list_ind_data,rankingTypeId,verNo,compareVerNo):
        dt_indicators_data = self.get_developtrend_data(rankingTypeId, verNo, compareVerNo)
        # 该院校当前版本与对比版本的总得分与排名
        rank, rankComp, score, scoreComp = self.do.get_value_from_dict(dt_indicators_data, "rank", "rankComp",
                                                                            "score", "scoreComp")
        print(f"院校 {verNo} 版本下得分:{score}，排名:{rank}，对比 {compareVerNo} 版本下得分:{scoreComp}，排名:{rank}")
        # 该院校当前版本与对比版本的指标数据
        dict_univ_compare_details_data = dt_indicators_data["detail"]
        # self.logging.info(f"院校 {verNo} 获取的指标数据:{dict_univ_compare_details_data}")
        # 创建一个失败列表,用于存放排名形式不正确的指标
        list_fail_verNo = []
        list_fail_compareVerNo = []
        for dict_indicators in list_ind_data:
            # 列表直接解包到变量
            ind_id, ind_name = self.do.get_value_from_dict(dict_indicators, "id", "name")
            dict_ind_rand_data = self.get_ind_rank_and_score(dict_univ_compare_details_data, ind_id)
            rank, rankComp = self.do.get_value_from_dict(dict_ind_rand_data, "rank", "rankComp")
            # if rank == "318+":print(f"指标 {ind_name} 在 {verNo} 获取的排名为 {rank}，应该为N+")
            if rank in ["0", "0+"]: list_fail_verNo.append(ind_name)
            if rankComp in ["0", "0+"]: list_fail_compareVerNo.append(ind_name)
        # 断言验证结果
        error_messages = []
        if list_fail_verNo:
            error_messages.append(
                f"在 {verNo} 版本下，趋势分析-名次对比共有 {len(list_fail_verNo)} 个指标"
                f"排名形式不正确：{list_fail_verNo}"
            )
        if list_fail_compareVerNo:
            error_messages.append(
                f"在 {compareVerNo} 版本下，趋势分析-名次对比共有 {len(list_fail_compareVerNo)} 个指标"
                f"排名形式不正确：{list_fail_compareVerNo}"
            )
        if error_messages:
            # 使用"\n".join()将多个错误信息合并为一个多行字符串
            raise AssertionError("\n".join(error_messages))

    @allure.step("对比分析-对比版本的明细点击校验")
    def check_compare_detail_click(self,list_ind_info,rankingTypeId,verNo,compareVerNo):
        """
        对比分析-对比版本的明细点击校验
        """
        # 全部指标信息:[{},{},{}]
        # 一个包含当前版本和对比版本的指标信息字典
        dict_verNo_and_comp_ind_data = self.get_developtrend_data(rankingTypeId, verNo, compareVerNo)
        # 获取detail部分：
        dict_verNo_and_comp_ind_data_detail = self.do.get_value_from_dict(dict_verNo_and_comp_ind_data, 'detail')
        assert dict_verNo_and_comp_ind_data_detail is not None, "排名趋势-对比分析无法找到各指标数据！"

        # 存放当前版本明细请求失败的列表
        list_fail_ind_data = []
        # 存放对比版本明细请求失败的列表
        list_fail_comp_ind_data = []
        # 循环点击当前版本和对比版本的指标明细
        for dict_ind_info in list_ind_info:
            # 从全部指标信息中获取每个指标id
            ind_id,ind_name = self.do.get_value_from_dict(dict_ind_info, 'id',"name")
            # 根据ind_id从detail中获取每个指标的数据
            dict_ind_data = self.do.get_value_from_dict(dict_verNo_and_comp_ind_data_detail, ind_id)
            # 每个指标当前版本和对比版本的indVal(detail->indVal->indValId)
            dict_ind_indVal = self.do.get_value_from_dict(dict_ind_data, 'indVal')
            dict_ind_indValComp = self.do.get_value_from_dict(dict_ind_data, 'indValComp')

            # 获取当前版本的indValId和indDetailDefId，这2个参数用于明细接口请求
            indValId = self.do.get_value_from_dict(dict_ind_indVal, 'indValId')
            indDetailDefId = self.do.get_value_from_dict(dict_ind_indVal, 'indDetailDefId')
            if indValId != 0 and indDetailDefId != 0:
                print(f"点击指标 {ind_name}")
                response = self.detail_request(indValId, verNo, indDetailDefId)
                list_ind_detail = response["data"]["details"]
                # 增加明细弹窗可以打开，但是获取的明细数据为空的情况
                if response["code"] != 200 or list_ind_detail is None or len(list_ind_detail) == 0 :
                    list_fail_ind_data.append(ind_name)

            # 获取对比版本的indValId和indDetailDefId,并请求明细接口
            indValIdComp = self.do.get_value_from_dict(dict_ind_indValComp, 'indValId')
            indDetailDefIdComp = self.do.get_value_from_dict(dict_ind_indValComp, 'indDetailDefId')
            if indValIdComp != 0 and indDetailDefIdComp != 0:
                print(f"点击对比版本指标 {ind_name}")
                response_comp = self.detail_request(indValIdComp, compareVerNo, indDetailDefIdComp)
                list_ind_detail_comp = response_comp["data"]["details"]
                # 添加对比版本明细请求失败的指标
                if response_comp["code"] != 200 or list_ind_detail_comp is None or len(list_ind_detail_comp) == 0:
                    list_fail_comp_ind_data.append(ind_name)

        list_all_fail_ind_data = []
        if list_fail_ind_data:
            list_all_fail_ind_data.append(
                f"{verNo} 版本共有 {len(list_fail_ind_data)} 个指标明细请求失败！失败的指标为：{list_fail_ind_data}"
            )
        if list_fail_comp_ind_data:
            list_all_fail_ind_data.append(
                f"{compareVerNo} 版本共有 {len(list_fail_comp_ind_data)} 个指标明细请求失败！失败的指标为：{list_fail_comp_ind_data}"
            )
        if list_all_fail_ind_data:
            raise AssertionError("\n".join(list_all_fail_ind_data))

    @allure.step("趋势分析-每个指标版本数据排名提取")
    def get_ind_data_from_version(self,univData : list,verNo,ind_name):
        """
        获取每个指标的版本数据排名
        """
        # 使用集合避免重复
        set_fail_ind_rank = set()
        for dict_univ_data in univData:
            univCode,score,rankType = self.do.get_value_from_dict(dict_univ_data, 'univCode',"score","rankType")
            print("rankType:",rankType)
            print(f"{univCode}的指标'{ind_name}'在{verNo}版本下的得分为{score},排名为{rankType} ")
            if rankType in ["0", "0+",None]:
                set_fail_ind_rank.add(f"{ind_name}（{univCode},{verNo}）")
        return set_fail_ind_rank

    @allure.step("趋势分析-每个指标对比版本的数据请求校验")
    def all_ind_rankingAnalysis(self,list_ind_info,verNo,compUnivCode):
        """
        请求不同指标的对比数据
        """
        # 增加一个“整体趋势”
        list_ind_info.append({"id":0,"name": "整体趋势","editable":"val"})
        # 存放请求失败的指标列表
        list_fail_ind_data = []
        set_fail_ind_rank = set()
        for dict_ind_info in list_ind_info:
            ind_id,ind_name,editable = self.do.get_value_from_dict(dict_ind_info, 'id',"name","editable")
            if editable in("val", "detail"):
                print(f"请求指标 {ind_name}")
                list_ind_comp_data = self.request_rankingAnalysis(ind_id,verNo,compUnivCode)
                if list_ind_comp_data is None or len(list_ind_comp_data) == 0:
                    list_fail_ind_data.append(ind_name)

                for dict_ind_comp_data in list_ind_comp_data:
                    # 获取每个对比的版本
                    all_verNo = self.do.get_value_from_dict(dict_ind_comp_data, 'verNo')
                    univData = dict_ind_comp_data["univData"]
                    # 避免每次调用get_ind_data_from_version()都会把set_fail_ind_rank之前的数据给覆盖
                    current_fail_set = self.get_ind_data_from_version(univData, all_verNo, ind_name)
                    set_fail_ind_rank.update(current_fail_set)

        list_all_fail_ind_data = []
        if list_fail_ind_data:
            list_all_fail_ind_data.append(
                f"{verNo} 版本下,排名趋势-趋势分析共有 {len(list_fail_ind_data)} 个指标请求失败！失败的指标为：{list_fail_ind_data}"
            )
        if set_fail_ind_rank:
            list_all_fail_ind_data.append(
                f"{verNo} 版本下,排名趋势-趋势分析共有 {len(set_fail_ind_rank)} 个指标数据排名形式错误！错误的指标及版本为：{set_fail_ind_rank}"
            )
        assert not list_all_fail_ind_data, "\n".join(list_all_fail_ind_data)

