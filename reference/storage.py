"""持久化层（Repository）。

职责只有一句话：把“一个 dict 文档”安全地写进文件，或从文件读出来。
它不认识 Student，也不做业务校验 —— 那是 models / service 的事。

文件长这样（schema v1）：
{
  "schema_version": 1,
  "next_seq": 4,              <- 上层塞进来的元数据，这里只负责原样保存
  "students": [ {...}, ... ]
}

三个关键点：
1. ensure_ascii=False：中文按原样存，文件可读、可 git diff。
2. schema_version：给数据格式留版本号，以后改结构不慌。
3. 原子写入：先写同目录临时文件，再 os.replace。
   断电/崩溃时，磁盘上要么是完整的旧文件，要么是完整的新文件，不会有半个 JSON。
"""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

SCHEMA_VERSION = 1


class StorageError(RuntimeError):
    """磁盘/文件层面的故障：不可恢复，必须让用户知道，不能静默吞掉。"""


class JsonRepository:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def load(self) -> dict:
        """读回整个文档；文件不存在时返回一个合法的空文档（第一次运行不是错误）。"""
        if not self.path.exists():
            return {"schema_version": SCHEMA_VERSION, "students": []}

        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            backup = self._backup_broken_file()
            hint = f"，原文件已备份为 {backup.name}" if backup else ""
            raise StorageError(f"无法读取 {self.path.name}：{exc}{hint}") from exc

        if not isinstance(payload, dict):
            raise StorageError("数据文件格式不对：根节点应该是一个对象")

        version = int(payload.get("schema_version", 0))
        if version > SCHEMA_VERSION:
            raise StorageError(
                f"数据文件版本 {version} 高于程序支持的 {SCHEMA_VERSION}，请先升级程序"
            )
        if not isinstance(payload.get("students"), list):
            raise StorageError("数据文件格式不对：students 字段应该是一个列表")
        return payload

    def save(self, payload: dict) -> None:
        """原子写入：临时文件写成功后才替换正式文件。"""
        if not isinstance(payload.get("students"), list):
            raise ValueError("payload 必须包含 students 列表")

        payload = {"schema_version": SCHEMA_VERSION, **payload}
        self.path.parent.mkdir(parents=True, exist_ok=True)

        tmp = self.path.with_name(f".{self.path.name}.{os.getpid()}.tmp")
        try:
            with open(tmp, "w", encoding="utf-8", newline="\n") as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=2)
                handle.flush()
                os.fsync(handle.fileno())  # 让数据真正落盘，而不是停在系统缓存里
            os.replace(tmp, self.path)      # 原子替换：要么旧文件，要么新文件
        except Exception as exc:  # noqa: BLE001 - 任何写盘失败都要变成 StorageError
            tmp.unlink(missing_ok=True)
            raise StorageError(f"保存失败：{self.path}（{exc}）") from exc

    def _backup_broken_file(self) -> Path | None:
        """损坏的文件别删，改名留证 —— 让用户自己决定怎么修。"""
        backup = self.path.with_name(self.path.name + ".corrupt")
        try:
            shutil.copy2(self.path, backup)
        except OSError:
            return None
        return backup
