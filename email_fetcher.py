#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QQ邮箱IMAP客户端
用于接收和获取邮件
"""

import imaplib
import email
from email.header import decode_header
from datetime import datetime


class QQEmailFetcher:
    """QQ邮箱IMAP客户端 - 用于接收邮件"""

    IMAP_SERVER = 'imap.qq.com'
    IMAP_PORT = 993

    def __init__(self, email_account, auth_code):
        """初始化邮箱客户端"""
        self.email_account = email_account
        self.auth_code = auth_code
        self.imap = None

    def connect(self):
        """连接到QQ邮箱IMAP服务器"""
        try:
            print(f"正在连接到 {self.IMAP_SERVER}...")
            self.imap = imaplib.IMAP4_SSL(self.IMAP_SERVER, self.IMAP_PORT)
            self.imap.login(self.email_account, self.auth_code)
            print("✓ IMAP登录成功")
            return True
        except Exception as e:
            print(f"✗ IMAP连接失败: {str(e)}")
            return False

    def disconnect(self):
        """断开连接"""
        if self.imap:
            try:
                self.imap.logout()
            except Exception:
                pass

    def decode_str(self, s):
        """解码邮件头部信息"""
        if s is None:
            return ""
        value, charset = decode_header(s)[0]
        if charset:
            try:
                value = value.decode(charset)
            except Exception:
                value = value.decode('utf-8', errors='ignore')
        elif isinstance(value, bytes):
            value = value.decode('utf-8', errors='ignore')
        return str(value)

    def get_email_body(self, msg):
        """获取邮件正文"""
        body = ""

        if msg.is_multipart():
            # 优先查找纯文本，如果没有再使用HTML
            text_parts = []
            html_parts = []

            for part in msg.walk():
                content_type = part.get_content_type()
                disposition = str(part.get('Content-Disposition'))

                # 跳过附件
                if 'attachment' in disposition:
                    continue

                try:
                    payload = part.get_payload(decode=True)
                    if not payload:
                        continue

                    if content_type == 'text/plain':
                        text_parts.append(payload.decode('utf-8', errors='ignore'))
                    elif content_type == 'text/html':
                        html_parts.append(payload.decode('utf-8', errors='ignore'))
                except Exception:
                    continue

            # 优先使用文本，如果没有文本则使用HTML
            if text_parts:
                body = '\n'.join(text_parts)
            elif html_parts:
                # 简单的HTML转文本（去除标签）
                import re
                html_body = '\n'.join(html_parts)
                # 移除script和style标签及内容
                html_body = re.sub(r'<script[^>]*>.*?</script>', '', html_body, flags=re.DOTALL | re.IGNORECASE)
                html_body = re.sub(r'<style[^>]*>.*?</style>', '', html_body, flags=re.DOTALL | re.IGNORECASE)
                # 移除HTML标签
                html_body = re.sub(r'<[^>]+>', ' ', html_body)
                # 解码HTML实体
                import html as html_module
                html_body = html_module.unescape(html_body)
                # 清理多余空白
                html_body = re.sub(r'\s+', ' ', html_body)
                body = html_body.strip()
        else:
            # 非multipart邮件
            try:
                payload = msg.get_payload(decode=True)
                if payload:
                    content_type = msg.get_content_type()
                    decoded = payload.decode('utf-8', errors='ignore')

                    if content_type == 'text/html':
                        # HTML转文本
                        import re
                        import html as html_module
                        decoded = re.sub(r'<script[^>]*>.*?</script>', '', decoded, flags=re.DOTALL | re.IGNORECASE)
                        decoded = re.sub(r'<style[^>]*>.*?</style>', '', decoded, flags=re.DOTALL | re.IGNORECASE)
                        decoded = re.sub(r'<[^>]+>', ' ', decoded)
                        decoded = html_module.unescape(decoded)
                        decoded = re.sub(r'\s+', ' ', decoded)

                    body = decoded.strip()
            except Exception:
                pass

        return body

    def parse_email_date(self, date_str):
        """解析邮件日期字符串为datetime对象"""
        try:
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
        except Exception:
            return None

    def fetch_today_emails(self):
        """获取今天的所有邮件"""
        if not self.imap:
            print("请先连接到邮箱服务器")
            return []

        try:
            self.imap.select('INBOX')

            # 获取本地时区的今天日期
            import time
            local_timezone = time.timezone
            today = datetime.now()
            today_date = today.date()
            today_str = today.strftime('%d-%b-%Y')
            search_criteria = f'SINCE {today_str}'

            print(f"正在搜索 {today.strftime('%Y-%m-%d')} 的邮件...")
            status, messages = self.imap.search(None, search_criteria)

            if status != 'OK':
                print("搜索失败")
                return []

            email_ids = messages[0].split()
            print(f"服务器返回 {len(email_ids)} 封邮件，正在筛选...")

            emails = []
            matched_count = 0

            for email_id in email_ids:
                status, msg_data = self.imap.fetch(email_id, '(RFC822)')
                if status != 'OK':
                    continue

                msg = email.message_from_bytes(msg_data[0][1])
                date_str = msg.get('Date', '')
                email_date = self.parse_email_date(date_str)

                # 调试输出
                subject = self.decode_str(msg.get('Subject', ''))
                print(f"  调试: 邮件「{subject[:30]}」")
                print(f"    原始日期: {date_str}")

                if email_date:
                    # 转换为本地时区的日期（用于比较）
                    # email_date是带时区的datetime，astimezone()会转换为本地时区
                    local_email_date = email_date.astimezone()
                    local_date = local_email_date.date()

                    print(f"    UTC日期: {email_date.date()}")
                    print(f"    本地日期: {local_date}")
                    print(f"    目标日期: {today_date}")
                    print(f"    匹配: {local_date == today_date}")

                    # 使用本地时区的日期进行比较
                    if local_date == today_date:
                        matched_count += 1
                        email_info = {
                            'id': email_id.decode(),
                            'subject': self.decode_str(msg.get('Subject', '')),
                            'from': self.decode_str(msg.get('From', '')),
                            'to': self.decode_str(msg.get('To', '')),
                            'date': date_str,
                            'parsed_date': local_email_date.strftime('%Y-%m-%d %H:%M:%S'),
                            'body': self.get_email_body(msg)
                        }
                        emails.append(email_info)
                else:
                    print(f"    解析失败")

            print(f"✓ 找到 {matched_count} 封今天的邮件")
            return emails

        except Exception as e:
            print(f"✗ 获取邮件时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
