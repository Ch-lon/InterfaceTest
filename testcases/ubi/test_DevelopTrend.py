# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : test_DevelopTrend.py
@Author  : Chlon
@Date    : 2025/10/21 13:17
@Desc    : 排名趋势测试类
"""
import os
import pytest
import allure
import io                          # <--- 1. 导入 io 库
from svglib.svglib import svg2rlg    # <--- 2. 导入 svglib
from reportlab.graphics import renderPM  # <--- 3. 导入 reportlab
from common.logger import get_logger
from product.ubi.pages.DevelopTrend import DevelopTrend

class TestDevelopTrend:

    logging = get_logger(__name__)
    test_data = ["RC00005"]

    # 参数化测试，为不同的 school_code 运行测试
    @pytest.fixture(scope="module", params=test_data)
    def ubi_session(self, choose_product_session, request):
        """
        创建最终用于 UBI 接口测试的、带 cookie 的 RequestUtil 实例。
        """
        school_code = request.param
        # self.cg = CGOperations(cg_session,config)
        session = choose_product_session("ubi", school_code)
        yield session

    @pytest.fixture(scope="module", params=test_data)
    def univCode(self, request):
        """从 ubi_session_data 中提取并返回 school_code。"""
        school_code = request.param
        return school_code

    @pytest.fixture(scope="module", autouse=True)
    def load_page(self, ubi_session):
        self.session = ubi_session
        page = DevelopTrend(self.session)
        yield page

    @pytest.fixture(scope="module")
    def indicators_data(self, load_page):
        """
        获取排名趋势指标数据
        """
        rankingTypeId, verNo = load_page.get_version()
        list_ind_info = load_page.get_developtrend_indicators(rankingTypeId, verNo)
        yield list_ind_info,rankingTypeId, verNo

    @allure.story("排名趋势排名校验")
    @allure.title("检查当前学校排名趋势页数据")
    @allure.tag("regression")
    @allure.description("检查当前学校排名趋势页数据")
    def test_DevelopTrend01(self, load_page, indicators_data):
        list_ind_info,rankingTypeId, verNo = indicators_data
        load_page.check_indicators_rank_form(list_ind_info,rankingTypeId, verNo, "202508")

    # @allure.story("排名趋势图片下载校验")
    # @allure.title("检查当前学校排名趋势图片")
    # @allure.tag("regression")
    # @allure.description("检查当前学校排名趋势图片")
    # def test_DevelopTrend02(self, load_page):
    #     response = load_page.check_image_download()
    #     # 断言：Content-Type 应该是 SVG
    #     content_type = response.headers.get('Content-Type', '')
    #     assert 'image/svg+xml' in content_type, f"期望 Content-Type 为 'image/svg+xml', 实际为 '{content_type}'"
    #     # --- 3. 保存图片以便查看 ---
    #     load_page.fm.clear_directory(load_page.download_files_path)
    #     #load_page.fm.write_binary_file_and_save(response.text, load_page.download_files_path, "名次对比图片下载.svg")
    #     # --- 4. 保存原始 SVG 文件 (以便调试) ---
    #     svg_path = os.path.join(load_page.download_files_path, "ranking-prefix-actual.svg")
    #     try:
    #         with open(svg_path, "w", encoding="utf-8") as f:
    #             f.write(response.text)
    #         print(f"\n--- 原始SVG已保存到: {svg_path} ---")
    #     except IOError as e:
    #         print(f"警告：保存SVG文件失败: {e}")
    #
    #     # --- 5. 【新增】转换并保存为 PNG ---
    #     png_path = os.path.join(load_page.download_files_path, "ranking-prefix-actual.png")
    #     try:
    #         # svglib 需要一个文件句柄，我们使用 io.StringIO 从文本创建
    #         # 注意：这里用 response.text (字符串) 而不是 response.content (字节)
    #         drawing = svg2rlg(svg_path)
    #
    #         # renderPM 将其绘制并保存为PNG
    #         renderPM.drawToFile(drawing, png_path, fmt="PNG")
    #         print(f"--- PNG 图片已保存到: {png_path} ---")
    #     except Exception as e:
    #         assert False, f"SVG 转换 PNG 失败: {e}"

    @allure.story("名次对比数据导出校验")
    @allure.title("检查当前学校名次对比数据导出")
    @allure.tag("regression")
    @allure.description("检查当前学校名次对比数据导出")
    def test_DevelopTrend03(self, load_page, indicators_data,univCode):
        _,rankingTypeId, verNo = indicators_data
        response = load_page.data_export(rankingTypeId, verNo, "202508")
        filename = f"{univCode}_排名趋势_{verNo}.xlsx"
        load_page.check_export_response(response, "xlsx", filename)

    @allure.story("名次对比-对比版本的明细点击校验")
    @allure.title("检查当前学校名次对比-对比版本的明细请求")
    @allure.tag("regression")
    @allure.description("检查当前学校名次对比-对比版本的明细请求")
    def test_DevelopTrend04(self, load_page, indicators_data):
        list_ind_info, rankingTypeId, verNo = indicators_data
        load_page.check_compare_detail_click(list_ind_info,rankingTypeId,verNo,"202508")

    @allure.story("趋势分析-各指标趋势分析")
    @allure.title("检查当前学校与对比学校各指标趋势")
    @allure.tag("regression")
    @allure.description("检查当前学校与对比学校各指标趋势")
    def test_DevelopTrend05(self, load_page, indicators_data):
        list_ind_info, rankingTypeId, verNo = indicators_data
        # resp = load_page.request_rankingAnalysis(16254,202511,"RC00002")
        # print("当前版本为：",resp[0])
        load_page.all_ind_rankingAnalysis(list_ind_info,verNo,"RC00002")






