# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : report_center.py
@Author  : Chlon
@Date    : 2025/11/17 11:16
@Desc    : 报告中心
"""

import allure,time
from common.path_util import get_absolute_path
from product.ubi.pages.UbiCommon import UbiCommon

class ReportCenter(UbiCommon):

    @allure.step("报告列表请求")
    def report_list_request(self,reportType) -> list[dict]:
        """
        获取报告列表
        :param reportType:报告类型
        :return 多个报告列表
        """
        api_report_list = self.al.get_api('report_center', 'report_center', 'report_list')
        url = api_report_list['url']
        payload = self.do.get_copy_key_from_dict(api_report_list, "payload")
        payload.update(
            {
                "reportLang": "zh-CN",
                "reportType": reportType
            }
        )
        response = self.ru.request(
            method=api_report_list['method'],
            url=url,
            headers=api_report_list.get('headers'),
            json = payload
        )
        response_json = response.json()
        assert response_json["code"] == api_report_list["expected"]["code"], f"报告列表请求失败，请求响应:{response_json}"
        return response_json["data"]

    @allure.step("报告详情请求")
    def report_request(self, report_id) :
        """
        获取报告详情
        """
        api_report_path = self.al.get_api('report_center', 'report_center', 'report_path')
        url = self.do.format_url(api_report_path['url'],id=report_id)

        response = self.ru.request(
            method=api_report_path['method'],
            url=url,
            headers=api_report_path.get('headers'),
        )
        response_json = response.json()
        assert response_json["code"] == api_report_path["expected"]["code"], f"报告详情请求失败，请求响应:{response_json}"
        return response_json["data"]

    @allure.step("上传报告图片")
    def upload_report_images(self):
        """
        上传报告图片
        """
        api_images_upload = self.al.get_api('report_center', 'report_center', 'upload_images')
        url = api_images_upload['url']
        # 4. 关键步骤：处理 Files
        files = self.do.get_copy_key_from_dict(api_images_upload, "files")
        # 【核心变量】用于存储每一次上传的响应结果
        list_OverViewImgUrls = []
        # 2. 开始循环：一个文件发一次请求
        form_field_key = files['field_name']
        for index, item in enumerate(files['items']):
            file_path = get_absolute_path(item['file_path'])
            print(f"[{index + 1}] 获取文件绝对路径: {file_path}")
            v_name = item['virtual_name']
            print(f"[{index + 1}] 正在上传: {v_name} ...")
            # 打开文件 (使用 with 确保单次请求后文件立即关闭)
            try:
                with open(file_path, 'rb') as f_obj:
                    # 构造单个文件的 payload
                    # 字典结构: {'files': ('文件名', 文件对象, '类型')}
                    current_files = {
                        form_field_key: (v_name, f_obj, item['mime_type'])
                    }
                    print(f"    -> 构造 payload: {current_files}")
                    # 发送请求
                    response = self.ru.request(
                        method=api_images_upload['method'],
                        url=url,
                        headers=api_images_upload.get('headers'),
                        # 注意：files 参数传给 files，普通参数传给 data 或 json
                        files=current_files,
                    )
                    # 3. 解析响应
                    response_json = response.json()
                    # 4. 将结果存入列表
                    list_OverViewImgUrls.append(response_json["data"][0])
                    print(f"    -> 上传成功，状态码: {response.status_code}")
            except FileNotFoundError:
                print(f"    -> 错误：找不到文件 {file_path}")
                # 记录错误信息，防止后续步骤崩溃
                #upload_results.append({"file_name": v_name, "error": "File Not Found"})
            except Exception as e:
                print(f"    -> 未知错误: {e}")
                #upload_results.append({"file_name": v_name, "error": str(e)})
        return list_OverViewImgUrls

    @allure.step("创建ARWU排名指标数据分析报告")
    def request_ranking_create(self,
                               name,
                               rVerNo,
                               version,
                               OverViewImgUrls: list):
        """
        创建报告
        :param name:报告名称
        :param rVerNo:选择的版本，如202508
        :param version:选择的版本，如：2025年08月
        :param OverViewImgUrls:总览图片位置。共有2个，放在列表里
        :return:报告ID
        """
        api_ranking_create = self.al.get_api('report_center', 'report_center', 'ranking_create')
        url = api_ranking_create['url']
        payload = self.do.get_copy_key_from_dict(api_ranking_create, "payload")
        payload.update(
            {
                "name": name,
                "lang": "zh-CN",
                "rVerNo": rVerNo,
                "version": version,
                "OverViewImgUrls": OverViewImgUrls
            }
        )
        response = self.ru.request(
            method=api_ranking_create['method'],
            url=url,
            headers=api_ranking_create.get('headers'),
            json=payload
        )
        response_json = response.json()
        assert response_json["code"] == api_ranking_create["expected"]["code"], f"创建报告【{name}】失败，请求响应:{response_json}"
        return response_json["data"]

    @allure.step("生成报告")
    def request_ranking_generate(self, report_id):
        """
        异步报告生成接口
        :param report_id:报告ID
        :return:
        """
        timeout_seconds = 10
        api_generate_report = self.al.get_api('report_center', 'report_center', 'generate_report')
        url = self.do.format_url(api_generate_report['url'], id=report_id)

        start_time = time.time()  # 记录开始时间

        print(f"开始轮询报告 {report_id}，最大等待时间: {timeout_seconds}秒")

        while True:
            # 1. 检查是否超时
            elapsed_time = time.time() - start_time
            if elapsed_time > timeout_seconds:
                raise TimeoutError(f"❌ 错误：轮询超时！已等待 {elapsed_time:.1f} 秒，仍未获取到结果。")
            try:
                # 2. 发起请求
                response = self.ru.request(
                    method=api_generate_report['method'],
                    url=url,
                    headers=api_generate_report.get('headers'),
                )
                response_json = response.json()
                # 3. 接口层级的断言（失败直接报错，不要重试）
                # 如果接口崩了(500/404)，重试通常没意义，应该 Fail Fast
                assert response.status_code == 200, f"接口请求失败: {response.status_code}"
                # 业务Code校验
                if response_json["code"] != api_generate_report["expected"]["code"]:
                    raise AssertionError(f"业务码错误: {response_json}")
                data = response_json.get('data', {})
                report_path = data.get('path')
                isPdf = data.get('isPdf')

                # 3. 判断核心条件：path 是否有值
                if report_path and report_path != "" and isPdf is True:
                    print(f"✅ 成功：报告已生成！(耗时 {elapsed_time:.1f} 秒)")
                    return data  # 成功拿到数据，跳出循环并返回
                elif report_path == "":
                    print(f"⏳ HTML报告正在生成中...(耗时 {elapsed_time:.1f} 秒)")
                elif report_path and report_path != "" and isPdf is False:
                    print(f"⏳ PDF报告正在生成中...(耗时 {elapsed_time:.1f} 秒)")
                else:
                    print(f"⏳ ({elapsed_time:.1f}s) 报告生成中... path为空，继续等待")
            except Exception as e:
                print(f"⚠️ 请求异常: {e}")
            # 4. 暂停一段时间再进行下一次循环
            time.sleep(3)


    @allure.step("删除报告")
    def delete_report(self, reportId):
        api_delete_report = self.al.get_api('report_center', 'report_center', 'delete_report')
        url = self.do.format_url(api_delete_report['url'], reportId=reportId)
        response = self.ru.request(
            method=api_delete_report['method'],
            url=url,
            headers=api_delete_report.get('headers')
        )
        response_json = response.json()
        assert response_json["code"] == api_delete_report["expected"]["code"], f"删除报告【{reportId}】失败，请求响应:{response_json}"
        assert response_json["data"] is True, f"删除报告【{reportId}】失败，请求响应:{response_json}"





