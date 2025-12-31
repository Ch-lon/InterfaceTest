# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : test_ranking_monitor.py
@Author  : Chlon
@Date    : 2025/12/11 11:24
@Desc    : 排名监测测试用例
"""
import allure
import pytest
from product.ubi.pages.ranking_monitor import RankingMonitor

@allure.feature("排名监测页")
@allure.tag("API", "RankingMonitor")
class TestRankingMonitor:
    test_data = ["RC00005","RI02727"]

    # 参数化测试，为不同的 school_code 运行测试
    @pytest.fixture(scope="module", params=test_data)
    def ubi_session(self, choose_product_session, request):
        """
        创建最终用于 UBI 接口测试的、带 cookie 的 RequestUtil 实例。
        """
        school_code = request.param

        # 在Allure中记录参数检查
        allure.step(f"检查学校代码: {school_code}")

        if not school_code.startswith("RC"):
            # 记录详细的跳过信息
            skip_reason = f"学校 {school_code} 不是国内院校，没有排名监测页面"
            allure.attach(
                skip_reason,
                name="跳过原因",
                attachment_type=allure.attachment_type.TEXT
            )

            # 设置测试标题显示跳过状态
            allure.dynamic.title(f"排名监测页面 - {school_code} [已跳过]")

            # 设置测试描述
            allure.dynamic.description(f"测试被跳过\n原因: {skip_reason}")

            # 跳过测试
            pytest.skip(skip_reason)

        # 如果参数有效，设置正常的标题
        allure.dynamic.title(f"排名监测 - {school_code}")
        allure.dynamic.description(f"测试学校代码: {school_code}")

        session = choose_product_session("ubi", school_code)
        yield session,school_code

    @pytest.fixture(scope="module")
    def univCode(self, ubi_session):
        """从 ubi_session 中提取并返回 school_code。"""
        # 直接从ubi_session的请求参数中获取
        # 注意：由于ubi_session可能被跳过，这个fixture只有在ubi_session成功创建时才会被调用
        _,school_code = ubi_session
        return school_code  # 这里获取ubi_session的参数

    @pytest.fixture(scope="module", autouse=True)
    def load_page(self, ubi_session):
        session,_ = ubi_session
        page = RankingMonitor(session)
        yield page

    @allure.story("排名监测数据导出")
    @allure.title("排名监测数据导出功能及文件是否正常")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("regression", "API")
    @allure.description("排名监测数据导出功能及文件是否正常")
    def test_ranking_monitor01(self, load_page, univCode):
        """
        排名监测数据导出
        """
        response = load_page.ranking_monitor_data_export()
        filename = f"{univCode}_排名监测.xlsx"
        load_page.check_export_response(response, "xlsx", filename)

    @allure.story("各类排名数据校验")
    @allure.title("各类排名数据校验")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("regression", "API")
    @allure.description("各类排名数据校验")
    def test_ranking_monitor02(self, load_page):
        """
        各类排名数据校验
        """
        list_fail = []
        list_approxYear_fail = []
        list_all_ranking_data = load_page.get_ranking_data ()
        for dict_ranking_data in list_all_ranking_data:
            name, versions = load_page.do.get_value_from_dict(dict_ranking_data, "name", "versions")
            if not versions:
                list_fail.append(name)
                continue
            for dict_ver in versions:
                approxYear,indicators= load_page.do.get_value_from_dict(dict_ver, "approxYear", "indicators")
                if indicators is None:
                    list_approxYear_fail.append(name-approxYear)

        all_fail = []
        if list_fail:
            all_fail.append(f"共有{len(list_fail)}个排名未获得数据：{list_fail}！")
        if list_approxYear_fail:
            all_fail.append(f"共有{len(list_approxYear_fail)}个排名的年份未获得数据，具体排名和年份为：{list_approxYear_fail}！")
        if all_fail:
            raise AssertionError("\n".join(all_fail))

