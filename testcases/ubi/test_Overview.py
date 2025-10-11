# InterfaceTest/testcases/test_Overview.py
import pytest
from product.ubi.pages.Overview import Overview
import allure
import os
from openpyxl import load_workbook
from product.cg.pages.CGOperations import CGOperations

@allure.feature("总体定位页")
@allure.tag("API","Overview")
class TestOverview:

    test_data = ["RC00005"]

    # 参数化测试，为不同的 school_code 运行测试
    @pytest.fixture(scope="module",params=test_data)
    def ubi_session(self,choose_product_session,request):
        """
        创建最终用于 UBI 接口测试的、带 cookie 的 RequestUtil 实例。
        """
        school_code = request.param
        #self.cg = CGOperations(cg_session,config)
        session = choose_product_session("ubi",school_code)
        yield session,school_code


    @pytest.fixture(scope="function", autouse=True)
    def load_page(self,ubi_session):
        self.session,self.school_code= ubi_session
        page = Overview(self.session)
        yield page

    @allure.story("数据导出校验")
    @allure.title("检查数据导出的响应")
    @allure.tag("regression")
    @allure.description("检查数据导出的响应是否符合预期")
    def test_Overview01(self, load_page):
        # 获取版本及排名类型信息
        rankingTypeId, verNo = load_page.get_version()
        # 获取该版本下的该校数据
        overview_data = load_page.get_overview_data(verNo, rankingTypeId)
        # 提取同排名区间
        range_start, range_end = load_page.get_ranking_range(overview_data)
        # 数据导出请求
        response = load_page.data_export(verNo, rankingTypeId, range_start, range_end)
        # 设置导出文件命名
        filename = f"{self.school_code}_总体定位_{verNo}.xlsx"
        assert response.status_code == 200
        # 清空下载目录
        load_page.fm.clear_directory(load_page.download_files_path)
        try:
            file_path = load_page.fm.write_binary_file_and_save(response.content,load_page.download_files_path, filename)
            assert file_path is not None, "文件未能成功保存"
            # 断言3：检查文件大小是否符合要求（例如，大于1KB）
            file_size = load_page.fm.get_file_size(file_path)
            # 设定一个合理的最小文件大小阈值，例如1024字节 (1KB)
            # 一个空的Excel文件也占用一定空间，所以这个值通常比0大
            assert file_size > 1 * 1024, f"文件大小 {file_size} 字节, 小于预期的最小值 1 KB"
        except Exception as e:
            # 将异常作为附件内容添加到测试报告中
            allure.attach(str(e), "异常信息", allure.attachment_type.TEXT)

    # def test_Overview02(self, load_page):
    #     response = 1