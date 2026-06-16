# AutoTest Hub 单人落地版

🤖 一款 Windows 开箱即用的单人专属自动化测试工具

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Vue 3](https://img.shields.io/badge/vue-3-brightgreen.svg)](https://vuejs.org/)

---

## 📋 项目概述

AutoTest Hub 是一款面向单人测试工程师的自动化测试工具，支持 Web、Android、iOS、微信小程序等多端测试，提供可视化低代码用例编排、全局元素管理、统一执行引擎、测试报告分析、AI 辅助修复等核心能力。

### 核心特性

- 🎯 **低代码编排**：拖拽式可视化用例编辑，无需编写代码
- 🔄 **多端统一**：一套工具覆盖 Web、Android、iOS、小程序
- 🧠 **智能定位**：多定位符融合降级，元素定位成功率 ≥ 98%
- 📊 **报告分析**：多维度测试结果分析与缺陷取证
- 🤖 **AI 辅助**：自然语言生成用例、智能修复、失败分析

---

## 🚀 快速开始

### 环境要求

- **操作系统**：Windows 10 1903+ / Windows 11
- **Python**：3.11+
- **Node.js**：16+
- **硬件**：CPU i5+ / 内存 8GB+ / 硬盘 20GB+

### 方式一：源码运行（开发调试）

```bash
# 1. 克隆项目
git clone https://github.com/your-username/AutoTestHub.git
cd AutoTestHub

# 2. 安装后端依赖
cd backend
pip install -r requirements.txt

# 3. 启动后端服务
python main.py

# 4. 新终端，安装前端依赖
cd frontend
npm install

# 5. 启动前端开发服务
npm run dev
```

### 方式二：Electron 桌面应用

```bash
# 安装依赖后
cd frontend
npm run electron:dev
```

### 方式三：打包安装包

```bash
cd frontend
npm run electron:build
```

---

## 📁 项目结构

```
AutoTestHub/
├── frontend/                    # 前端 Electron + Vue3 项目
│   ├── src/
│   │   ├── views/              # 页面组件
│   │   ├── components/         # 公共组件
│   │   ├── store/              # Pinia 状态管理
│   │   ├── api/                # 接口调用
│   │   ├── router/             # 路由配置
│   │   ├── layouts/            # 布局组件
│   │   └── utils/              # 工具函数
│   ├── electron/               # Electron 主进程
│   ├── package.json
│   └── vite.config.js
├── backend/                    # 后端 Python 服务
│   ├── app/
│   │   ├── api/               # 接口层
│   │   │   ├── endpoints/     # API 端点
│   │   │   └── router.py      # 路由注册
│   │   ├── service/           # 业务逻辑层
│   │   ├── engine/            # 执行引擎核心
│   │   ├── driver/            # 各端驱动封装
│   │   ├── models/            # 数据模型
│   │   ├── core/              # 核心配置
│   │   └── utils/             # 工具类
│   ├── plugins/               # 插件扩展
│   │   └── keywords/          # 自定义关键字
│   ├── data/                  # 本地数据存储
│   ├── logs/                  # 日志文件
│   ├── main.py                # 服务入口
│   ├── requirements.txt
│   └── .env.example
├── docs/                      # 文档
├── private/                   # 私有文件（不提交到 GitHub）
├── .gitignore
├── CLAUDE.md
└── README.md
```

---

## 🔧 技术栈

| 层级 | 技术选型 | 说明 |
|------|----------|------|
| 桌面客户端 | Electron + Vue3 + Element Plus | 前端生态成熟，Windows 适配好 |
| 执行内核 | Python 3.11 + FastAPI | 自动化生态完善，开发效率高 |
| 本地存储 | SQLite | 文件级数据库，无需安装服务 |
| Web 驱动 | Playwright | 自动管理浏览器驱动，稳定性好 |
| Android 驱动 | Appium + uiautomator2 | 开源成熟，兼容性好 |
| iOS 驱动 | tidevice + WDA | Windows 原生直连 iOS |
| 小程序驱动 | miniprogram-automator | 官方原生接口 |
| OCR / 图像 | PaddleOCR + OpenCV | 开源免费，中文识别准确 |

---

## 📖 功能模块

### 1. 用例管理
- 用例 CRUD、分组、标签、搜索
- JSON 格式导入导出
- 版本历史与回滚

### 2. 可视化编排
- 拖拽关键字到画布
- 条件分支、循环执行
- 数据驱动与参数化
- 单步调试、断点执行

### 3. 元素管理
- 多端定位符绑定
- 智能定位降级
- 元素健康巡检
- 批量同步

### 4. 执行引擎
- 统一执行内核
- 智能等待机制
- 异常自动处理
- 多任务并行

### 5. 测试报告
- 总览报告
- 步骤级详情
- 失败自动分类
- 趋势分析

### 6. 任务调度
- Cron 定时执行
- 用例集管理
- 消息通知（飞书/企微/邮件）

### 7. AI 辅助
- 自然语言生成用例
- 元素智能修复
- 失败根因分析

---

## 🔌 API 接口

后端服务启动后，默认在 `http://127.0.0.1:8686` 提供 HTTP 接口。

### 核心接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/case/list` | GET | 获取用例列表 |
| `/api/case/create` | POST | 创建用例 |
| `/api/element/list` | GET | 获取元素列表 |
| `/api/exec/run` | POST | 执行用例 |
| `/api/exec/status/{task_id}` | GET | 查询任务状态 |
| `/api/report/list` | GET | 获取报告列表 |
| `/api/device/list` | GET | 获取设备列表 |
| `/api/scheduler/suites` | GET | 获取用例集 |
| `/api/system/configs` | GET | 获取系统配置 |

---

## 🔒 安全规范

### 绝对禁止

- ❌ 不得提交 API Key、密码、密钥
- ❌ 不得提交 .env 文件
- ❌ 不得在代码中硬编码任何凭证
- ❌ 不得提交测试账号、密码、自动化操作细节

### 敏感信息处理

- 使用 `.env` 文件存储敏感配置
- `.gitignore` 已排除敏感文件
- 提供 `.env.example` 模板文件
- 敏感数据使用 AES 加密存储

---

## 📚 文档

| 文档 | 说明 |
|------|------|
| [软件需求规格说明书](private/document/《AutoTest%20Hub%20单人落地版%20%20软件需求规格说明书》.md) | 详细需求文档 |
| [系统概要设计说明书](private/document/《AutoTest%20Hub%20单人落地版%20系统概要设计说明书》.md) | 技术架构设计 |
| [用户操作手册](private/document/《AutoTest%20Hub%20单人落地版%20用户操作手册》.md) | 使用指南 |
| [运维与故障排查手册](private/document/《AutoTest%20Hub%20单人落地版%20运维与故障排查手册》.md) | 运维指南 |
| [验收测试用例清单](private/document/《AutoTest%20Hub%20单人落地版%20验收测试用例清单》.md) | 验收标准 |

---

## 🤝 贡献指南

这是一个单人开发项目，欢迎提出建议和反馈。

---

## 📄 许可证

MIT License

---

*最后更新：2026-06-16*
*维护者：AI 协作开发团队*
