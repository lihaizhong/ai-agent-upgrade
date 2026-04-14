from __future__ import annotations

import json
from typing import Any


def json_dumps(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)


def json_print(payload: Any) -> None:
    print(json_dumps(payload))

