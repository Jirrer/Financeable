from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable


def _ensure_user_file(user_path: str) -> Path:
    path = Path(user_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(json.dumps({"favorites": []}, indent=2), encoding="utf-8")
    return path


def _read_user_data(user_path: str) -> dict:
    path = _ensure_user_file(user_path)
    try:
        return json.loads(path.read_text(encoding="utf-8") or "{}")
    except json.JSONDecodeError:
        return {"favorites": []}


def get_favorites(user_path: str) -> list[int]:
    data = _read_user_data(user_path)
    favorites = data.get("favorites", [])
    if not isinstance(favorites, list):
        return []
    return [int(x) for x in favorites if isinstance(x, (int, float, str))]


def set_favorites(favorites: Iterable[int], user_path: str) -> bool:
    path = _ensure_user_file(user_path)
    data = _read_user_data(user_path)
    data["favorites"] = [int(x) for x in favorites]
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return True
