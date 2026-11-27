直接贴。这是把前面已确认的设计整理成文件，**不是新设计**。贴完你要能指着每一段说出“为什么这么填”，否则 W3 写代码时会变成抄。

```markdown
# API Checklist

技术栈：FastAPI + SQLite。所有接口前缀省略，本地为 `http://127.0.0.1:8000`。
约定：成功返回 JSON；失败返回 `{"detail": "..."}`；`status` 后端固定写 `active`，不接收前端传。

## 总览

| # | 方法 + 路径 | 作用 | 成功码 | 失败码 |
|---|---|---|---|---|
| 1 | POST /goals | 创建学习目标 | 201 | 400 |
| 2 | GET /goals | 列出所有目标 | 200 | — |
| 3 | POST /logs | 给某个目标记一笔工作量 | 201 | 400 / 404 |
| 4 | GET /goals/{id}/logs | 列出某目标的所有记录 | 200 | 404 |
| 5 | GET /goals/{id}/summary | 查某目标的总工作量和记录天数 | 200 | 404 |
| 6 | PATCH /goals/{id}/status | 修改目标状态 | 200 | 400 / 404 |
| 7 | DELETE /goals/{id}?with_logs= | 删除目标，可选是否连带删除记录 | 204 | 404 / 409 |
| 8 | POST /ai/feedback | 生成 AI 反馈（W3 为 mock） | 200 | 404 |

---

## 接口 1：POST /goals

- **作用**：创建一个学习目标。
- **请求参数**：

| 字段 | 类型 | 必填 | 校验 |
|---|---|---|---|
| name | string | 是 | 非空，长度 1–50 |
| target_amount | number | 否 | 若填，必须 > 0 |
| unit | string | 否 | 长度 ≤ 10 |

- **成功返回**（201）：
```json
{"id": 1, "name": "德语 A1", "target_amount": 60, "unit": "小时", "status": "active", "created_at": "2026-11-10 14:00:00"}
```

- **失败**：
  - 400：`name` 为空 → `{"detail": "name 不能为空"}`
  - 400：`target_amount` ≤ 0 → `{"detail": "target_amount 必须大于 0"}`

- **对应 SQL**：
```sql
INSERT INTO goals (name, target_amount, unit) VALUES (?, ?, ?)
```

- **业务规则**：`status` 不接收前端传，后端固定写 `'active'`；`created_at` 用表默认值；返回新目标的完整字段。

---

## 接口 2：GET /goals

- **作用**：列出所有目标。
- **请求参数**：无。

- **成功返回**（200）：
```json
[
  {"id": 1, "name": "德语 A1", "target_amount": 60, "unit": "小时", "status": "active", "created_at": "..."},
  {"id": 2, "name": "保研资料", "target_amount": null, "unit": null, "status": "active", "created_at": "..."}
]
```

- **失败**：无。

- **对应 SQL**：
```sql
SELECT id, name, target_amount, unit, status, created_at FROM goals ORDER BY created_at DESC
```

- **业务规则**：默认返回全部状态（含 `completed` / `abandoned`），前端自己过滤；不做分页；不返回汇总数字，汇总由接口 5 单独提供，避免 N+1 查询。

---

## 接口 3：POST /logs

- **作用**：给某个目标记一笔工作量。首页和详情页共用，`goal_id` 由前端传。
- **请求参数**：

| 字段 | 类型 | 必填 | 校验 |
|---|---|---|---|
| goal_id | integer | 是 | 必须存在于 `goals`，否则 404 |
| log_date | string | 是 | 严格 `YYYY-MM-DD` |
| amount | number | 是 | 必须 > 0 |
| note | string | 否 | 长度 ≤ 200 |

- **成功返回**（201）：
```json
{"id": 10, "goal_id": 1, "log_date": "2026-11-10", "amount": 2.0, "note": "背单词"}
```

- **失败**：
  - 400：`log_date` 不是 `YYYY-MM-DD` → `{"detail": "log_date 格式必须是 YYYY-MM-DD"}`
  - 400：`amount` ≤ 0 → `{"detail": "amount 必须大于 0"}`
  - 404：`goal_id` 不存在 → `{"detail": "目标不存在"}`

- **对应 SQL**：
```sql
SELECT id FROM goals WHERE id = ?
INSERT INTO logs (goal_id, log_date, amount, note) VALUES (?, ?, ?, ?)
```

- **业务规则**：先查 `goals` 是否存在，不存在主动返回 404，不靠外键报错变 500；同一天允许多次记录，汇总时合并；W3 不做防重复提交，W6 前端加按钮禁用。

---

## 接口 4：GET /goals/{id}/logs

- **作用**：列出某个目标的所有记录。
- **请求参数**：

| 位置 | 字段 | 类型 | 必填 |
|---|---|---|---|
| 路径 | id | integer | 是 |

- **成功返回**（200）：
```json
[
  {"id": 10, "goal_id": 1, "log_date": "2026-11-11", "amount": 3.0, "note": "复习"},
  {"id": 9, "goal_id": 1, "log_date": "2026-11-10", "amount": 2.0, "note": "背单词"}
]
```

- **失败**：
  - 404：目标不存在 → `{"detail": "目标不存在"}`

- **对应 SQL**：
```sql
SELECT id FROM goals WHERE id = ?
SELECT id, goal_id, log_date, amount, note FROM logs WHERE goal_id = ? ORDER BY log_date DESC, created_at DESC
```

- **业务规则**：先查目标是否存在，不存在返回 404，不返回空数组（空数组无法区分“目标不存在”和“目标存在但没记录”）；按 `log_date` 倒序，同一天再按 `created_at` 倒序。

---

## 接口 5：GET /goals/{id}/summary

- **作用**：查某个目标的总工作量和记录天数。
- **请求参数**：

| 位置 | 字段 | 类型 | 必填 |
|---|---|---|---|
| 路径 | id | integer | 是 |

- **成功返回**（200）：
```json
{"goal_id": 1, "total_amount": 6.5, "days": 2, "status": "active"}
```

- **失败**：
  - 404：目标不存在 → `{"detail": "目标不存在"}`

- **对应 SQL**：
```sql
SELECT status FROM goals WHERE id = ?
SELECT SUM(amount) AS total_amount, COUNT(DISTINCT log_date) AS days FROM logs WHERE goal_id = ? GROUP BY goal_id
```

- **业务规则**：目标存在但无记录时，返回 `{"goal_id": 1, "total_amount": 0, "days": 0, "status": "active"}`，不是 404 也不是 null；`SUM` 在空集上返回 `NULL`，代码里要 `if total is None: total = 0`；`days` 用 `COUNT(DISTINCT log_date)`，同一天多次只算一天。

---

## 接口 6：PATCH /goals/{id}/status

- **作用**：修改目标状态（标记完成或放弃）。
- **请求参数**：

| 位置 | 字段 | 类型 | 必填 | 校验 |
|---|---|---|---|---|
| 路径 | id | integer | 是 | 目标必须存在 |
| 请求体 | status | string | 是 | 只能是 `active` / `completed` / `abandoned` |

- **成功返回**（200）：
```json
{"id": 1, "status": "completed"}
```

- **失败**：
  - 400：`status` 不在枚举内 → `{"detail": "status 只能是 active/completed/abandoned"}`
  - 404：目标不存在 → `{"detail": "目标不存在"}`

- **对应 SQL**：
```sql
SELECT id FROM goals WHERE id = ?
UPDATE goals SET status = ? WHERE id = ?
```

- **业务规则**：先查目标是否存在，再校验枚举值；只改 `status`，不动其他字段；返回修改后的 id 和 status。

---

## 接口 7：DELETE /goals/{id}?with_logs=

- **作用**：删除目标，可选是否连带删除该目标的记录。
- **请求参数**：

| 位置 | 字段 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|---|
| 路径 | id | integer | 是 | — | 目标 id |
| 查询 | with_logs | boolean | 否 | false | `true` = 连记录一起删；`false` = 只删目标 |

- **成功返回**（204）：无响应体。

- **失败**：
  - 404：目标不存在 → `{"detail": "目标不存在"}`
  - 409：`with_logs=false` 且目标有记录 → `{"detail": "该目标有 3 条记录，不能单独删除；请选择连记录一起删除"}`

- **对应 SQL**：
```sql
-- 先查目标存在
SELECT id FROM goals WHERE id = ?

-- with_logs=true：两步在同一个事务里
DELETE FROM logs WHERE goal_id = ?
DELETE FROM goals WHERE id = ?

-- with_logs=false：先数记录
SELECT COUNT(*) FROM logs WHERE goal_id = ?
-- count > 0 → 409，不执行 DELETE
DELETE FROM goals WHERE id = ?
```

- **业务规则**：`with_logs=true` 时先删 logs 再删 goals，用 `with conn:` 包住，任一失败整体回滚；`with_logs=false` 时先数记录，有记录返回 409，不依赖数据库 RESTRICT 报错变 500；前端弹窗两个选项分别映射到 `false` / `true`。

---

## 接口 8：POST /ai/feedback

- **作用**：为某个目标生成 AI 反馈。W3 返回固定假数据，W5 换成真实 DeepSeek。
- **请求参数**：

| 字段 | 类型 | 必填 | 校验 |
|---|---|---|---|
| goal_id | integer | 是 | 必须存在于 `goals`，否则 404 |

- **成功返回**（200，W3 mock）：
```json
{"goal_id": 1, "feedback": "本周保持得不错，继续按计划推进。", "source": "mock"}
```

- **失败**：
  - 404：目标不存在 → `{"detail": "目标不存在"}`

- **对应 SQL**（W3）：
```sql
SELECT id FROM goals WHERE id = ?
```

- **业务规则**：W3 不调用任何外部 API，不查 logs，直接返回固定 JSON；W5 把 `feedback` 换成 DeepSeek 返回文本，`source` 改 `"deepseek"`；调用失败时 `try/except` 降级返回固定文案，`source` 标 `"fallback"`，主流程不受影响；不做缓存，每次点都重新生成。

---

## 砍掉清单（W8 答辩主动讲）

- 不做用户系统 / 注册登录：单人使用，JWT 对验收无增量。
- 不做 `GET /goals/{id}`：列表接口已返回全部字段，详情页用列表数据 + 记录/汇总接口。
- 不做编辑目标 / 编辑记录：W6 历史记录范围，W3 不做。
- 不做 AI 反馈缓存：演示频率低，缓存复杂度不值得。
- 不做分页：数据量小，W3 不需要。
