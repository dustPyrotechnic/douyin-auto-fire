# 每日编程名言发送实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 每次任务运行时从 GitHub 编程名言数据源选择当前时区对应的每日名言，并将同一条名言作为所有目标好友的文字消息发送。

**Architecture:** 新增独立的 `app/quotes.py`，负责请求 JSON、校验记录、按日期稳定选择并格式化名言；主流程在打开浏览器前获取一次每日名言，将配置目标中的消息替换为该条文字消息。网络或数据错误直接终止本次任务，禁止使用旧的固定消息静默回退。

**Tech Stack:** Python 3.11 标准库 `urllib`、`json`、`zoneinfo`；现有 pytest/pytest-asyncio 测试体系。

---

### Task 1: 定义每日名言行为测试

**Files:**
- Create: `tests/test_quotes.py`
- Test: `tests/test_quotes.py`

**Steps:**
1. 为有效 JSON 记录测试 `text`、`author` 组合成带作者的发送文本。
2. 为同一日期测试稳定返回同一条名言，为相邻日期测试按日期索引产生可变化选择。
3. 为无效记录、空数据和缺失作者测试抛出明确的名言数据错误。
4. 运行 `pytest tests/test_quotes.py -q`，确认测试因 `app.quotes` 尚不存在而失败。

### Task 2: 实现名言获取器

**Files:**
- Create: `app/quotes.py`

**Steps:**
1. 固定使用 `https://raw.githubusercontent.com/mudroljub/programming-quotes-api/master/data/quotes.json`。
2. 使用标准库请求 JSON，限制请求超时并将网络、JSON、数据结构错误统一转换为 `QuoteError`。
3. 使用 `ZoneInfo(task.timezone)` 对当前日期取值，以 `date.toordinal() % len(quotes)` 稳定选择每日记录。
4. 格式化为 `名言\n—— 作者`，保留数据源的英文内容和作者。
5. 运行 `pytest tests/test_quotes.py -q`，确认测试通过。

### Task 3: 接入发送主流程

**Files:**
- Modify: `app/main.py`
- Modify: `tests/test_main.py`

**Steps:**
1. 添加主流程测试，验证每次运行只获取一次每日名言，并向每个目标发送同一条动态文字消息。
2. 运行该测试确认先失败。
3. 在加载配置后、启动浏览器前获取每日名言；为每个目标构造单条 `Message(type="text")`，不再发送配置中的固定消息。
4. 捕获逻辑保持现有任务异常处理语义；名言获取失败在浏览器启动前抛出，避免部分好友已发送后才发现数据源不可用。
5. 运行主流程测试和现有测试，确认通过。

### Task 4: 更新项目示例和说明

**Files:**
- Modify: `README.md`
- Modify: `config.example.json`
- Modify: `config/tasks.example.json`

**Steps:**
1. 说明每次运行会从数据源按任务时区选择每日编程名言，并作为文字消息发送。
2. 将示例固定消息改成明确的每日名言模式说明，避免用户误以为配置里的固定文字仍会发送。
3. 记录数据源 URL 和网络失败时任务终止的行为。

### Task 5: 验证

**Steps:**
1. 运行 `pytest tests/test_quotes.py tests/test_main.py -q`。
2. 运行完整 `pytest`。
3. 使用真实 GitHub Raw 数据源执行一次只读名言获取烟测，确认返回非空名言和作者。
4. 检查 `git diff`，确认没有修改 Cookie、Storage State 或其他用户本地凭证文件。
