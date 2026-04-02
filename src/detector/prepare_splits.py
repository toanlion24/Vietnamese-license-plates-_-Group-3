"""
Chia train/val/test theo plan buổi 2 từ ảnh đã có nhãn trong data/labels/raw/.

Tỷ lệ mặc định: 70% train, 20% val, 10% test (random seed cố định để lặp lại được).

Mỗi dòng trong file split là đường dẫn tương đối từ thư mục gốc repo tới ảnh,
ví dụ: data/images/raw/plate_0001.png

Chạy từ thư mục gốc repo:
  python -m src.detector.prepare_splits
  python -m src.detector.prepare_splits --data-root data --seed 42
"""

from __future__ import annotations

import argparse
import random
from pathlib import Path


def verify_split_files(repo_root: Path, labels_dir: Path, split_path: Path) -> tuple[int, int, int]:
    """Returns (lines, images_ok, labels_ok)."""
    if not split_path.is_file():
        return 0, 0, 0
    lines = 0
    img_ok = lbl_ok = 0
    for line in split_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        lines += 1
        ip = (repo_root / line).resolve()
        if ip.is_file():
            img_ok += 1
        lp = labels_dir / f"{ip.stem}.txt"
        if lp.is_file():
            lbl_ok += 1
    return lines, img_ok, lbl_ok


def stem_to_image_path(images_dir: Path, stem: str) -> Path | None:
    for ext in (".png", ".jpg", ".jpeg", ".bmp", ".webp"):
        p = images_dir / f"{stem}{ext}"
        if p.is_file():
            return p
    return None


def main() -> None:
    p = argparse.ArgumentParser(description="Tạo data/splits train|val|test.txt")
    p.add_argument(
        "--data-root",
        type=Path,
        default=Path("data"),
        help="Thư mục data (mặc định: data).",
    )
    p.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Gốc repo (mặc định: parent của data-root).",
    )
    p.add_argument("--train", type=float, default=0.7, help="Tỷ lệ train")
    p.add_argument("--val", type=float, default=0.2, help="Tỷ lệ val")
    p.add_argument("--test", type=float, default=0.1, help="Tỷ lệ test")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument(
        "--verify-only",
        action="store_true",
        help="Only check existing splits/*.txt vs images and labels (plan 5.2).",
    )
    args = p.parse_args()

    data_root = args.data_root.resolve()
    repo_root = (args.repo_root or data_root.parent).resolve()
    labels_dir = data_root / "labels" / "raw"
    images_dir = data_root / "images" / "raw"
    splits_dir = data_root / "splits"

    if not labels_dir.is_dir():
        raise SystemExit(f"Missing {labels_dir}")
    if not images_dir.is_dir():
        raise SystemExit(f"Missing {images_dir}")

    if args.verify_only:
        for name in ("train.txt", "val.txt", "test.txt"):
            sp = splits_dir / name
            ln, io, lo = verify_split_files(repo_root, labels_dir, sp)
            print(f"{name}: lines={ln} images_exist={io} labels_exist={lo}")
        return

    ratio_sum = args.train + args.val + args.test
    if abs(ratio_sum - 1.0) > 1e-6:
        raise SystemExit(f"Split ratios must sum to 1.0, got {ratio_sum}")

    stems: list[str] = []
    for txt in sorted(labels_dir.glob("*.txt")):
        img = stem_to_image_path(images_dir, txt.stem)
        if img is None:
            print(f"warn: skip {txt.name} (no matching image stem)")
            continue
        stems.append(txt.stem)

    if not stems:
        raise SystemExit("No valid label+image pairs.")

    rnd = random.Random(args.seed)
    rnd.shuffle(stems)
    n = len(stems)
    n_train = int(n * args.train)
    n_val = int(n * args.val)
    n_test = n - n_train - n_val

    train_stems = stems[:n_train]
    val_stems = stems[n_train : n_train + n_val]
    test_stems = stems[n_train + n_val :]

    splits_dir.mkdir(parents=True, exist_ok=True)

    def write_split(name: str, group: list[str]) -> None:
        lines: list[str] = []
        for stem in group:
            img = stem_to_image_path(images_dir, stem)
            assert img is not None
            rel = img.relative_to(repo_root).as_posix()
            lines.append(rel)
        out = splits_dir / f"{name}.txt"
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"{out}: {len(lines)} images")

    write_split("train", train_stems)
    write_split("val", val_stems)
    write_split("test", test_stems)
    print(f"total: {n} (train {len(train_stems)}, val {len(val_stems)}, test {len(test_stems)})")


if __name__ == "__main__":
    main()
