# InterfaceTest/testcases/test_Overview.py
import pytest
from product.ubi.pages.Overview import Overview
from urllib.parse import urljoin
from common.RequestUtil import RequestUtil
from common.SeleniumUtil import get_cookies_from_browser
from product.cg.pages.CGOperations import CGOperations


class TestOverview:

    test_data = ["RC00005"]
    # 参数化测试，为不同的 school_code 运行测试
    @pytest.fixture(scope="module",params=test_data)
    def ubi_session(self,cg_session,auth_token,request):
        """
        创建最终用于 UBI 接口测试的、带 cookie 的 RequestUtil 实例。
        """
        self.school_code = request.param
        self.cg = CGOperations(cg_session,config)
        ru = self.cg.choose_product_session(product_name="ubi", school_code=self.school_code, token=auth_token)
        yield ru


    @pytest.fixture(scope="module", autouse=True)
    def load_page(self,ubi_session):
        self.session= ubi_session
        page = Overview(self.session)
        yield page


    def test_Overview01(self, load_page):
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