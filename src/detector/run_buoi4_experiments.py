"""
Buoi 4 - Chay nhieu cau hinh YOLO de so sanh.

Muc tieu:
- Thu >= 2 cau hinh (model/imgsz/augment) trong mot lan chay.
- Luu ket qua moi run va file tong hop de notebook Buoi 4 doc.

Chay tu goc repo:
  python -m src.detector.run_buoi4_experiments --preset fast2 --epochs 10 --device cpu
  python -m src.detector.run_buoi4_experiments --preset full3 --epochs 30 --device 0
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from ultralytics import YOLO


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read_results_csv(csv_path: Path) -> list[dict[str, str]]:
    if not csv_path.is_file():
        return []
    with csv_path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def to_float_or_none(v: Any) -> float | None:
    try:
        return float(v)
    except Exception:
        return None


def build_configs(preset: str) -> list[dict[str, Any]]:
    # augment: de None = dung mac dinh cua YOLO
    fast2 = [
        {
            "tag": "y8n_640_default",
            "weights": "yolov8n.pt",
            "imgsz": 640,
            "augment": None,
        },
        {
            "tag": "y8s_640_default",
            "weights": "yolov8s.pt",
            "imgsz": 640,
            "augment": None,
        },
    ]
    full3 = [
        {
            "tag": "y8n_640_default",
            "weights": "yolov8n.pt",
            "imgsz": 640,
            "augment": None,
        },
        {
            "tag": "y8s_640_default",
            "weights": "yolov8s.pt",
            "imgsz": 640,
            "augment": None,
        },
        {
            "tag": "y8n_416_lightaug",
            "weights": "yolov8n.pt",
            "imgsz": 416,
            "augment": {
                "hsv_h": 0.010,
                "hsv_s": 0.50,
                "hsv_v": 0.30,
                "degrees": 5.0,
                "mosaic": 0.5,
            },
        },
    ]
    quick2 = [
        {
            "tag": "y8n_416_default",
            "weights": "yolov8n.pt",
            "imgsz": 416,
            "augment": None,
        },
        {
            "tag": "y8n_320_lightaug",
            "weights": "yolov8n.pt",
            "imgsz": 320,
            "augment": {
                "hsv_h": 0.010,
                "hsv_s": 0.50,
                "hsv_v": 0.30,
                "degrees": 5.0,
                "mosaic": 0.5,
            },
        },
    ]
    if preset == "fast2":
        return fast2
    if preset == "full3":
        return full3
    if preset == "quick2":
        return quick2
    raise ValueError(f"Unsupported preset: {preset}")


def pick_metrics(last_row: dict[str, str]) -> dict[str, float | None]:
    keys = {
        "precision": "metrics/precision(B)",
        "recall": "metrics/recall(B)",
        "map50": "metrics/mAP50(B)",
        "map50_95": "metrics/mAP50-95(B)",
        "train_box_loss": "train/box_loss",
        "train_cls_loss": "train/cls_loss",
        "train_dfl_loss": "train/dfl_loss",
        "val_box_loss": "val/box_loss",
        "val_cls_loss": "val/cls_loss",
        "val_dfl_loss": "val/dfl_loss",
    }
    out: dict[str, float | None] = {}
    for k, src in keys.items():
        out[k] = to_float_or_none(last_row.get(src))
    return out


def main() -> None:
    root = repo_root()
    default_data = root / "data" / "data.yaml"
    default_project = root / "experiments"

    p = argparse.ArgumentParser(description="Buoi 4 YOLO experiments runner")
    p.add_argument("--data", type=Path, default=default_data)
    p.add_argument("--project", type=Path, default=default_project)
    p.add_argument("--group-name", type=str, default="buoi4_experiments")
    p.add_argument("--preset", type=str, choices=("quick2", "fast2", "full3"), default="fast2")
    p.add_argument("--epochs", type=int, default=10, help="Nen dong nhat giua cac run")
    p.add_argument("--batch", type=int, default=16)
    p.add_argument("--fraction", type=float, default=1.0, help="Ti le du lieu train (0..1), giam de chay nhanh")
    p.add_argument("--workers", type=int, default=0, help="So worker dataloader")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--device", type=str, default="", help="Rong=auto, hoac 'cpu', '0', ...")
    p.add_argument("--dry-run", action="store_true", help="Chi in cau hinh, khong train")
    args = p.parse_args()

    data_path = args.data.resolve()
    if not data_path.is_file():
        raise SystemExit(f"Khong thay data yaml: {data_path}")

    project = args.project.resolve()
    group_dir = project / args.group_name
    group_dir.mkdir(parents=True, exist_ok=True)

    configs = build_configs(args.preset)
    device_kw = {"device": args.device} if args.device else {}

    summary: dict[str, Any] = {
        "group_name": args.group_name,
        "preset": args.preset,
        "data": str(data_path.relative_to(root)) if data_path.is_relative_to(root) else str(data_path),
        "epochs": args.epochs,
        "batch": args.batch,
        "device": args.device or "auto",
        "runs": [],
    }

    for cfg in configs:
        run_name = f"{args.group_name}_{cfg['tag']}"
        run_dir = project / run_name
        print(f"\n=== RUN: {run_name} ===")
        print(json.dumps(cfg, ensure_ascii=False, indent=2))

        if args.dry_run:
            summary["runs"].append(
                {
                    "tag": cfg["tag"],
                    "run_name": run_name,
                    "dry_run": True,
                    "weights": cfg["weights"],
                    "imgsz": cfg["imgsz"],
                    "augment": cfg["augment"],
                }
            )
            continue

        model = YOLO(cfg["weights"])
        train_kw: dict[str, Any] = dict(
            data=str(data_path),
            epochs=args.epochs,
            imgsz=int(cfg["imgsz"]),
            batch=args.batch,
            fraction=args.fraction,
            workers=args.workers,
            project=str(project),
            name=run_name,
            exist_ok=True,
            seed=args.seed,
            **device_kw,
        )
        if isinstance(cfg.get("augment"), dict):
            train_kw.update(cfg["augment"])

        model.train(**train_kw)

        results_csv = run_dir / "results.csv"
        rows = read_results_csv(results_csv)
        last = rows[-1] if rows else {}
        metrics = pick_metrics(last) if last else {}

        best_pt = run_dir / "weights" / "best.pt"
        last_pt = run_dir / "weights" / "last.pt"

        summary["runs"].append(
            {
                "tag": cfg["tag"],
                "run_name": run_name,
                "weights_init": cfg["weights"],
                "imgsz": cfg["imgsz"],
                "augment": cfg["augment"],
                "results_csv": str(results_csv.relative_to(root)) if results_csv.is_relative_to(root) else str(results_csv),
                "weights_best": str(best_pt) if best_pt.is_file() else None,
                "weights_last": str(last_pt) if last_pt.is_file() else None,
                "metrics_last_epoch": metrics,
            }
        )

    # Chon run tot nhat theo map50_95, fallback map50
    best_run = None
    best_score = -1.0
    for r in summary["runs"]:
        m = r.get("metrics_last_epoch") or {}
        s = m.get("map50_95")
        if s is None:
            s = m.get("map50")
        if isinstance(s, (int, float)) and s > best_score:
            best_score = float(s)
            best_run = r
    summary["best_by_map"] = {
        "run_name": best_run.get("run_name") if isinstance(best_run, dict) else None,
        "score": best_score if best_score >= 0 else None,
    }

    out_path = group_dir / "summary.json"
    out_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nWrote summary: {out_path}")


if __name__ == "__main__":
    main()
