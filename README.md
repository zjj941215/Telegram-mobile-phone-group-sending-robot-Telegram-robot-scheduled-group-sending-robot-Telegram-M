# 黑猫TG手机群发机器人开发文档与安装指南

## 目录

## 联系方式
体验机器人 https://t.me/HM888Bot 

如需技术支持或咨询服务，请联系：https://t.me/hmboos 

1. [项目概述](#项目概述)
2. [功能特性](#功能特性)
3. [技术架构](#技术架构)
4. [环境要求](#环境要求)
5. [安装步骤](#安装步骤)
6. [配置说明](#配置说明)
7. [启动与运行](#启动与运行)
8. [管理员命令](#管理员命令)
9. [用户使用指南](#用户使用指南)
10. [常见问题](#常见问题)

## 项目概述

黑猫手机群发机器人是一款基于Telegram API开发的消息群发工具，支持多账号管理、定时发送、智能调频等功能。系统采用用户等级制度，不同等级用户拥有不同数量的账号配额。机器人支持手机操作，便于随时随地管理群发任务。

## 功能特性

- **多账号管理**：根据用户等级支持5-10个账号同时管理
- **智能群发**：支持群组/私聊消息定向投放
- **定时任务**：设置多轮次自动化消息推送
- **账号管理**：多账号灵活切换与调度
- **智能防护**：内置风控机制，自动调频发送
- **用户等级**：试用用户、VIP用户、高级VIP用户三级权限
- **管理后台**：管理员可添加用户、设置时长、发送广播

## 技术架构

- **编程语言**：Python 3.8+
- **核心框架**：
  - python-telegram-bot：用于机器人交互
  - telethon：用于操作Telegram客户端账号
- **数据存储**：SQLite数据库
- **任务调度**：自定义定时任务系统
- **会话管理**：Telegram session文件管理

## 环境要求

- Python 3.8或更高版本
- 运行内存：至少512MB
- 存储空间：至少1GB
- 操作系统：Linux系统（推荐Ubuntu 18.04+或Debian 10+）
- 网络环境：能稳定访问Telegram API

## 安装步骤

### 1. 准备服务器环境

```bash
# 更新系统
apt update && apt upgrade -y

# 安装Python和依赖
apt install -y python3 python3-pip python3-venv git screen

# 安装SQLite
apt install -y sqlite3
```

### 2. 下载源码

```bash
# 创建工作目录
mkdir -p /root/bot
cd /root/bot

# 上传源码或克隆仓库
# 假设源码已经上传到服务器，按照当前目录结构放置文件
```

### 3. 创建Python虚拟环境

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate
```

### 4. 安装依赖

```bash
# 安装依赖包
pip install -r requirements.txt
```

### 5. 创建目录结构

```bash
# 创建sessions目录
mkdir -p sessions

# 设置执行权限
chmod +x start_bot.sh debug_bot.sh
```

## 配置说明

### 修改配置文件

编辑`config.py`文件，填入您的API信息：

```python
API_ID = 12345  # 从Telegram获取的API ID
API_HASH = "你的API_HASH字符串"  # 从Telegram获取的API哈希
BOT_TOKEN = "你的机器人TOKEN"  # BotFather创建的机器人token
ADMIN_ID = [123456789]  # 管理员用户ID，可以有多个
SESSIONS_DIR = "sessions"  # session文件存储目录
```

### 获取API凭证

1. 访问 https://my.telegram.org/auth 登录您的Telegram账号
2. 进入"API development tools"
3. 创建一个新应用，填写应用信息
4. 获取API_ID和API_HASH
5. 使用BotFather创建机器人并获取BOT_TOKEN

## 启动与运行

### 普通启动

```bash
# 激活虚拟环境(如果尚未激活)
source venv/bin/activate

# 启动机器人
bash start_bot.sh
```

### 调试模式启动

```bash
# 启动调试模式
bash debug_bot.sh
```

### 检查运行状态

```bash
# 查看日志
tail -f bot.log

# 查看调试日志
tail -f debug.log
```

### 停止机器人

```bash
# 查找进程
ps aux | grep python3

# 停止进程
kill -9 进程ID
```

## 数据库结构

系统使用SQLite数据库，主要包含以下表：

1. **users表**：存储用户信息
   - user_id: 用户ID
   - username: 用户名
   - expire_date: 过期时间
   - user_level: 用户等级

2. **sessions表**：存储账号会话信息
   - id: 会话ID
   - user_id: 所属用户ID
   - session_file: 会话文件路径
   - account_name: 账号名称
   - is_active: 是否活跃
   - is_locked: 是否被锁定

3. **scheduled_tasks表**：存储定时任务
   - id: 任务ID
   - user_id: 所属用户ID
   - message_text: 消息内容
   - rounds_per_day: 每天轮数
   - interval_hours: 间隔小时数
   - start_time: 开始时间

## 管理员命令

### 添加用户命令

```
/adduser <用户ID> <天数> <等级>
```

参数说明：
- 用户ID：Telegram用户ID
- 天数：授权天数
- 等级：1(VIP用户，5个账号)或2(高级VIP用户，10个账号)

示例：
```
/adduser 123456789 30 1
```

### 管理员菜单功能

- **添加用户时长**：为用户添加使用时长
- **查看用户列表**：查看所有注册用户
- **发送广播消息**：向所有用户发送通知

## 用户使用指南

### 主要功能

- **开始群发消息**：立即发送消息到多个对话
- **定时发送设置**：创建定时群发任务
- **账号管理**：添加、删除和切换账号
- **个人中心**：查看账户状态和时长

### 账号添加方法

1. **上传Session文件**：上传已有的.session文件
2. **生成Session账号**：输入手机号和验证码生成新账号

### 定时任务设置

1. 选择"定时发送设置"
2. 输入消息内容
3. 设置每天轮数（1-24）
4. 设置间隔小时数（1-24）
5. 选择开始时间
6. 选择要使用的账号

## 常见问题

### 1. 机器人无法启动

**可能原因**：
- Python版本不兼容
- 依赖包未正确安装
- API凭证错误

**解决方法**：
- 确认Python版本是3.8或以上
- 重新安装依赖：`pip install -r requirements.txt`
- 检查config.py中的API凭证是否正确

### 2. 账号验证失败

**可能原因**：
- API请求限制
- 账号被封禁
- 网络连接问题

**解决方法**：
- 等待一段时间后重试
- 检查账号状态
- 确认服务器能够访问Telegram API

### 3. 定时任务未执行

**可能原因**：
- 服务器时区设置错误
- 进程意外终止
- 数据库锁定

**解决方法**：
- 检查服务器时区是否为Asia/Shanghai
- 重启机器人
- 检查debug.log查找错误

## 联系方式
体验机器人 https://t.me/HM888Bot 

如需技术支持或咨询服务，请联系：https://t.me/hmboos 

---

*本文档适用于黑猫手机群发机器人v1.8版本* 