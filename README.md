# 邮件提醒助手

自动获取QQ邮箱当天邮件，使用Gemini AI生成智能摘要，并发送到指定邮箱。

## ✨ 功能特性

- 📥 自动获取QQ邮箱当天所有邮件
- 🤖 使用Gemini AI生成智能摘要报告
- 📤 自动发送HTML格式摘要到指定邮箱
- ⏰ GitHub Actions定时任务（默认每天北京时间23:50执行）
- 🔐 安全的环境变量配置

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/zstar1003/EmailHelper.git
cd EmailHelper
```

### 2. 安装依赖

```bash
uv sync
```

### 3. 配置环境变量

参考`.env.example`文件，创建并编辑 `.env` 文件。

#### 获取QQ邮箱授权码：
1. 登录 [QQ邮箱](https://mail.qq.com)
2. 设置 → 账户 → POP3/IMAP/SMTP服务
3. 开启 IMAP/SMTP 服务
4. 生成授权码（需要短信验证）

#### 获取Gemini API Key：
1. 访问 [Google AI Studio](https://aistudio.google.com/app/apikey)
2. 创建API密钥
3. 复制密钥到 `.env` 文件

### 4. 本地测试运行

```bash
python main.py
```

## ⚙️ GitHub Actions 自动化配置

### 1. 配置GitHub Secrets

进入GitHub仓库设置：`Settings` → `Secrets and variables` → `Actions` → `New repository secret`

添加以下4个密钥：

| 名称 | 值 |
|-----|---|
| `QQ_EMAIL` | 你的QQ邮箱 |
| `QQ_AUTH_CODE` | QQ邮箱授权码 |
| `RECIPIENT_EMAIL` | 接收摘要的邮箱 |
| `GEMINI_API_KEY` | Gemini API密钥 |

### 2. 启用GitHub Actions

1. 进入仓库的 `Actions` 标签页
2. 启用 Workflows
3. 找到 "Daily Email Summary" workflow
4. 点击 "Enable workflow"

### 3. 定时任务说明

- **自动执行**：每天北京时间 23:50（UTC 15:50）
- **手动触发**：可在 Actions 页面手动运行 workflow
- **执行内容**：
  1. 获取当天QQ邮箱所有邮件
  2. 使用Gemini AI生成摘要
  3. 发送摘要到指定邮箱

### 4. 查看执行日志

`Actions` → `Daily Email Summary` → 选择运行记录 → 查看详细日志

## 🔧 自定义配置

### 修改定时任务时间

编辑 `.github/workflows/daily-email-summary.yml`：

```yaml
schedule:
  # 修改cron表达式，格式：分 时 日 月 周
  - cron: '50 15 * * *'  # UTC时间
```

北京时间转UTC时间：北京时间 - 8小时

示例：
- 北京时间 23:50 = UTC 15:50 → `'50 15 * * *'`
- 北京时间 08:00 = UTC 00:00 → `'0 0 * * *'`

### 修改Gemini模型

编辑 `utils.py` 中的 `GeminiSummarizer` 类：

```python
self.model = genai.GenerativeModel('gemini-2.0-flash-exp')  # 可更换为其他模型
```

## 📄 许可证

MIT License