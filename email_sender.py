#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QQ邮箱SMTP客户端
用于发送邮件
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from datetime import datetime


class QQEmailSender:
    """QQ邮箱SMTP客户端 - 用于发送邮件"""

    SMTP_SERVER = 'smtp.qq.com'
    SMTP_PORT = 465

    def __init__(self, email_account, auth_code):
        """初始化邮件发送器"""
        self.email_account = email_account
        self.auth_code = auth_code
        self.smtp = None

    def connect(self):
        """连接到QQ SMTP服务器"""
        try:
            print(f"正在连接到 {self.SMTP_SERVER}...")
            self.smtp = smtplib.SMTP_SSL(self.SMTP_SERVER, self.SMTP_PORT)
            self.smtp.login(self.email_account, self.auth_code)
            print("✓ SMTP登录成功")
            return True
        except Exception as e:
            print(f"✗ SMTP连接失败: {str(e)}")
            return False

    def disconnect(self):
        """断开连接"""
        if self.smtp:
            try:
                self.smtp.quit()
            except Exception:
                pass

    def send_email(self, to_email, subject, content, content_type='html'):
        """发送邮件"""
        if not self.smtp:
            print("请先连接到邮箱服务器")
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_account
            msg['To'] = to_email
            msg['Subject'] = Header(subject, 'utf-8')
            msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
            msg.attach(MIMEText(content, content_type, 'utf-8'))

            print(f"正在发送邮件到 {to_email}...")
            self.smtp.sendmail(self.email_account, to_email, msg.as_string())
            print("✓ 邮件发送成功")
            return True

        except Exception as e:
            print(f"✗ 发送失败: {str(e)}")
            return False
