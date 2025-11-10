#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日邮件自动摘要系统
功能：
1. 获取当天QQ邮箱的所有邮件
2. 使用Gemini AI生成摘要报告
3. 将摘要发送到指定邮箱
"""

from email_fetcher import QQEmailFetcher
from email_sender import QQEmailSender
from ai_summarizer import GeminiSummarizer
from utils import load_env_config
from datetime import datetime
import sys


def main():
    """主函数"""
    print("=" * 70)
    print("📧 每日邮件自动摘要系统")
    print("=" * 70)
    print(f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    try:
        # 1. 加载配置
        print("【步骤 1/4】加载配置...")
        config = load_env_config()
        print(f"✓ 配置加载成功")
        print(f"  - QQ邮箱: {config['qq_email']}")
        print(f"  - 收件人: {config['recipient_email']}")
        print()

        # 2. 获取今天的邮件
        print("【步骤 2/4】获取今天的邮件...")
        fetcher = QQEmailFetcher(config['qq_email'], config['qq_auth_code'])

        if not fetcher.connect():
            print("✗ 无法连接到邮箱服务器")
            return 1

        try:
            emails = fetcher.fetch_today_emails()
        finally:
            fetcher.disconnect()

        if emails is None:
            emails = []

        print(f"✓ 成功获取 {len(emails)} 封邮件")
        print()

        # 3. 使用Gemini生成摘要
        print("【步骤 3/4】生成AI摘要报告...")
        summarizer = GeminiSummarizer(config['gemini_api_key'])
        summary_report = summarizer.summarize_emails(emails)
        print()

        # 4. 发送摘要邮件
        print("【步骤 4/4】发送摘要报告...")
        sender = QQEmailSender(config['qq_email'], config['qq_auth_code'])

        if not sender.connect():
            print("✗ 无法连接到SMTP服务器")
            return 1

        try:
            subject = f"📧 每日邮件摘要 - {datetime.now().strftime('%Y年%m月%d日')}"
            success = sender.send_email(
                to_email=config['recipient_email'],
                subject=subject,
                content=summary_report,
                content_type='html'
            )

            if success:
                print()
                print("=" * 70)
                print("✅ 任务完成！")
                print(f"✓ 分析了 {len(emails)} 封邮件")
                print(f"✓ 摘要报告已发送到: {config['recipient_email']}")
                print("=" * 70)
                return 0
            else:
                print("✗ 邮件发送失败")
                return 1

        finally:
            sender.disconnect()

    except ValueError as e:
        print(f"✗ 配置错误: {str(e)}")
        print("请检查 .env 文件配置")
        return 1
    except Exception as e:
        print(f"✗ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
