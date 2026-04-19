"""
Đưa ảnh đã trích từ video (thư mục from_video) vào data/images/raw với quy ước plate_XXXX.

Luồng đề xuất:
  1) python -m src.preprocess.extract_video_frames --collection giao_thong_vn --every 30
  2) python -m src.preprocess.merge_from_video_to_raw --collection giao_thong_vn
  3) LabelImg: Open Dir = data/images/raw, Save = data/labels/raw
  4) python -m src.detector.prepare_splits

Chạy từ gốc repo:
  python -m src.preprocess.merge_from_video_to_raw --collection giao_thong_vn --dry-run
  python -m src.preprocess.merge_from_video_to_raw --from-dir data/images/from_video/giao_thong_vn
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from .video_sources import repo_root


IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def max_plate_index(raw_dir: Path) -> int:
    best = 0
    if not raw_dir.is_dir():
        return 0
    for p in raw_dir.iterdir():
        if not p.is_file() or p.suffix.lower() not in IMG_EXT:
            continue
        if not p.stem.startswith("plate_"):
            continue
        rest = p.stem[len("plate_") :]
        try:
            best = max(best, int(rest))
        except ValueError:
            continue
    return best


def collect_frame_images(from_root: Path) -> list[Path]:
    if not from_root.is_dir():
        return []
    out: list[Path] = []
    for p in sorted(from_root.rglob("*")):
        if p.is_file() and p.suffix.lower() in IMG_EXT:
            out.append(p)
    return out


def default_from_dir(collection: str, root: Path) -> Path:
    return root / "data" / "images" / "from_video" / collection


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    root = repo_root()
    raw_dir = root / "data" / "images" / "raw"

    p = argparse.ArgumentParser(
        description="Merge extracted video frames into data/images/raw as plate_XXXX"
    )
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument(
        "--collection",
        type=str,
        metavar="ID",
        help="Tên collection; đọc từ data/images/from_video/<ID>/ (sau extract_video_frames --collection)",
    )
    src.add_argument(
        "--from-dir",
        type=Path,
        help="Thư mục gốc chứa ảnh đã trích (quét đệ quy)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Chỉ in thống kê, không copy",
    )
    p.add_argument(
        "--move",
        action="store_true",
        help="Dùng move thay vì copy (tiết kiệm dung lượng; mất file ở thư mục nguồn)",
    )
    p.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Giới hạn số ảnh (0 = tất cả)",
    )
    args = p.parse_args()

    if args.collection:
        from_root = default_from_dir(args.collection, root).resolve()
    else:
        from_root = args.from_dir.resolve()

    if not from_root.is_dir():
        hint = (
            f"Không thấy thư mục nguồn: {from_root}\n"
            "Chạy trước: python -m src.preprocess.extract_video_frames "
            f"--collection {args.collection!r} --every 30"
            if args.collection
            else f"Không thấy thư mục nguồn: {from_root}"
        )
        raise SystemExit(hint)

    frames = collect_frame_images(from_root)
    if args.limit > 0:
        frames = frames[: args.limit]

    if not frames:
        raise SystemExit(f"Không có ảnh (.jpg/.png/...) trong: {from_root}")

    start = max_plate_index(raw_dir) + 1

    mapping: list[dict[str, str]] = []
    if not args.dry_run:
        raw_dir.mkdir(parents=True, exist_ok=True)

    for i, src_path in enumerate(frames):
        idx = start + i
        ext = src_path.suffix.lower()
        if ext not in IMG_EXT:
            ext = ".jpg"
        dest_name = f"plate_{idx:04d}{ext}"
        dest_path = raw_dir / dest_name
        mapping.append(
            {
                "source": str(src_path.relative_to(root)) if src_path.is_relative_to(root) else str(src_path),
                "dest": str(dest_path.relative_to(root)) if dest_path.is_relative_to(root) else str(dest_path),
            }
        )
        if args.dry_run:
            continue
        if args.move:
            shutil.move(str(src_path), dest_path)
        else:
            shutil.copy2(src_path, dest_path)

    meta_path = root / "data" / "migration_from_video_frames.json"
    payload = {
        "source_dir": str(from_root.relative_to(root)) if from_root.is_relative_to(root) else str(from_root),
        "collection": args.collection,
        "count": len(mapping),
        "start_plate": start,
        "end_plate": start + len(mapping) - 1 if mapping else None,
        "dry_run": args.dry_run,
        "move": args.move,
        "items": mapping,
    }

    print(f"Nguon:  {from_root}")
    print(f"Dich:   {raw_dir}")
    print(f"So anh: {len(frames)}  -> plate_{start:04d} .. plate_{start + len(frames) - 1:04d}")

    if args.dry_run:
        print("dry-run: khong ghi file.")
        for m in mapping[:5]:
            print(f"  {m['source']} -> {m['dest']}")
        if len(mapping) > 5:
            print(f"  ... (+{len(mapping) - 5})")
        return

    meta_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Ghi metadata: {meta_path.relative_to(root)}")
    print(
        "Tiep theo: gan nhan bang LabelImg (Save vao data/labels/raw), "
        "roi: python -m src.detector.prepare_splits"
    )


if __name__ == "__main__":
    main()
