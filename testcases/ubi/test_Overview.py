# InterfaceTest/testcases/test_Overview.py
import os
import re
import pytest
import openpyxl
from urllib.parse import unquote
from product.ubi.pages.Overview import Overview
from common.path_util import get_absolute_path
from urllib.parse import urljoin
from common.request_util import RequestUtil
from common.selenium_util import get_cookies_from_browser
from product.ubi.pages.Login import UbiCommon


class TestOverview:

    test_data = ["RC00005", "ANOTHER_SCHOOL_CODE"]
    # 参数化测试，为不同的 school_code 运行测试
    @pytest.fixture(scope="module",params=test_data)
    def ubi_request_session(self,config,auth_token,request):
        """
        创建最终用于 UBI 接口测试的、带 cookie 的 RequestUtil 实例。
        """
        ubi_base_url = config.get('ubi_base_url')
        print(f"创建 UBI Session，Base URL: {ubi_base_url}")
        ru = RequestUtil(ubi_base_url)
        school_code = request.param
        login_name = config.get('username')
        login_type_id = config.get('loginTypeId', 2)

        # 拼接需要用 Selenium 访问的 URL
        jump_path = f"/login?loginTypeId={login_type_id}&univCode={school_code}&loginName={login_name}&token={auth_token}"
        jump_url = urljoin(ubi_base_url, jump_path)

        # 使用 Selenium 获取 cookie
        cookies = get_cookies_from_browser(jump_url)
        if not cookies:
            pytest.fail(f"未能从 {jump_url} 获取到 cookie。")

        # 将 cookie 注入到 requests session 中
        ru.session.cookies.update(cookies)

        # 同样可以将 token 设置到请求头中
        ru.session.headers.update({'Authorization': auth_token})

        yield ru, school_code


    @pytest.fixture(scope="module", autouse=True)
    def load_page(self,ubi_request_session):
        self.session, self.school_code= ubi_request_session
        page = Overview(self.session)
        yield page


    def test_overview01(self, load_page):
        # 如果需要为每个测试用例切换 school_code，可以重新获取cookie
        # 对于很多场景，如果cookie在不同school_code之间是通用的，这一步可能不是必须的
        # 但如果每个school_code需要独立的会话，这一步是必要的

        # 1. 调用接口
        # 假设 company_id 与 school_code 有某种关联，或者是一个独立的测试参数
        company_id = "11"
        response = load_page.get_version()

        # 2. 基本断言
        print(response.json())
        assert response.status_code == 200

    # def test_data_export_for_school(self, overview_page, request_session, config, auth_token, school_code):
        # expected_content_type = "application/octet-stream"
        # assert expected_content_type in response.headers.get("Content-Type", ""), "响应的Content-Type不符合预期"
        #
        # content_disposition = response.headers.get("Content-Disposition")
        # assert content_disposition is not None, "响应头中缺少 Content-Disposition"
        #
        # filename_match = re.search(r'filename="?([^"]+)"?', content_disposition)
        # assert filename_match is not None, "无法从 Content-Disposition 中解析出文件名"
        #
        # filename = unquote(filename_match.group(1), encoding='utf-8')
        # print(f"从响应头中解析出的文件名是: {filename}")
        #
        # # 3. 保存文件
        # download_dir = get_absolute_path("../downloads")
        # overview_page.fm.create_directory_if_not_exists(download_dir)
        # file_path = os.path.join(download_dir, filename)
        #
        # with open(file_path, "wb") as f:
        #     f.write(response.content)
        # print(f"文件已保存至: {file_path}")
        #
        # # 4. 验证文件内容
        # assert os.path.getsize(file_path) > 0, "下载的文件是空的"
        # try:
        #     workbook = openpyxl.load_workbook(file_path)
        #     sheet = workbook.active
        #     assert sheet.cell(row=1, column=1).value is not None, "Excel文件A1单元格没有内容"
        #     print(f"成功验证Excel文件内容，A1单元格的值为: {sheet.cell(row=1, column=1).value}")
        # except Exception as e:
        #     pytest.fail(f"验证下载的Excel文件失败: {e}")