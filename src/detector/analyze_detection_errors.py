"""
Phân tích lỗi detection sơ bộ trên split (mặc định val): TP / FP / FN theo IoU.

Không thay thế báo cáo val đầy đủ của Ultralytics; dùng để đếm nhanh và liệt kê
ảnh có nhiều lỗi (miss hoặc dư box).

Chạy từ gốc repo:
  python -m src.detector.analyze_detection_errors --weights experiments/baseline_train/weights/best.pt
  python -m src.detector.analyze_detection_errors --weights yolov8n.pt --max-images 50
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def yolo_norm_to_xyxy(line: str, w: int, h: int) -> np.ndarray | None:
    parts = line.strip().split()
    if len(parts) < 5:
        return None
    try:
        _c, cx, cy, bw, bh = map(float, parts[:5])
    except ValueError:
        return None
    cx *= w
    cy *= h
    bw *= w
    bh *= h
    x1 = cx - bw / 2
    y1 = cy - bh / 2
    x2 = cx + bw / 2
    y2 = cy + bh / 2
    return np.array([x1, y1, x2, y2], dtype=np.float32)


def iou_xyxy(a: np.ndarray, b: np.ndarray) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1 = max(ax1, bx1)
    iy1 = max(ay1, by1)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)
    iw = max(0.0, ix2 - ix1)
    ih = max(0.0, iy2 - iy1)
    inter = iw * ih
    if inter <= 0:
        return 0.0
    aa = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    ba = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    union = aa + ba - inter
    return float(inter / union) if union > 0 else 0.0


def match_boxes(
    gt: list[np.ndarray],
    pr: list[np.ndarray],
    iou_thr: float,
) -> tuple[int, int, int]:
    """Greedy matching: returns (tp, fp, fn)."""
    if not gt:
        return 0, len(pr), 0
    if not pr:
        return 0, 0, len(gt)
    ious = np.zeros((len(gt), len(pr)), dtype=np.float64)
    for i, g in enumerate(gt):
        for j, p in enumerate(pr):
            ious[i, j] = iou_xyxy(g, p)
    tp = 0
    used_g = set()
    used_p = set()
    flat = [(ious[i, j], i, j) for i in range(len(gt)) for j in range(len(pr))]
    flat.sort(reverse=True)
    for score, i, j in flat:
        if score < iou_thr:
            break
        if i in used_g or j in used_p:
            continue
        used_g.add(i)
        used_p.add(j)
        tp += 1
    fp = len(pr) - len(used_p)
    fn = len(gt) - len(used_g)
    return tp, fp, fn


def main() -> None:
    root = repo_root()
    p = argparse.ArgumentParser(description="Sơ bộ TP/FP/FN detection trên split")
    p.add_argument("--weights", type=str, required=True, help="best.pt hoặc pretrained .pt")
    p.add_argument("--data", type=Path, default=root / "data" / "data.yaml")
    p.add_argument(
        "--split-file",
        type=Path,
        default=root / "data" / "splits" / "val.txt",
        help="File danh sách ảnh (đường dẫn tương đối repo)",
    )
    p.add_argument("--max-images", type=int, default=200, help="Giới hạn số ảnh (0 = tất cả)")
    p.add_argument("--conf", type=float, default=0.25)
    p.add_argument("--iou-match", type=float, default=0.5, help="IoU để gán TP")
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--device", type=str, default="")
    p.add_argument(
        "--pred-class",
        type=int,
        default=None,
        help="Chỉ giữ bbox có class id này. Mặc định: 0 nếu model 1 class; None = mọi class (COCO).",
    )
    p.add_argument(
        "--out-json",
        type=Path,
        default=root / "experiments" / "error_analysis_summary.json",
    )
    args = p.parse_args()

    data_yaml = args.data.resolve()
    split_path = args.split_file.resolve()
    if not data_yaml.is_file():
        raise SystemExit(f"Không thấy {data_yaml}")
    if not split_path.is_file():
        raise SystemExit(f"Không thấy {split_path}")

    model = YOLO(args.weights)
    device_kw = {"device": args.device} if args.device else {}

    names = model.names
    n_cls = len(names) if isinstance(names, dict) else int(getattr(model.model, "nc", 0) or 0)
    pred_class = args.pred_class
    if pred_class is None and n_cls == 1:
        pred_class = 0

    lines = [ln.strip() for ln in split_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if args.max_images and args.max_images > 0:
        lines = lines[: args.max_images]

    total_tp = total_fp = total_fn = 0
    worst: list[tuple[int, str]] = []

    for rel in lines:
        img_path = (root / rel).resolve()
        if not img_path.is_file():
            continue
        stem = img_path.stem
        lbl_path = root / "data" / "labels" / "raw" / f"{stem}.txt"
        im = cv2.imread(str(img_path))
        if im is None:
            continue
        h, w = im.shape[:2]
        gt_boxes: list[np.ndarray] = []
        if lbl_path.is_file():
            for line in lbl_path.read_text(encoding="utf-8").splitlines():
                b = yolo_norm_to_xyxy(line, w, h)
                if b is not None:
                    gt_boxes.append(b)

        res = model.predict(
            source=str(img_path),
            imgsz=args.imgsz,
            conf=args.conf,
            verbose=False,
            **device_kw,
        )[0]
        pr_boxes: list[np.ndarray] = []
        if res.boxes is not None and len(res.boxes):
            xyxy = res.boxes.xyxy.cpu().numpy()
            cls_ids = res.boxes.cls.cpu().numpy().astype(int)
            for row, ci in zip(xyxy, cls_ids):
                if pred_class is not None and int(ci) != pred_class:
                    continue
                pr_boxes.append(row.astype(np.float32))

        tp, fp, fn = match_boxes(gt_boxes, pr_boxes, args.iou_match)
        total_tp += tp
        total_fp += fp
        total_fn += fn
        err = fp + fn
        if err > 0:
            worst.append((err, rel))

    worst.sort(reverse=True)
    top_failures = [rel for _e, rel in worst[:30]]

    denom = total_tp + total_fp
    precision = total_tp / denom if denom else 0.0
    denom_r = total_tp + total_fn
    recall = total_tp / denom_r if denom_r else 0.0

    report = {
        "weights": args.weights,
        "split_file": str(split_path.relative_to(root)) if split_path.is_relative_to(root) else str(split_path),
        "images_scanned": len(lines),
        "model_num_classes": n_cls,
        "pred_class_filter": pred_class,
        "conf": args.conf,
        "iou_match": args.iou_match,
        "tp": total_tp,
        "fp": total_fp,
        "fn": total_fn,
        "micro_precision": round(precision, 4),
        "micro_recall": round(recall, 4),
        "top_failure_paths": top_failures,
        "notes": [
            "FP: box dự đoán không khớp GT (IoU < ngưỡng hoặc dư box).",
            "FN: GT không có pred khớp IoU >= ngưỡng.",
            "Với nhiều biển/ảnh, greedy matching có thể khác COCO mAP chính thức.",
        ],
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
