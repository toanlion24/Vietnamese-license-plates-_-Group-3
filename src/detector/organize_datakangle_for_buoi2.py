"""
Tổ chức dataset từ datakangle (images/{train,val}, labels_bbox|labels) sang cấu trúc buổi 2.

Cấu trúc đích (tương thích Ultralytics YOLO — đường dẫn ảnh phải chứa segment "images"):
  data/images/raw/plate_0001.png
  data/labels/raw/plate_0001.txt
  data/splits/{train,val,test}.txt

Quy ước tên: plate_XXXX + cùng phần mở rộng ảnh gốc (.png/.jpg).
Nhãn: BSD/BSV (class 0,1) gom về 0 = license_plate (một lớp cho detection buổi sau).

Chạy từ thư mục gốc repo:
  python -m src.detector.organize_datakangle_for_buoi2
  python -m src.detector.organize_datakangle_for_buoi2 --dry-run
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


def remap_label_line_to_single_class(line: str, target_cls: int = 0) -> str | None:
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    parts = line.split()
    if len(parts) < 5:
        return None
    try:
        float(parts[1])
        float(parts[2])
        float(parts[3])
        float(parts[4])
    except ValueError:
        return None
    return f"{target_cls} {' '.join(parts[1:5])}"


def remap_label_file(text: str, target_cls: int = 0) -> str:
    out: list[str] = []
    for line in text.splitlines():
        m = remap_label_line_to_single_class(line, target_cls)
        if m:
            out.append(m)
    return "\n".join(out) + ("\n" if out else "")


def find_label_path(
    dataset_root: Path, split: str, stem: str, prefer_bbox: bool
) -> Path | None:
    if prefer_bbox:
        p = dataset_root / "labels_bbox" / split / f"{stem}.txt"
        if p.is_file():
            return p
    p = dataset_root / "labels" / split / f"{stem}.txt"
    if p.is_file():
        return p
    if not prefer_bbox:
        p = dataset_root / "labels_bbox" / split / f"{stem}.txt"
        if p.is_file():
            return p
    return None


def collect_pairs(
    dataset_root: Path, splits: list[str], prefer_bbox: bool
) -> list[tuple[str, Path, Path]]:
    """(split_name, image_path, label_path) — chỉ cặp có đủ ảnh và nhãn."""
    pairs: list[tuple[str, Path, Path]] = []
    exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    for split in splits:
        img_dir = dataset_root / "images" / split
        if not img_dir.is_dir():
            continue
        for img in sorted(img_dir.iterdir()):
            if not img.is_file() or img.suffix.lower() not in exts:
                continue
            lp = find_label_path(dataset_root, split, img.stem, prefer_bbox)
            if lp is None:
                continue
            pairs.append((split, img, lp))
    return pairs


def main() -> None:
    p = argparse.ArgumentParser(description="Migrate datakangle → data/ (buổi 2 layout).")
    p.add_argument(
        "--source",
        type=Path,
        default=Path("datakangle"),
        help="Thư mục gốc dataset nguồn (mặc định: datakangle).",
    )
    p.add_argument(
        "--dest",
        type=Path,
        default=Path("data"),
        help="Thư mục đích (mặc định: data).",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Chỉ in thống kê, không copy file.",
    )
    p.add_argument(
        "--prefer-polygon-labels",
        action="store_true",
        help="Ưu tiên labels/ (polygon); mặc định ưu tiên labels_bbox/ (bbox).",
    )
    args = p.parse_args()

    root = args.source.resolve()
    dest = args.dest.resolve()
    prefer_bbox = not args.prefer_polygon_labels

    if not root.is_dir():
        raise SystemExit(f"Source not found: {root}")

    splits_order = ["train", "val"]
    pairs = collect_pairs(root, splits_order, prefer_bbox)
    if not pairs:
        raise SystemExit(
            "No image+label pairs. Check images/{train,val} and labels_bbox or labels."
        )

    img_out = dest / "images" / "raw"
    lbl_out = dest / "labels" / "raw"
    if not args.dry_run:
        img_out.mkdir(parents=True, exist_ok=True)
        lbl_out.mkdir(parents=True, exist_ok=True)
        (dest / "splits").mkdir(parents=True, exist_ok=True)

    mapping: list[dict[str, str]] = []
    for i, (split, img_path, lbl_path) in enumerate(pairs, start=1):
        new_base = f"plate_{i:04d}"
        new_img = img_out / f"{new_base}{img_path.suffix.lower()}"
        new_lbl = lbl_out / f"{new_base}.txt"
        rel_img = new_img.relative_to(dest.parent).as_posix()
        text = lbl_path.read_text(encoding="utf-8", errors="replace")
        new_text = remap_label_file(text, target_cls=0)
        mapping.append(
            {
                "split": split,
                "source_image": str(img_path.as_posix()),
                "source_label": str(lbl_path.as_posix()),
                "dest_image": rel_img,
                "dest_label": new_lbl.relative_to(dest.parent).as_posix(),
            }
        )
        if args.dry_run:
            continue
        shutil.copy2(img_path, new_img)
        new_lbl.write_text(new_text, encoding="utf-8")

    meta_path = dest / "migration_from_datakangle.json"
    if not args.dry_run:
        meta_path.write_text(
            json.dumps(
                {
                    "source": str(root),
                    "count": len(mapping),
                    "prefer_bbox_labels": prefer_bbox,
                    "class_map": {"0": "license_plate (was BSD)", "1": "license_plate (was BSV)"},
                    "items": mapping,
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    print(f"source: {root}")
    print(f"dest:   {dest}")
    print(f"pairs (image+label): {len(mapping)}")
    print(
        f"labels: {'labels_bbox' if prefer_bbox else 'labels (polygon; run convert_polygon_to_yolo_bbox if bbox needed)'}"
    )
    if args.dry_run:
        print("dry-run: no files written.")
    else:
        rel = meta_path.relative_to(dest.parent) if dest.parent in meta_path.parents else meta_path
        print(f"wrote: {rel}")


if __name__ == "__main__":
    main()
