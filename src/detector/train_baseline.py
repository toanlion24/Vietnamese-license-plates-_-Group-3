"""
Huấn luyện baseline YOLOv8 cho class `license_plate`.

- Pretrained (mặc định): tải backbone COCO, fine-tune head detection.
- From scratch: `YOLO("yolov8n.yaml")` — khởi tạo ngẫu nhiên theo kiến trúc.

Chạy từ gốc repo:
  python -m src.detector.train_baseline
  python -m src.detector.train_baseline --from-scratch --epochs 5
  python -m src.detector.train_baseline --val-initial --epochs 3
  python -m src.detector.train_baseline --epochs 50 --name baseline_50ep   # Buổi 3 đầy đủ (GPU)
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from ultralytics import YOLO


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read_results_csv(csv_path: Path) -> list[dict[str, str]]:
    if not csv_path.is_file():
        return []
    with csv_path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def pick_metrics_row(rows: list[dict[str, str]], epoch: int) -> dict[str, str] | None:
    for r in rows:
        try:
            if int(float(r.get("epoch", -1))) == epoch:
                return r
        except (TypeError, ValueError):
            continue
    return rows[-1] if rows else None


def main() -> None:
    root = repo_root()
    data_yaml = root / "data" / "data.yaml"
    default_project = root / "experiments"

    p = argparse.ArgumentParser(description="Train YOLOv8 baseline (pretrained or scratch)")
    p.add_argument("--data", type=Path, default=data_yaml, help="Path to data.yaml")
    p.add_argument(
        "--from-scratch",
        action="store_true",
        help="Train from architecture YAML (random weights), not COCO pretrained .pt",
    )
    p.add_argument(
        "--model-yaml",
        type=str,
        default="yolov8n.yaml",
        help="Architecture when --from-scratch (default: yolov8n.yaml)",
    )
    p.add_argument(
        "--weights",
        type=str,
        default="yolov8n.pt",
        help="Pretrained checkpoint when not --from-scratch (default: yolov8n.pt)",
    )
    p.add_argument(
        "--epochs",
        type=int,
        default=3,
        help="Số epoch (Buổi 3 theo kế hoạch: ~50; thử nhanh: 1–3)",
    )
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--batch", type=int, default=16)
    p.add_argument("--device", type=str, default="", help="Rỗng = auto; hoặc 'cpu', '0', ...")
    p.add_argument("--project", type=Path, default=default_project, help="Thư mục experiments")
    p.add_argument("--name", type=str, default="baseline_train", help="Tên run (subfolder)")
    p.add_argument(
        "--val-initial",
        action="store_true",
        help="Chạy val một lần trước khi train (ghi metrics khởi đầu)",
    )
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    data_path = args.data.resolve()
    if not data_path.is_file():
        raise SystemExit(f"Không thấy data yaml: {data_path}")

    project = args.project.resolve()
    project.mkdir(parents=True, exist_ok=True)

    if args.from_scratch:
        model = YOLO(args.model_yaml)
        init_source = args.model_yaml
    else:
        model = YOLO(args.weights)
        init_source = args.weights

    summary: dict = {
        "init_source": init_source,
        "from_scratch": args.from_scratch,
        "data": str(data_path.relative_to(root)) if data_path.is_relative_to(root) else str(data_path),
        "epochs_requested": args.epochs,
        "imgsz": args.imgsz,
        "batch": args.batch,
    }

    device_kw = {}
    if args.device:
        device_kw["device"] = args.device

    if args.val_initial:
        v = model.val(data=str(data_path), imgsz=args.imgsz, batch=args.batch, **device_kw)
        vd = getattr(v, "results_dict", None) or {}
        summary["metrics_before_train"] = {k: float(vd[k]) for k in sorted(vd) if isinstance(vd[k], (int, float))}

    train_kw = dict(
        data=str(data_path),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        project=str(project),
        name=args.name,
        exist_ok=True,
        seed=args.seed,
        **device_kw,
    )
    model.train(**train_kw)

    run_dir = project / args.name
    results_csv = run_dir / "results.csv"
    rows = read_results_csv(results_csv)
    if rows:
        first = pick_metrics_row(rows, 1) or rows[0]
        last = rows[-1]
        summary["epoch_1"] = first
        summary["epoch_last"] = last
        summary["results_csv"] = str(results_csv.relative_to(root)) if results_csv.is_relative_to(root) else str(results_csv)
    else:
        summary["results_csv"] = str(results_csv)
        summary["note"] = "Không đọc được results.csv (kiểm tra đường dẫn run)."

    best_pt = run_dir / "weights" / "best.pt"
    last_pt = run_dir / "weights" / "last.pt"
    summary["weights_best"] = str(best_pt) if best_pt.is_file() else None
    summary["weights_last"] = str(last_pt) if last_pt.is_file() else None

    out_json = run_dir / "baseline_summary.json"
    out_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {out_json}")


if __name__ == "__main__":
    main()
