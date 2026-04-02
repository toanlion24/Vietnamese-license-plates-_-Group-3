"""
Áp dụng tiền xử lý / augment lên 1–2 ảnh mẫu, ghi ra data/debug_aug/ (plan buổi 2).

Chạy từ gốc repo:
  python -m src.preprocess.debug_augment_demo
  python -m src.preprocess.debug_augment_demo --images data/images/raw/plate_0001.png
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from .image_utils import (
    adjust_brightness_contrast,
    load_image_bgr,
    random_light_augment,
    random_small_rotation,
    resize_to_max_side,
    save_image_bgr,
)


def main() -> None:
    p = argparse.ArgumentParser(description="Write augmented samples to data/debug_aug/")
    p.add_argument(
        "--images",
        type=Path,
        nargs="*",
        default=None,
        help="Image paths (default: first two under data/images/raw/)",
    )
    p.add_argument(
        "--out-dir",
        type=Path,
        default=Path("data/debug_aug"),
        help="Output directory",
    )
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    repo = Path.cwd()
    raw = repo / "data" / "images" / "raw"
    if args.images:
        paths = [x.resolve() for x in args.images]
    else:
        if not raw.is_dir():
            raise SystemExit(f"Missing {raw}; pass --images explicitly")
        exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        paths = sorted([p for p in raw.iterdir() if p.suffix.lower() in exts])[:2]
        if not paths:
            raise SystemExit(f"No images in {raw}")

    rng = np.random.default_rng(args.seed)
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    for img_path in paths:
        stem = img_path.stem
        img = load_image_bgr(img_path)
        save_image_bgr(out_dir / f"{stem}_orig.png", img)

        sm = resize_to_max_side(img, max_side=640)
        save_image_bgr(out_dir / f"{stem}_resize_max640.png", sm)

        bc = adjust_brightness_contrast(img, alpha=1.15, beta=15)
        save_image_bgr(out_dir / f"{stem}_brighter.png", bc)

        lit = random_light_augment(img, rng=rng)
        save_image_bgr(out_dir / f"{stem}_rand_light.png", lit)

        rot = random_small_rotation(img, max_abs_deg=8.0, rng=rng)
        save_image_bgr(out_dir / f"{stem}_rot_small.png", rot)

    print(f"wrote samples under {out_dir}")


if __name__ == "__main__":
    main()
