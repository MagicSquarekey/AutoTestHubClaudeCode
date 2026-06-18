# 知道何时停止 / Know When to Stop

> 识别失败模式，及时停止自动尝试，把操作权交还给用户
> Recognize failure patterns, stop auto-attempting, return control to user

## 核心原则 / Core Principle

**用户的手动操作 > AI 的反复重试**
**User's manual action > AI's repeated attempts**

## 触发条件 / Trigger Conditions

当满足以下任一条件时，**立即停止**并请求人工介入：
Stop immediately and request human intervention when any of:

### 快速停止（2次失败即停）/ Quick Stop (2 failures)
- 杀进程 / 重启服务 / Kill process, restart service
- 安装依赖 / 下载资源 / Install dependencies, download resources
- 端口占用 / 网络请求 / Port occupied, network requests
- 权限不足 / 文件被占用 / Permission denied, file locked

### 标准停止（3次失败）/ Standard Stop (3 failures)
- 同一问题连续修复失败 ≥ 3 次 / Same issue fails ≥ 3 times in a row
- 修复一个问题导致另一个问题出现，循环 ≥ 2 次 / Fixing one issue causes another, looping ≥ 2 times
- 同一问题持续未解决超过 10 分钟 / Same issue unresolved for > 10 minutes
- 对修复方案信心不足（需要猜测）/ Low confidence in fix (requires guessing)

## 执行步骤 / Execution Steps

1. **记录尝试** — 每次修复尝试都记录下来
   Record attempts — Log each fix attempt

2. **检测阈值** — 判断是否达到停止条件
   Detect threshold — Check if stop threshold is reached

3. **立即停止** — 不再尝试其他方案
   Stop immediately — No more attempts

4. **清晰汇报** — 告诉用户：
   Clear report — Tell user:
   - 我做了什么 / What I did
   - 为什么失败 / Why it failed
   - 用户需要做什么（具体步骤）/ What user needs to do (specific steps)

## 输出格式 / Output Format

当触发停止时，输出以下内容：
When triggered, output:

```
⚠️ 需要人工介入 / Human intervention needed

**问题描述 / Problem**：
[简述问题 / Brief description]

**已尝试方案 / Attempted solutions**：
1. [方案1] — 失败原因 / Reason
2. [方案2] — 失败原因 / Reason
3. ...

**用户操作步骤 / User action steps**：
1. [具体操作1] / [Specific action 1]
2. [具体操作2] / [Specific action 2]
```

## 示例 / Examples

❌ 错误做法：反复尝试杀进程 10 次
❌ Wrong: Try to kill process 10 times

✅ 正确做法：失败 2 次后说"请在任务管理器中结束 python.exe 进程，然后双击 start.vbs"
✅ Right: After 2 failures, say "Please end python.exe in Task Manager, then double-click start.vbs"

---

*最后更新 / Last Updated: 2026-06-18*