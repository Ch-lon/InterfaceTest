# -*- coding: utf-8 -*-
"""
@Project : InterfaceTest
@File    : FeishuNotification.py
@Author  : Chlon
@Date    : 2025/12/31 15:34
@Desc    : 飞书通知
"""
# -*- coding: utf-8 -*-
import requests
import json
import os
from common.path_util import get_absolute_path


class FeishuNotification:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
        self.headers = {'Content-Type': 'application/json'}

    def get_allure_results(self):
        """
        读取Allure生成的summary.json获取统计信息
        """
        # 注意：这里路径要指向你生成报告后的 widgets/summary.json
        summary_path = get_absolute_path("reports/allure_reports/widgets/summary.json")

        if not os.path.exists(summary_path):
            print(f"警告：找不到Allure统计文件: {summary_path}")
            return None

        try:
            with open(summary_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('statistic', {})
        except Exception as e:
            print(f"读取Allure结果失败: {e}")
            return None

    def send_notification(self, report_url):
        """
        发送飞书卡片消息
        """
        stats = self.get_allure_results()
        if not stats:
            return

        total = stats.get('total', 0)
        passed = stats.get('passed', 0)
        failed = stats.get('failed', 0)
        broken = stats.get('broken', 0)
        skipped = stats.get('skipped', 0)

        # 计算通过率
        pass_rate = "{:.2%}".format(passed / total) if total > 0 else "0.00%"

        # 根据结果决定标题颜色（红色失败，绿色成功）
        title_color = "red" if failed> 0 else "green"

        # 构造飞书富文本卡片 (Interactive Card)
        card_content = {
            "msg_type": "interactive",
            "card": {
                "config": {
                    "wide_screen_mode": True
                },
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": "📢 国际360自动化测试报告"
                    },
                    "template": title_color
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"本次共执行{total}个用例，通过{passed}个，失败{failed}个，跳过{skipped}个。\n通过率：{pass_rate}"
                        }
                    },
                    {
                        "tag": "hr"
                    },
                    {
                        "tag": "div",
                        "fields": [
                            {
                                "is_short": True,
                                "text": {
                                    "tag": "lark_md",
                                    "content": f"**总用例数**\n{total}"
                                }
                            },
                            {
                                "is_short": True,
                                "text": {
                                    "tag": "lark_md",
                                    "content": f"**通过**\n🟢 {passed}"
                                }
                            },
                            {
                                "is_short": True,
                                "text": {
                                    "tag": "lark_md",
                                    "content": f"**失败**\n🔴 {failed}"
                                }
                            },
                            {
                                "is_short": True,
                                "text": {
                                    "tag": "lark_md",
                                    "content": f"**跳过**\nVi {skipped}"
                                }
                            }
                        ]
                    },
                    {
                        "tag": "action",
                        "actions": [
                            {
                                "tag": "button",
                                "text": {
                                    "tag": "plain_text",
                                    "content": "查看详细报告"
                                },
                                "type": "primary",
                                "url": report_url
                            }
                        ]
                    }
                ]
            }
        }

        try:
            response = requests.post(self.webhook_url, headers=self.headers, json=card_content)
            if response.status_code == 200:
                print("✅ 飞书通知发送成功")
            else:
                print(f"❌ 飞书通知发送失败: {response.text}")
        except Exception as e:
            print(f"❌ 发送请求异常: {e}")


if __name__ == '__main__':
    # 调试用
    webhook = "你的webhook地址"
    feishu = FeishuNotification(webhook)
    feishu.send_notification()