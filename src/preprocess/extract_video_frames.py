"""
Trích frame từ video (OpenCV), lưu ra thư mục ảnh — plan buổi 2 mục 3.

Mặc định ghi vào data/images/raw/ (cùng layout buổi 2; plan gọi là data/raw).

Chạy từ gốc repo:
  python -m src.preprocess.extract_video_frames --video path/to/video.mp4 --every 10
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2


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
    p = argparse.ArgumentParser(description="Extract every N-th frame from video to images folder.")
    p.add_argument("--video", type=Path, required=True, help="Path to input video")
    p.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/images/raw"),
        help="Output directory (default: data/images/raw)",
    )
    p.add_argument("--every", type=int, default=10, help="Save one frame every N frames")
    p.add_argument("--prefix", type=str, default="frame_", help="Filename prefix")
    p.add_argument(
        "--auto-index",
        action="store_true",
        help="Continue numbering after existing prefix_* in output dir",
    )
    args = p.parse_args()

    video = args.video.resolve()
    out = args.output_dir.resolve()
    start = next_frame_start_index(out, args.prefix) if args.auto_index else 1

    n = extract_frames(video, out, every_n=args.every, prefix=args.prefix, start_index=start)
    print(f"saved {n} frames to {out}")


if __name__ == "__main__":
    main()
