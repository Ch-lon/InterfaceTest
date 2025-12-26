# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : report_center.py
@Author  : Chlon
@Date    : 2025/11/17 11:16
@Desc    : 报告中心
"""

import allure,os
from common.path_util import get_absolute_path
from product.ubi.pages.UbiCommon import UbiCommon

class ReportCenter(UbiCommon):

    @allure.step("报告列表请求")
    def report_list_request(self) -> list:
        """
        获取报告列表
        """
        api_report_list = self.al.get_api('report_center', 'report_center', 'report_list')
        url = api_report_list['url']

        response = self.ru.request(
            method=api_report_list['method'],
            url=url,
            headers=api_report_list.get('headers'),
            json = api_report_list.get("data")
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





        upload_results = []
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
                    # 我们把“文件名”和“响应”绑定在一起，方便你后续使用
                    # result_entry = {
                    #     "file_name": v_name,
                    #     "status_code": response.status_code,
                    #     "response_data": response_json["data"]
                    # }
                    # upload_results.append(result_entry)
                    upload_results.append(response_json["data"])
                    print(f"    -> 上传成功，状态码: {response.status_code}")
            except FileNotFoundError:
                print(f"    -> 错误：找不到文件 {file_path}")
                # 记录错误信息，防止后续步骤崩溃
                #upload_results.append({"file_name": v_name, "error": "File Not Found"})
            except Exception as e:
                print(f"    -> 未知错误: {e}")
                #upload_results.append({"file_name": v_name, "error": str(e)})
        return upload_results







        # # 组装 requests 需要的 files 结构
        # # 格式: {'字段名': ('文件名', 文件句柄, 'MIME类型')}
        # files_payload = {
        #     files['field_name']: (
        #         files['virtual_name'],
        #         open(file_path, 'rb'),
        #         files['mime_type']
        #     )
        # }
        # response = self.ru.request(
        #     method=api_images_upload['method'],
        #     url=url,
        #     headers=api_images_upload.get('headers'),
        #     # 注意：files 参数传给 files，普通参数传给 data 或 json
        #     files=files_payload,
        # )
        # response_json = response.json()
        # assert response_json["code"] == api_images_upload["expected"]["code"], f"上传报告图片失败，请求响应:{response_json}"
        # return response_json["data"]