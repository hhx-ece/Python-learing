# reference/ —— 阶段一的「答案卷」

这是 [Python学习路线图.md](../Python学习路线图.md) 阶段一的完整参考实现，**12 个单元测试全绿**。

> **它是 v1.7 的形态，不是你现在要抄的目标。** 你的 v1.2 应该按 [代码诊断-v1.2.md](../代码诊断-v1.2.md) 的阶梯走：v1.3 → v1.4 → v1.5 → v1.6 → v1.7，每版只加一个概念，写完再看对应那一步的答案。现在照抄这一份等于跳级。

用途：卡住 30 分钟以上再看。对着 diff 自己的代码，比抄一遍有用十倍。

## 怎么跑

```powershell
cd reference
python main.py                          # 启动控制台程序
python -m unittest discover -s tests -v # 跑测试
```

需要 Python 3.10+（用到 `X | None` 类型写法）。数据存在 `data/students.json`，删掉它就从空库开始。

## 文件对应关系

| 文件 | 层 | 职责 | 不该出现的东西 |
|---|---|---|---|
| `models.py` | Model | `Student` 长什么样、什么算合法 | `input` / `print` / `json` |
| `storage.py` | Repository | dict 文档 ↔ 文件，原子写入 | `Student` / 业务规则 |
| `service.py` | Service | 增删改查、ID 分配、统计 | `input` / `print` |
| `cli.py` | View | 菜单、输入、表格渲染 | 业务常量（60、100） |
| `main.py` | 组装 | 创建对象、启动、兜底异常 | 任何逻辑 |
| `tests/` | 测试 | 把逻辑变成机器可检查的断言 | —— |

## 三个值得抄进笔记的设计

1. **先落盘，再提交内存**（`service._commit`）：写盘失败时内存不会变脏。
2. **删除用重建列表**（`service.remove`）：`[s for s in ... if s.sid != sid]`，永不边遍历边删。
3. **序号单独持久化**（`next_seq`）：删掉 S002 后，新同学拿 S003，学号不复活。

## 已知的简化（留给你升级）

- 单用户假设：两个进程同时写会互相覆盖（阶段四可换 SQLite）
- 一条坏记录会让整个文件加载失败（可以改成「跳过并报告」）
- `all()` 返回列表副本，但 `Student` 本身是共享引用（要真隔离得 `deepcopy` 或改 frozen dataclass）
- 没有日志，只有 `print`（阶段二换 `logging`）

这些不是 bug，是**明确记录在案的边界**——能说清「我的系统在哪里会坏」，比假装它不会坏专业得多。
