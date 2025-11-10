#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI摘要生成器
使用Gemini API生成邮件摘要
"""

import google.generativeai as genai
from datetime import datetime


class GeminiSummarizer:
    """Gemini AI摘要生成器"""

    def __init__(self, api_key):
        """初始化Gemini API"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

    def summarize_emails(self, emails):
        """使用Gemini总结邮件"""
        if not emails:
            return self._generate_no_email_report()

        print(f"\n正在使用Gemini AI分析 {len(emails)} 封邮件...")

        # 构建提示词 - 提供更完整的邮件内容
        email_texts = []
        for i, email_info in enumerate(emails, 1):
            # 提取更多正文内容，最多2000字符
            body_content = email_info['body'][:2000] if email_info['body'] else "（无正文内容）"

            email_text = f"""
========== 邮件 {i} ==========
主题: {email_info['subject']}
发件人: {email_info['from']}
接收时间: {email_info['parsed_date']}
正文内容:
{body_content}
===============================
"""
            email_texts.append(email_text)

        prompt = f"""你是一位专业的邮件管理助手。请仔细分析以下 {len(emails)} 封今日收到的邮件，并生成一份实用的摘要报告。

今日邮件详情:
{''.join(email_texts)}

请按照以下要求生成HTML格式的报告：

1. **今日概览** - 统计邮件数量，简述主要类别

2. **优先级分级** - 根据邮件的重要性和紧急性分为三级：
   - 🔴 高优先级：需要立即处理的重要邮件（账单、系统通知、工作邮件等）
   - 🟡 中优先级：需要关注但不紧急的邮件
   - 🟢 低优先级：营销邮件、推广信息等

   每个优先级下列出对应的邮件，包含：
   - 邮件主题
   - 发件人
   - 核心内容摘要（30-50字）
   - 建议操作

3. **邮件分类** - 将邮件按类型归类：
   - 📧 工作邮件
   - 💰 账单/财务
   - 🔔 系统通知
   - 📢 营销推广
   - 📰 新闻资讯
   - 其他

   每类列出数量和代表性邮件

4. **待办事项** - 从邮件中提取需要处理的具体事项：
   - 需要回复的邮件
   - 需要查看的链接/附件
   - 账单缴费提醒
   - 其他行动项

5. **智能建议** - 给出处理建议

HTML格式要求：
- 使用现代化的CSS样式，美观专业
- 使用emoji图标增加可读性
- 重要信息使用醒目的颜色标注
- 保持简洁，避免冗余
- 每封邮件的摘要要包含正文的关键信息，不要只写标题

请直接输出HTML代码，不要有任何解释性文字。"""

        try:
            response = self.model.generate_content(prompt)
            print("✓ AI摘要生成成功")
            return response.text
        except Exception as e:
            print(f"✗ AI摘要生成失败: {str(e)}")
            return self._generate_fallback_report(emails)

    def _generate_no_email_report(self):
        """生成无邮件报告"""
        return f"""
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }}
        .header {{ background: #4CAF50; color: white; padding: 15px; border-radius: 5px; }}
        .content {{ margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="header">
        <h2>📧 每日邮件摘要报告</h2>
        <p>日期: {datetime.now().strftime('%Y-%m-%d')}</p>
    </div>
    <div class="content">
        <h3>📊 今日概览</h3>
        <p>今天没有收到新邮件。</p>
        <p>祝你有美好的一天！</p>
    </div>
</body>
</html>
"""

    def _generate_fallback_report(self, emails):
        """生成备用报告（当AI失败时）- 改进版包含内容摘要"""
        # 按发件人分类邮件
        system_emails = []
        marketing_emails = []
        other_emails = []

        for email_info in emails:
            from_addr = email_info['from'].lower()
            subject = email_info['subject'].lower()
            body_preview = email_info['body'][:150] if email_info['body'] else "（无正文）"

            email_item = {
                'subject': email_info['subject'],
                'from': email_info['from'],
                'time': email_info['parsed_date'],
                'preview': body_preview
            }

            # 改进的分类逻辑 - 先判断系统通知（高优先级），再判断营销
            # 系统通知：账单、安全、验证等重要通知
            is_system = any(word in from_addr or word in subject or word in body_preview[:200].lower() for word in [
                '账单', '欠费', '余额不足', '到期', '续费', '支付', '缴费',
                'bill', 'payment', 'expired', 'renew', 'overdue',
                '验证码', '登录异常', '密码', '风险',
                '停机', '暂停服务', '服务到期'
            ])

            # 营销推广：优惠活动、产品推广等
            is_marketing = any(word in subject or word in body_preview[:200].lower() for word in [
                '优惠', '促销', '折扣', '限时', '抢购', '特价', '活动',
                'sale', 'offer', 'discount', 'deal', 'promotion',
                '1折', '2折', '3折', '5折', '低至', '最低',
                '双11', '618', '秒杀', '团购', '福利',
                '更强大', '更高效', '尽在', '立即体验',
                '免费试用', '新功能', '升级体验',
                'app下载', '下载app', '安装',
                '推荐', '精选', '热门', '爆款'
            ])

            # 分类优先级：系统通知 > 营销推广 > 其他
            # 注意：先判断系统通知，因为系统通知优先级更高
            if is_system:
                system_emails.append(email_item)
            elif is_marketing:
                marketing_emails.append(email_item)
            else:
                other_emails.append(email_item)

        # 生成分类列表HTML
        def generate_email_list(email_list, priority_color):
            html = ""
            for email in email_list:
                html += f"""
        <div style="margin-bottom: 20px; padding: 15px; background: white; border-left: 4px solid {priority_color}; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h4 style="margin: 0 0 10px 0; color: #333;">📧 {email['subject']}</h4>
            <p style="margin: 5px 0; color: #666; font-size: 14px;">
                <strong>发件人:</strong> {email['from']}<br>
                <strong>时间:</strong> {email['time']}
            </p>
            <p style="margin: 10px 0 0 0; padding: 10px; background: #f9f9f9; border-radius: 3px; color: #555; font-size: 13px; line-height: 1.6;">
                <strong>内容摘要:</strong> {email['preview']}...
            </p>
        </div>
"""
            return html

        system_section = ""
        if system_emails:
            system_section = f"""
        <div style="margin-bottom: 30px;">
            <h3 style="color: #f44336; border-bottom: 2px solid #f44336; padding-bottom: 10px;">
                🔴 高优先级 - 系统通知/账单 ({len(system_emails)} 封)
            </h3>
            {generate_email_list(system_emails, '#f44336')}
        </div>
"""

        marketing_section = ""
        if marketing_emails:
            marketing_section = f"""
        <div style="margin-bottom: 30px;">
            <h3 style="color: #4CAF50; border-bottom: 2px solid #4CAF50; padding-bottom: 10px;">
                🟢 低优先级 - 营销推广 ({len(marketing_emails)} 封)
            </h3>
            {generate_email_list(marketing_emails, '#4CAF50')}
        </div>
"""

        other_section = ""
        if other_emails:
            other_section = f"""
        <div style="margin-bottom: 30px;">
            <h3 style="color: #FF9800; border-bottom: 2px solid #FF9800; padding-bottom: 10px;">
                🟡 中优先级 - 其他邮件 ({len(other_emails)} 封)
            </h3>
            {generate_email_list(other_emails, '#FF9800')}
        </div>
"""

        return f"""
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            padding: 20px;
            background: #f5f5f5;
            color: #333;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 28px;
        }}
        .header p {{
            margin: 5px 0;
            opacity: 0.9;
        }}
        .summary {{
            background: #e3f2fd;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            border-left: 4px solid #2196F3;
        }}
        .summary h3 {{
            margin: 0 0 10px 0;
            color: #1976D2;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📧 每日邮件摘要报告</h1>
            <p>📅 日期: {datetime.now().strftime('%Y年%m月%d日')}</p>
            <p>⏰ 生成时间: {datetime.now().strftime('%H:%M:%S')}</p>
        </div>

        <div class="summary">
            <h3>📊 今日概览</h3>
            <p style="margin: 5px 0; font-size: 16px;">
                今日共收到 <strong style="color: #2196F3; font-size: 20px;">{len(emails)}</strong> 封邮件
            </p>
            <p style="margin: 5px 0; color: #666;">
                系统通知: {len(system_emails)} 封 | 营销推广: {len(marketing_emails)} 封 | 其他: {len(other_emails)} 封
            </p>
        </div>

        {system_section}
        {other_section}
        {marketing_section}

        <div style="margin-top: 20px; text-align: center; color: #999; font-size: 12px;">
            <p>本报告由邮件自动摘要系统生成 | Powered by AI</p>
        </div>
    </div>
</body>
</html>
"""
