# 临时任务管理

> 管理临时方案执行和临时脚本运行，执行完毕后自动清理临时文件

## 触发条件

### 临时方案执行
- 用户说"制定临时方案并执行"
- 用户说"临时方案"
- 用户说"plan and execute"
- 用户说"执行完删除"相关意图
- **自动触发**：发现系统自动生成的分析文件时

### 临时脚本管理
- 用户说"运行临时脚本"
- 用户说"测试脚本"
- 用户说"临时测试"
- 用户提到 `_` 开头的 Python 文件

## 执行步骤

### 临时方案执行

#### 1. 制定方案
- 与用户对话，理解需求
- 制定执行计划
- 将计划保存到 `.claude/tmp/` 目录（文件名格式：`plan-{timestamp}.md`）

#### 2. 执行方案
- 按计划逐步执行
- 每步执行后记录结果
- 遇到问题及时与用户沟通

#### 3. 执行完毕清理
- 确认所有步骤完成
- **清理项目根目录的系统自动生成文件**
- 删除 `.claude/tmp/` 目录下的临时计划文件
- 向用户汇报执行结果和清理情况

### 临时脚本管理

#### 1. 识别临时脚本
临时脚本的特征：
- 文件名以 `_` 开头（如 `_check.py`, `_fix.py`, `_patch.py`）
- 位于项目根目录
- 不是正式的测试文件（不在 `tests/` 目录）

#### 2. 运行脚本
```bash
python <script_name>.py
```

#### 3. 记录输出
- 保存脚本输出到 `private/logs/` 目录
- 文件名格式：`<script_name>_<timestamp>.log`

#### 4. 删除脚本
```powershell
Remove-Item -Path "<script_name>.py" -Force
```

#### 5. 确认结果
向用户报告：
- 脚本执行状态（成功/失败）
- 输出摘要
- 脚本已删除确认

## 临时文件管理

### 需要清理的文件类型

#### 1. 系统自动生成的分析文件
- **位置**：项目根目录
- **命名格式**：`{中文摘要}-{时间戳}.md`
- **示例**：
  ```
  现在我对全貌有清晰认识了...-2026-06-18T05-18-24.md
  现在我对整个体系有完整了解了...-2026-06-18T05-15-46.md
  ```
- **特征**：文件名包含中文 + ISO时间戳格式

#### 2. 临时计划文件
- **位置**：`.claude/tmp/`
- **命名格式**：`plan-{timestamp}.md`

#### 3. 后端测试文件
- **位置**：`backend/`
- **文件类型**：
  - `create_*.py` — 测试创建脚本
  - `test_*.png` / `test_*.jpg` — 测试图片
  - `test_*.py` — 临时测试脚本
- **特征**：不在 `tests/` 目录下的测试相关文件

#### 4. 执行日志
- **位置**：`.claude/tmp/`
- **命名格式**：`execution-log-{timestamp}.md`

#### 4. 脚本输出日志
- **位置**：`private/logs/`
- **命名格式**：`<script_name>_<timestamp>.log`

#### 5. 临时脚本文件
- **位置**：项目根目录
- **命名格式**：`_*.py`

### 清理命令

```powershell
# 清理系统自动生成的分析文件
Get-ChildItem -Path "." -Filter "*-202*.md" | Remove-Item -Force

# 清理临时计划文件
Remove-Item -Path ".claude/tmp/plan-*.md" -Force -ErrorAction SilentlyContinue

# 清理执行日志
Remove-Item -Path ".claude/tmp/execution-log-*.md" -Force -ErrorAction SilentlyContinue

# 清理脚本输出日志
Remove-Item -Path "private/logs/*.log" -Force -ErrorAction SilentlyContinue

# 清理临时脚本文件
Remove-Item -Path "_*.py" -Force -ErrorAction SilentlyContinue

# 清理后端测试文件
Remove-Item -Path "backend/create_*.py", "backend/test_*.png", "backend/test_*.jpg", "backend/test_*.py" -Force -ErrorAction SilentlyContinue
```

### 清理规则
- 执行成功：删除所有临时文件
- 执行失败：保留临时文件供用户查看，提示用户手动删除或确认删除
- 用户主动要求保留：不删除

## 防止再次生成

在 `.gitignore` 中添加排除规则：
```gitignore
# 排除系统自动生成的临时分析文件
*-202*.md

# 排除临时目录
.claude/tmp/
```

## 示例

### 临时方案执行示例
```
用户：制定临时方案并执行添加日志功能

AI：
1. 与用户讨论日志需求
2. 制定执行计划，保存到 `.claude/tmp/plan-20260617.md`
3. 按计划执行：
   - 创建日志配置文件
   - 添加日志装饰器
   - 测试日志功能
4. 执行完毕：
   - 清理项目根目录的临时分析文件
   - 删除 `.claude/tmp/plan-20260617.md`
   - 报告：已完成日志功能添加，所有临时文件已清理
```

### 临时脚本管理示例
```
用户：运行 `_check_i18n.py`

AI：
1. 执行 `python _check_i18n.py`
2. 保存输出到 `private/logs/check_i18n_20260617.log`
3. 删除 `_check_i18n.py`
4. 报告结果：
   - 脚本执行成功
   - 输出摘要：发现 3 个未翻译的字符串
   - 脚本已删除确认
```

## 注意事项

- 如果脚本执行失败，**不要删除**，保留供调试
- 所有日志保存在 `private/logs/`（已在 .gitignore 中）
- 长期使用的脚本应移动到 `private/scripts/`
- 临时文件清理时需谨慎，避免误删重要文件
- 对于系统自动生成的分析文件，清理前可先查看内容确认

---

*最后更新：2026-06-18*
*维护者：AI 协作开发团队*