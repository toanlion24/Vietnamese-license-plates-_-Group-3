"""
Đăng ký các *bộ video* trong repo (đường dẫn tương đối gốc repo).

Cấu hình: `data/video_sources.json`
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

VIDEO_EXTENSIONS = frozenset({".mp4", ".avi", ".mov", ".mkv", ".webm", ".m4v"})


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_config_path(root: Path | None = None) -> Path:
    r = root or repo_root()
    return r / "data" / "video_sources.json"


def load_config(path: Path | None = None) -> dict[str, Any]:
    p = path or default_config_path()
    if not p.is_file():
        raise FileNotFoundError(f"Không thấy cấu hình video: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def collection_ids(config: dict[str, Any] | None = None) -> list[str]:
    cfg = config or load_config()
    cols = cfg.get("collections") or {}
    return sorted(cols.keys())


def get_collection_path(collection_id: str, root: Path | None = None) -> Path:
    root = root or repo_root()
    cfg = load_config(default_config_path(root))
    cols = cfg.get("collections") or {}
    if collection_id not in cols:
        known = ", ".join(sorted(cols)) or "(trống)"
        raise KeyError(f"Không có bộ video '{collection_id}'. Đã có: {known}")
    rel = (cols[collection_id] or {}).get("path")
    if not rel or not isinstance(rel, str):
        raise ValueError(f"Thiếu 'path' cho bộ '{collection_id}'")
    return (root / rel).resolve()


def iter_videos(directory: Path, *, recursive: bool = False) -> list[Path]:
    if not directory.is_dir():
        return []
    it = directory.rglob("*") if recursive else directory.iterdir()
    out: list[Path] = []
    for p in it:
        if p.is_file() and p.suffix.lower() in VIDEO_EXTENSIONS:
            out.append(p)
    return sorted(out)


def list_collection_videos(collection_id: str, root: Path | None = None) -> list[Path]:
    root = root or repo_root()
    root_dir = get_collection_path(collection_id, root=root)
    cfg = load_config(default_config_path(root))
    col = (cfg.get("collections") or {}).get(collection_id) or {}
    recursive = bool(col.get("recursive"))
    return iter_videos(root_dir, recursive=recursive)


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    r = repo_root()
    cfg = load_config(default_config_path(r))
    for cid in collection_ids(cfg):
        meta = (cfg.get("collections") or {}).get(cid) or {}
        p = get_collection_path(cid, root=r)
        n = len(list_collection_videos(cid, root=r))
        label = meta.get("label") or cid
        print(f"{cid}: {label}")
        print(f"  path: {p}")
        print(f"  videos: {n}")


if __name__ == "__main__":
    main()
