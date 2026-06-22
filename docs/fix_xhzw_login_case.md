# xhzw 登录用例修复指南

## 问题描述

录制转化的登录用例存在以下问题：
1. 数据填写不正确（手机号、密码值错误）
2. 验证码识别功能未使用

## 修正后的测试步骤

以下是修正后的完整测试步骤 JSON，可以直接在用例编辑页面替换：

```json
[
  {
    "id": "step_1",
    "keyword": "open_url",
    "name": "打开登录页",
    "params": {
      "url": "http://sxzw.xhbms.cn/login"
    },
    "timeout": 30,
    "retry_count": 0,
    "on_error": "stop",
    "disabled": false,
    "remark": "打开目标登录页面"
  },
  {
    "id": "step_2",
    "keyword": "wait_for_element",
    "name": "等待页面加载",
    "params": {
      "element": "input[placeholder*='账号'], input[placeholder*='手机号']"
    },
    "timeout": 10,
    "retry_count": 0,
    "on_error": "stop",
    "disabled": false,
    "remark": "等待账号输入框出现，替代固定5秒等待"
  },
  {
    "id": "step_3",
    "keyword": "click",
    "name": "关闭弹窗/同意协议",
    "params": {
      "element": "button:has-text('同意'), button:has-text('关闭'), .ant-modal-close"
    },
    "timeout": 5,
    "retry_count": 1,
    "on_error": "continue",
    "disabled": false,
    "remark": "如有弹窗则关闭，没有则跳过（设置失败继续）"
  },
  {
    "id": "step_4",
    "keyword": "input_text",
    "name": "输入账号",
    "params": {
      "element": "input[placeholder*='账号'], input[placeholder*='手机号'], input[type='text']:first-of-type",
      "value": "18325570926"
    },
    "timeout": 10,
    "retry_count": 0,
    "on_error": "stop",
    "disabled": false,
    "remark": "输入正确的手机号/账号"
  },
  {
    "id": "step_5",
    "keyword": "input_text",
    "name": "输入密码",
    "params": {
      "element": "input[type='password'], input[placeholder*='密码']",
      "value": "123qwe"
    },
    "timeout": 10,
    "retry_count": 0,
    "on_error": "stop",
    "disabled": false,
    "remark": "输入正确的密码"
  },
  {
    "id": "step_6",
    "keyword": "solve_captcha",
    "name": "识别并输入验证码",
    "params": {
      "captcha_selector": "img.captcha, img[src*='captcha'], img[src*='verify'], .captcha-img img",
      "input_selector": "input[placeholder*='验证码'], input[name*='captcha'], input[name*='verify']",
      "expected_length": 4,
      "max_retries": 3
    },
    "timeout": 30,
    "retry_count": 1,
    "on_error": "stop",
    "disabled": false,
    "remark": "使用OCR识别验证码并自动输入"
  },
  {
    "id": "step_7",
    "keyword": "click",
    "name": "点击登录按钮",
    "params": {
      "element": "button:has-text('登录'), button[type='submit'], .ant-btn-primary"
    },
    "timeout": 10,
    "retry_count": 0,
    "on_error": "stop",
    "disabled": false,
    "remark": "点击登录提交"
  },
  {
    "id": "step_8",
    "keyword": "wait_for_element",
    "name": "等待登录成功",
    "params": {
      "element": ".user-info, .avatar, [class*='dashboard'], [class*='home']"
    },
    "timeout": 15,
    "retry_count": 0,
    "on_error": "stop",
    "disabled": false,
    "remark": "等待登录成功后的元素出现"
  },
  {
    "id": "step_9",
    "keyword": "assert_url",
    "name": "验证登录成功",
    "params": {
      "expected": "/dashboard, /home, /index"
    },
    "timeout": 10,
    "retry_count": 0,
    "on_error": "stop",
    "disabled": false,
    "remark": "断言URL包含登录成功后的路径"
  }
]
```

## 关键改进点

### 1. 数据修正
- 账号：`18325570926`（正确的手机号）
- 密码：`123qwe`（正确的密码）

### 2. 验证码识别
添加了 `solve_captcha` 关键字步骤，参数说明：
- `captcha_selector`: 验证码图片选择器（使用多个可能的选择器）
- `input_selector`: 验证码输入框选择器
- `expected_length`: 验证码长度（默认4位）
- `max_retries`: 最大重试次数

### 3. 智能等待优化
- 使用 `wait_for_element` 替代固定 `wait` 5秒
- 等待特定元素出现，而非固定时间
- 大幅缩短执行时间

### 4. 错误处理增强
- 弹窗关闭步骤设置 `on_error: "continue"`，没有弹窗时继续执行
- 添加重试机制

## 如何找到正确的验证码选择器

如果默认选择器不工作，请按以下步骤找到正确的选择器：

1. 打开浏览器，访问 `http://sxzw.xhbms.cn/login`
2. 按 `F12` 打开开发者工具
3. 使用元素选择器（左上角箭头图标）点击验证码图片
4. 查看元素的 HTML 代码，找到：
   - **验证码图片**：通常是 `<img>` 标签，查看 `src`、`class`、`id` 属性
   - **验证码输入框**：通常是 `<input>` 标签，查看 `placeholder`、`name`、`id` 属性

### 常见验证码选择器模式

```css
/* 验证码图片 */
img.captcha
img[src*='captcha']
img[src*='verify']
img[src*='code']
.captcha-img img
#captchaImg
.verify-code img

/* 验证码输入框 */
input[placeholder*='验证码']
input[name*='captcha']
input[name*='verify']
input[name*='code']
#captchaInput
.verify-code input
```

## 修改用例的方法

### 方法一：通过 UI 修改（推荐）

1. 打开 AutoTest Hub 前端页面
2. 进入「用例管理」→ 找到「xhzw 登录」用例
3. 点击编辑进入用例编辑页面
4. 删除所有现有步骤
5. 按照上面的 JSON 逐步添加新步骤：
   - 从左侧关键字库拖拽关键字到中间画布
   - 在右侧配置面板填写参数
6. 保存用例

### 方法二：直接修改数据库

如果熟悉数据库操作，可以直接更新 SQLite 数据库：

```sql
-- 找到用例 ID
SELECT id, case_name FROM test_case WHERE case_name = 'xhzw 登录';

-- 更新步骤（将 <CASE_ID> 替换为实际 ID）
UPDATE test_case
SET steps = '<上面的JSON字符串>',
    update_time = datetime('now'),
    version = version + 1
WHERE id = <CASE_ID>;
```

## 调试建议

1. **先测试验证码选择器**：
   - 在浏览器控制台测试选择器是否能选中元素
   - 示例：`document.querySelector('img.captcha')`

2. **分步调试**：
   - 先禁用验证码步骤，确保其他步骤正常
   - 再单独测试验证码识别功能

3. **查看执行日志**：
   - 调试运行时查看每个步骤的详细日志
   - 如果验证码识别失败，检查 OCR 服务是否正常

## 常见问题

### Q1: 验证码识别失败怎么办？
A: 尝试以下方法：
- 调整 `captcha_selector` 为更精确的选择器
- 增加 `max_retries` 次数
- 检查验证码图片是否清晰
- 查看 OCR 服务日志

### Q2: 元素找不到怎么办？
A: 
- 使用浏览器开发者工具确认元素选择器
- 尝试不同的选择器（id > name > class > xpath）
- 增加 `timeout` 等待时间

### Q3: 登录后页面跳转不对？
A:
- 检查 `assert_url` 的 `expected` 值是否正确
- 查看实际跳转的 URL，更新断言条件
