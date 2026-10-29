# 电子信息工程 · Python 学习项目

一个大一学生的 Python 实战练习：从控制台版学生成绩管理系统，一路做到带图形界面的数据采集上位机。

## 现在做到哪了

| 关卡 | 内容 | 状态 |
|---|---|---|
| M01 | 输入契约（校验、范围、表格） | ✅ 5/5 |
| M02 | 查询 | ✅ 4/4 |
| M03 | 修改 | ⬜ 待做 |
| M04 | 删除重构 | ✅ 5/5 |
| M05 | 统计 | ⬜ 待做 |
| M06 | 持久化 | ⬜ 待做 |

## 目录说明

| 路径 | 作用 |
|---|---|
| `student_score_system.py` | 主程序，唯一在改的文件 |
| `missions/` | 六关任务书、验收测试、评审记录 |
| `reference/` | 完整参考实现（阶段一结束时的形态） |
| `archive/` | 历史版本存档 |
| `Python学习路线图.md` | 四阶段学习规划 |
| `代码诊断-v1.2.md` | 起点代码的逐行诊断与重构阶梯 |

## 怎么运行

```powershell
python student_score_system.py
```

## 怎么跑验收测试

```powershell
cd missions
python -m unittest discover -s tests -v
```

单关：

```powershell
python -m unittest discover -s tests -p "test_m01*.py" -v
```

## 说明

- 主程序用标准库实现，不依赖第三方包；`reference/` 里的版本也只用了标准库。
- 测试是黑盒的：喂输入、收输出，只看用户可见的行为，不关心内部结构。
