"""
Convert YOLO segmentation label files (class + normalized polygon x y ...) to YOLO detection (class xc yc w h).

Default layout (dataset root):
  images/{train,val}/...
  labels/{train,val}/*.txt   -> polygon lines
Writes:
  labels_bbox/{train,val}/*.txt
Optional --swap-for-yolo-detect: backup labels -> labels_segmentation_backup, rename labels_bbox -> labels.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def polygon_line_to_bbox(parts: list[str]) -> str | None:
    """One line: class x1 y1 x2 y2 ... -> class xc yc w h (normalized, clipped)."""
    if len(parts) < 3:
        return None
    try:
        cls_id = int(float(parts[0]))
        coords = [float(x) for x in parts[1:]]
    except ValueError:
        return None
    if len(coords) < 4 or len(coords) % 2 != 0:
        return None
    xs = coords[0::2]
    ys = coords[1::2]
    xmin, xmax = max(0.0, min(xs)), min(1.0, max(xs))
    ymin, ymax = max(0.0, min(ys)), min(1.0, max(ys))
    w = xmax - xmin
    h = ymax - ymin
    if w <= 0 or h <= 0:
        return None
    xc = (xmin + xmax) / 2.0
    yc = (ymin + ymax) / 2.0
    return f"{cls_id} {xc:.10f} {yc:.10f} {w:.10f} {h:.10f}"


def convert_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    out_lines: list[str] = []
    text = src.read_text(encoding="utf-8", errors="replace").strip()
    if not text:
        dst.write_text("", encoding="utf-8")
        return
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        bbox = polygon_line_to_bbox(parts)
        if bbox is not None:
            out_lines.append(bbox)
    dst.write_text("\n".join(out_lines) + ("\n" if out_lines else ""), encoding="utf-8")


def convert_tree(dataset_root: Path, splits: list[str]) -> None:
    for split in splits:
        src_dir = dataset_root / "labels" / split
        dst_dir = dataset_root / "labels_bbox" / split
        if not src_dir.is_dir():
            continue
        for src in sorted(src_dir.glob("*.txt")):
            convert_file(src, dst_dir / src.name)


def swap_for_detect(dataset_root: Path) -> None:
    labels = dataset_root / "labels"
    labels_bbox = dataset_root / "labels_bbox"
    backup = dataset_root / "labels_segmentation_backup"
    if not labels_bbox.is_dir():
        raise SystemExit(
            f"Missing {labels_bbox}. Run this script without --swap-for-yolo-detect first."
        )
    if not any(labels_bbox.rglob("*.txt")):
        raise SystemExit(f"No .txt files under {labels_bbox}.")
    if backup.exists():
        raise SystemExit(f"{backup} already exists; remove or rename it before swapping.")
    if labels.exists():
        labels.rename(backup)
    labels_bbox.rename(labels)


def restore_segmentation(dataset_root: Path) -> None:
    """Restore polygon labels: labels_segmentation_backup -> labels, and recreate empty labels_bbox if needed."""
    labels = dataset_root / "labels"
    backup = dataset_root / "labels_segmentation_backup"
    if not backup.is_dir():
        raise SystemExit(f"No backup at {backup}.")
    if labels.exists():
        raise SystemExit(f"{labels} exists; remove bbox labels folder first or rename manually.")
    backup.rename(labels)


def main() -> None:
    p = argparse.ArgumentParser(description="Polygon YOLO labels -> bbox YOLO labels.")
    p.add_argument(
        "--dataset-root",
        type=Path,
        default=Path("datakangle"),
        help="Folder containing images/ and labels/ (default: datakangle).",
    )
    p.add_argument(
        "--swap-for-yolo-detect",
        action="store_true",
        help="After convert: rename labels -> labels_segmentation_backup, labels_bbox -> labels.",
    )
    p.add_argument(
        "--restore-segmentation",
        action="store_true",
        help="Rename labels_segmentation_backup back to labels (undo swap).",
    )
    args = p.parse_args()
    root = args.dataset_root.resolve()
    if args.restore_segmentation:
        restore_segmentation(root)
        print(f"Restored polygon labels under {root / 'labels'}")
        return
    if not root.is_dir():
        raise SystemExit(f"Dataset root not found: {root}")
    convert_tree(root, ["train", "val"])
    print(f"Wrote bbox labels under {root / 'labels_bbox'}")
    if args.swap_for_yolo_detect:
        swap_for_detect(root)
        print(
            f"Swapped: polygon backup at {root / 'labels_segmentation_backup'}, "
            f"active labels are bbox for detection."
        )


if __name__ == "__main__":
    main()
