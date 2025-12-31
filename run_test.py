# InterfaceTest/run_test.py
import pytest
import os
import yaml
import time
# 引入新写的类
from common.FeishuNotification import FeishuNotification
from common.ApiLoader import ApiLoader  # 假设你用这个读取config
from common.path_util import get_absolute_path
from common.FileManager import FileManager


def run():
    # 1. 执行测试
    pytest.main(['-vs', './testcases/ubi', '--alluredir', './reports/allure_results', '--clean-alluredir'])

    # 2. 生成 Allure 报告 (这一步很重要，必须生成报告后才有 summary.json)
    # 注意：确保你的系统安装了 allure 命令行工具，并且在环境变量中
    os.system(f"allure generate ./reports/allure_results -o ./reports/allure_reports --clean")

    # 3. 发送飞书通知
    try:
        # 读取配置 (根据你项目中读取 config.yml 的方式调整)
        # 这里假设手动读取，或者你使用现有的 ApiLoader/ConfigLoader
        fm = FileManager()
        config_path = get_absolute_path("config/config.yml")
        config = fm.load_yaml_file(config_path)

        webhook_url = config.get('lark_url', {}).get('test')
        report_url = config.get('lark_url', {}).get('report_url', "")

        if webhook_url:
            print("正在发送飞书通知...")
            feishu = FeishuNotification(webhook_url)
            feishu.send_notification(report_url)
        else:
            print("未配置飞书 Webhook，跳过发送通知。")

    except Exception as e:
        print(f"发送通知流程异常: {e}")


if __name__ == '__main__':
    run()




# @pytest.fixture(scope="class")
    # def captured_oss_urls(self, ubi_session, config, univCode,auth_token,load_page):
    #     """
    #     使用 Playwright 访问报告中心页面，拦截前端自动调用的接口响应，获取 OSS 地址。
    #     """
    #     print("\n--- [Fixture] Playwright 启动：监听前端自动生成的图片接口 ---")
    #     session, _ = ubi_session
    #
    #     # 1. 准备 Cookies (免登录)
    #     #requests_cookies = session.session.cookies.get_dict()
    #     requests_cookies = load_page.ru.session.cookies.get_dict()
    #     playwright_cookies = []
    #     base_url = config.get("ubi_base_url")  # 确保 config.yml 中配置了前端地址
    #     if not base_url:
    #         # 如果配置里没写，这里临时给个默认值或报错，请根据实际情况调整
    #         raise ValueError("config.yml 中缺少 'ubi_base_url' 配置")
    #
    #     domain = urlparse(base_url).hostname
    #     for k, v in requests_cookies.items():
    #         playwright_cookies.append({
    #             "name": k, "value": v, "domain": domain, "path": "/"
    #         })
    #
    #     # 用于存储捕获到的 OSS 地址
    #     oss_urls = []
    #
    #     # 2. 定义响应拦截处理函数
    #     def handle_response(response):
    #         # 【关键配置】请将 'generating_interface_keyword' 替换为那个自动生成图片的接口 URL 中的独特关键字
    #         # 例如接口是 /api/report/generate_chart，关键字可以是 "generate_chart"
    #         target_api_keyword = "upload-report-images"  # <--- 请根据实际接口URL修改这里！
    #
    #         if target_api_keyword in response.url and response.status == 200:
    #             try:
    #                 resp_json = response.json()
    #                 print(f"  -> 捕获到目标接口响应: {response.url}")
    #                 # 【关键配置】根据实际返回结构提取 OSS 地址
    #                 # 假设返回结构是 {"code": 200, "data": "https://oss...", ...}
    #                 # 或者是 {"data": ["url1"]}，请根据实际情况调整
    #                 if "data" in resp_json:
    #                     data = resp_json["data"]
    #                     # 如果 data 是列表取第一个，如果是字符串直接用
    #                     url = data[0] if isinstance(data, list) else data
    #                     if url and str(url).startswith("http"):
    #                         oss_urls.append(url)
    #                         print(f"     已提取 OSS 地址: {url}")
    #             except Exception as e:
    #                 print(f"     解析响应失败: {e}")
    #
    #     # 3. 启动浏览器并访问
    #     with sync_playwright() as p:
    #         browser = p.chromium.launch(headless=False)  # 调试时可改为 False 观察过程
    #         context = browser.new_context()
    #         context.add_cookies(playwright_cookies)
    #
    #         # 开启网络监听
    #         page = context.new_page()
    #         page.on("response", handle_response)
    #
    #         # 拼接报告中心的前端 URL，请根据实际路由修改
    #         # 假设报告中心路由是 /#/report-center 或 /#/analysis/report
    #         ubi_url =f"https://ubi-3f3ab907.gaojidata.com/login?loginTypeId=2&univCode={univCode}&loginName=chenglong.yu&token={auth_token}"
    #         target_url = f"{base_url}/report-center"
    #         print(f"  -> 正在访问页面: {target_url}")
    #
    #         try:
    #             page.goto(ubi_url, wait_until="networkidle")
    #             page.goto(target_url, wait_until="networkidle")  # 等待网络空闲，通常接口就加载完了
    #             reportType = "ranking"
    #             list_reports = load_page.report_list_request(reportType)
    #             if list_reports:
    #                 button_generate_report_whit_list=page.locator(".create-report.px-12.py-10.cursor-pointer")
    #                 button_generate_report_whit_list.click()
    #             else:
    #                 button_generate_report_without_list=page.locator(".ant-btn.ant-btn-primary.immediately_report")
    #                 button_generate_report_without_list.click()
    #             button=page.wait_for_selector("//button[@class='ant-btn ant-btn-primary']//span[text()='生成报告']")
    #             button.click()
    #             # 4. 轮询等待，直到获取到 2 个地址或超时
    #             timeout = 15  # 秒
    #             start_time = time.time()
    #             while len(oss_urls) < 2:
    #                 if time.time() - start_time > timeout:
    #                     print("  -> ⚠️ 等待超时，未捕获到足够的 OSS 地址。")
    #                     break
    #                 time.sleep(1)
    #
    #         except Exception as e:
    #             print(f"Playwright 执行异常: {e}")
    #         finally:
    #             browser.close()
    #
    #     print(f"--- [Fixture] 监听结束，共获取 {len(oss_urls)} 个地址 ---")
    #     yield oss_urls

    # @pytest.fixture(scope="class")
    # def report_context(self, load_page, captured_oss_urls,indicators_data, univCode):
    #     """
    #     前置操作：生成报告，并返回报告的相关数据。
    #     scope="class" 表示在整个测试类执行期间只运行一次，
    #     所有用例共享这一份生成的报告数据。
    #     """
    #     print("\n--- [Fixture] 开始准备测试数据：生成报告 ---")
    #     _, _, verNo = indicators_data
    #     list_OverViewImgUrls = captured_oss_urls#load_page.upload_report_images()
    #
    #     report_name = f"{univCode}世界大学学术排名指标数据分析报告{verNo}"
    #     version = load_page.df.format_date_string(verNo)
    #
    #     # 创建报告
    #     report_info = load_page.request_ranking_create(report_name, verNo, version, list_OverViewImgUrls)
    #     reportId = report_info["id"]
    #
    #     # 轮询生成报告 (利用你之前写好的逻辑)
    #     report_data = load_page.request_ranking_generate(reportId)
    #     print(f"报告【{report_name}】已生成完毕！选择年份：{version}，院校名：{univCode}")
    #     yield report_name,report_info,report_data # 返回数据给测试用例
    #
    #     # (可选) 后置操作：测试结束后删除报告
    #     print("\n--- [Fixture] 清理测试数据 ---")
    #     #load_page.delete_report(reportId)
    #     print(f"报告【{reportId}】已成功删除！")
    #
    #
    # @allure.story("验证htmlData：ARWU世界大学学术排名指标数据分析报告")
    # @allure.title("验证htmlData：ARWU世界大学学术排名指标数据分析报告")
    # @allure.severity(allure.severity_level.CRITICAL)
    # @allure.tag("regression", "API")
    # @allure.description("验证htmlData：ARWU世界大学学术排名指标数据分析报告")
    # def test_report_center01(self,load_page,report_context,indicators_data,univCode):
    #     """
    #     报告中心
    #     """
    #     _,_,verNo = indicators_data
    #     report_name, report_info, report_data=report_context
    #     version = load_page.df.format_date_string(verNo)
    #
    #     report_htmlData = report_data["htmlData"]
    #     assert univCode in report_htmlData, f"报告HTML内容错误,期望院校：{univCode}，生成版本：{verNo}。实际数据：{report_htmlData}"
    #
    #     # 验证OSS下word文件内容
    #     report_docx_path = report_data["path"]
    #     print(f"报告路径: {report_docx_path}")
    #     load_page.fv.verify_file_content(report_docx_path, ["上海交通大学", f"{version}"])
    #     # 报告列表中会出现该份报告
    #     reportType = report_info["reportType"]
    #     list_reports = load_page.report_list_request(reportType)
    #     # 获取最新的报告信息
    #     dict_new_report= list_reports[0]
    #     assert dict_new_report["name"] == report_name, f"最新报告列表中不存在该报告,期望名称：{report_name}，实际名称：{dict_new_report['name']}"
    #
    # @allure.story("下载PDF报告并验证")
    # @allure.title("下载PDF报告并验证")
    # @allure.severity(allure.severity_level.CRITICAL)
    # @allure.tag("regression", "API")
    # @allure.description("下载PDF报告并验证")
    # def test_report_center02(self,load_page,report_context,univCode):
    #     """
    #     下载PDF报告
    #     """
    #     report_name, report_info, report_data = report_context
    #     report_path = report_data["path"]
    #     print(f"报告路径: {report_path}")
    #     #使用rsplit从右边分割，只分割一次，取第一部分
    #     path = report_path.rsplit(".", 1)[0]
    #     #print(f"分隔后报告路径: {path}")
    #     #report_name_encode = load_page.do.url_encode(report_name)
    #     pdf_url = f"{path}.pdf"
    #     print(f"PDF报告URL: {pdf_url}")
    #     load_page.fv.verify_file_content(pdf_url, ["上海交通大学"])