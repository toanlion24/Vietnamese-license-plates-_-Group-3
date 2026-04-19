"""
Trích frame từ video (OpenCV), lưu ra thư mục ảnh — plan buổi 2 mục 3.

Mặc định ghi vào data/images/raw/ (cùng layout buổi 2; plan gọi là data/raw).

Chạy từ gốc repo:
  python -m src.preprocess.extract_video_frames --video path/to/video.mp4 --every 10
  python -m src.preprocess.extract_video_frames --collection giao_thong_vn --every 30
  python -m src.preprocess.extract_video_frames --video-dir "vid/Giao thông Việt Nam" --every 30
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2

from .video_sources import (
    get_collection_path,
    iter_videos,
    list_collection_videos,
    repo_root,
)


def extract_frames(
    video_path: Path,
    output_dir: Path,
    every_n: int = 10,
    prefix: str = "frame_",
    start_index: int = 1,
    ext: str = ".jpg",
) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise SystemExit(f"Cannot open video: {video_path}")

    saved = 0
    idx = 0
    next_num = start_index
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if idx % every_n == 0:
            name = f"{prefix}{next_num:06d}{ext}"
            out = output_dir / name
            cv2.imencode(ext, frame)[1].tofile(str(out))
            saved += 1
            next_num += 1
        idx += 1
    cap.release()
    return saved


def extract_frames_batch(
    video_paths: list[Path],
    output_base: Path,
    every_n: int,
    prefix: str = "frame_",
    ext: str = ".jpg",
) -> int:
    """Mỗi video một thư mục con: output_base/<stem>/frame_*.jpg"""
    total = 0
    for vp in video_paths:
        sub = output_base / vp.stem
        n = extract_frames(vp, sub, every_n=every_n, prefix=prefix, start_index=1, ext=ext)
        total += n
        print(f"  {vp.name}: {n} frame -> {sub}")
    return total


def next_frame_start_index(output_dir: Path, prefix: str) -> int:
    best = 0
    if not output_dir.is_dir():
        return 1
    plen = len(prefix)
    for p in output_dir.iterdir():
        if not p.is_file() or not p.name.startswith(prefix):
            continue
        stem = p.stem
        if len(stem) <= plen:
            continue
        try:
            n = int(stem[plen:])
            best = max(best, n)
        except ValueError:
            continue
    return best + 1


def main() -> None:
    root = repo_root()
    p = argparse.ArgumentParser(description="Extract every N-th frame from video to images folder.")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--video", type=Path, help="Một file video")
    src.add_argument(
        "--collection",
        type=str,
        metavar="ID",
        help="ID trong data/video_sources.json (vd. giao_thong_vn)",
    )
    src.add_argument(
        "--video-dir",
        type=Path,
        help="Thư mục chứa nhiều video (không đệ quy)",
    )
    p.add_argument(
        "--recursive",
        action="store_true",
        help="Với --video-dir: quét cả file trong thư mục con",
    )
    p.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Thư mục đầu ra. Mặc định: data/images/raw (một video) hoặc data/images/from_video/<collection> (batch)",
    )
    p.add_argument("--every", type=int, default=10, help="Save one frame every N frames")
    p.add_argument("--prefix", type=str, default="frame_", help="Filename prefix")
    p.add_argument(
        "--auto-index",
        action="store_true",
        help="(Chỉ --video) Tiếp số frame sau prefix_* đã có trong output",
    )
    args = p.parse_args()

    if args.video:
        out = (args.output_dir or Path("data/images/raw")).resolve()
        video = args.video.resolve()
        start = next_frame_start_index(out, args.prefix) if args.auto_index else 1
        n = extract_frames(video, out, every_n=args.every, prefix=args.prefix, start_index=start)
        print(f"saved {n} frames to {out}")
        return

    if args.collection:
        out = (args.output_dir or (root / "data" / "images" / "from_video" / args.collection)).resolve()
        vdir = get_collection_path(args.collection, root=root)
        videos = list_collection_videos(args.collection, root=root)
        if not videos:
            raise SystemExit(f"Không thấy file video trong: {vdir}")
        print(f"Collection {args.collection}: {len(videos)} video(s) -> {out}")
        total = extract_frames_batch(videos, out, every_n=args.every, prefix=args.prefix)
        print(f"saved {total} frames total under {out}")
        return

    assert args.video_dir is not None
    vdir = args.video_dir.resolve()
    out = (args.output_dir or (root / "data" / "images" / "from_video" / vdir.name)).resolve()
    videos = iter_videos(vdir, recursive=args.recursive)
    if not videos:
        raise SystemExit(f"Không thấy file video trong: {vdir}")
    print(f"{len(videos)} video(s) -> {out}")
    total = extract_frames_batch(videos, out, every_n=args.every, prefix=args.prefix)
    print(f"saved {total} frames total under {out}")


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    main()
