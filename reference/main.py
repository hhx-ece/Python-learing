"""组装入口（Composition Root）。

依赖方向：main -> cli -> service -> storage / models
没有反向依赖，也没有一个模块 import main。
换 GUI 时只改这一行：把 cli.run 换成 gui.run。
"""

from __future__ import annotations

import sys
from pathlib import Path

from cli import run
from service import StudentService
from storage import JsonRepository, StorageError

DATA_FILE = Path(__file__).resolve().parent / "data" / "students.json"


def main() -> int:
    try:
        service = StudentService(JsonRepository(DATA_FILE))
        run(service)
    except StorageError as exc:
        print(f"[致命错误] {exc}", file=sys.stderr)
        print("请检查 data/students.json，或把它移走后重新运行。", file=sys.stderr)
        return 1
    except (KeyboardInterrupt, EOFError):
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
