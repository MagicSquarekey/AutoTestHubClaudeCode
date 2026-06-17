# Bilingual Comments 中英文注释规范

> 所有文件、代码、文档必须使用中英文双语注释

## 触发条件
- 创建新文件时
- 编写代码注释时
- 编写文档时
- 用户说"加注释"、"注释"时

## 注释规范

### 代码注释格式

所有注释使用 `中文 / English` 格式，中文在前，英文在后，用 `/` 分隔。

**Python：**
```python
# 初始化数据库连接 / Initialize database connection
def init_db():
    """创建数据表 / Create database tables"""
    pass
```

**JavaScript / Vue：**
```javascript
// 获取用例列表 / Get test case list
const fetchCases = async () => { ... }
```

**HTML / Vue Template：**
```html
<!-- 侧边栏导航 / Sidebar navigation -->
<el-aside>...</el-aside>
```

**CSS / SCSS：**
```css
/* 主内容区域 / Main content area */
.main-content { ... }
```

**Batch / CMD：**
```bat
:: 清理旧进程 / Clean up old processes
taskkill /F /PID %a
```

**VBScript：**
```vbs
' 检查虚拟环境 / Check virtual environment
If Not fso.FileExists(pythonExe) Then
```

**PowerShell：**
```powershell
# 获取项目根目录 / Get project root directory
$RootDir = Split-Path -Parent ...
```

### 文件头注释

每个文件头部必须有文件说明注释：

**Python：**
```python
# -*- coding: utf-8 -*-
"""
数据库模型定义 / Database model definitions
@Function: 定义系统所有数据表结构 / Define all database table structures
"""
```

**JavaScript / Vue：**
```javascript
/**
 * 用例编辑页面 / Test case edit page
 * @Function: 用例的创建和编辑 / Create and edit test cases
 */
```

**Batch：**
```bat
@echo off
:: AutoTest Hub 一键启动脚本 / AutoTest Hub one-click startup script
:: 后台启动所有服务，自动打开浏览器 / Start all services in background, auto-open browser
```

### 注释内容要求

| 场景 | 要求 |
|------|------|
| 函数/方法 | 必须有 docstring，说明功能、参数、返回值 |
| 类 | 必须有 docstring，说明职责 |
| 复杂逻辑 | 必须有行内注释，说明意图 |
| 魔法数字/字符串 | 必须有注释，说明含义 |
| 文件头 | 必须有文件说明和 @Function |
| 配置项 | 必须有注释，说明用途 |

### 不需要注释的情况

- 简单的变量赋值（如 `name = "test"`）
- 明显的代码（如 `return True`）
- 已有清晰的函数名（如 `get_user_by_id`）

## 检查清单

新写或修改代码时，确认：
- [ ] 文件头有中英文说明
- [ ] 函数有中英文 docstring
- [ ] 复杂逻辑有中英文行内注释
- [ ] 注释格式：`中文 / English`

## 示例

```python
# -*- coding: utf-8 -*-
"""
用例服务层 / Test case service layer
@Function: 处理用例的增删改查业务逻辑 / Handle CRUD business logic for test cases
"""

from app.models.test_case import TestCase


# @Function: 创建用例 / Create a test case
def create_case(data: dict) -> TestCase:
    """
    创建新的测试用例 / Create a new test case

    Args:
        data: 用例数据 / Case data

    Returns:
        创建的用例对象 / Created case object
    """
    # 参数校验 / Validate parameters
    if not data.get("name"):
        raise ValueError("用例名称不能为空 / Case name is required")

    # 写入数据库 / Save to database
    case = TestCase(**data)
    return case
```
