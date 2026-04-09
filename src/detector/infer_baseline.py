"""
Inference YOLO baseline: một ảnh, thư mục, video, hoặc danh sách từ split train/val/test.

Kết quả (ảnh có bbox) lưu dưới `experiments/<name>/` (mặc định Ultralytics).

Chạy từ gốc repo:
  python -m src.detector.infer_baseline --weights experiments/baseline_trial_1ep/weights/best.pt --source path/to/img.jpg
  python -m src.detector.infer_baseline --weights ... --source data/images/raw
  python -m src.detector.infer_baseline --weights ... --from-split test --max-images 20 --name infer_test_sample
  python -m src.detector.infer_baseline --weights yolov8n.pt --source video.mp4 --name coco_demo
"""

from __future__ import annotations

import argparse
from pathlib import Path

from ultralytics import YOLO


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def paths_from_split(root: Path, split_name: str, max_images: int) -> list[Path]:
    split_file = root / "data" / "splits" / f"{split_name}.txt"
    if not split_file.is_file():
        raise SystemExit(f"Không thấy {split_file}")
    lines = [ln.strip() for ln in split_file.read_text(encoding="utf-8").splitlines() if ln.strip()]
    out: list[Path] = []
    for rel in lines:
        if max_images > 0 and len(out) >= max_images:
            break
        p = (root / rel).resolve()
        if p.is_file():
            out.append(p)
    if not out:
        raise SystemExit(f"Không có file ảnh hợp lệ trong split {split_name!r} (sau khi resolve đường dẫn).")
    return out


def main() -> None:
    root = repo_root()
    default_project = root / "experiments"

    p = argparse.ArgumentParser(description="YOLO inference — ảnh / thư mục / video / split")
    p.add_argument("--weights", type=str, required=True, help="best.pt hoặc yolov8n.pt")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument(
        "--source",
        type=str,
        help="Ảnh, thư mục, video, hoặc glob (vd. 'data/images/raw/plate_*.jpg')",
    )
    src.add_argument(
        "--from-split",
        type=str,
        choices=("train", "val", "test"),
        help="Lấy danh sách ảnh từ data/splits/<split>.txt (đường dẫn tương đối repo)",
    )
    p.add_argument(
        "--max-images",
        type=int,
        default=50,
        help="Với --from-split: giới hạn số ảnh (0 = tất cả)",
    )
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--conf", type=float, default=0.25)
    p.add_argument("--device", type=str, default="", help="Rỗng = auto; 'cpu', '0', ...")
    p.add_argument("--project", type=Path, default=default_project)
    p.add_argument("--name", type=str, default="infer_baseline", help="Thư mục con trong experiments/")
    p.add_argument("--no-save", action="store_true", help="Không lưu ảnh kết quả (chỉ in log)")
    p.add_argument("--save-txt", action="store_true", help="Lưu thêm file nhãn YOLO dự đoán (.txt)")
    p.add_argument("--line-width", type=int, default=2)
    args = p.parse_args()

    project = args.project.resolve()
    project.mkdir(parents=True, exist_ok=True)

    if args.from_split:
        mx = args.max_images if args.max_images > 0 else 10**9
        paths = paths_from_split(root, args.from_split, mx)
        source: str | list[str] = [str(x) for x in paths]
    else:
        assert args.source is not None
        source = args.source

    model = YOLO(args.weights)
    device_kw = {"device": args.device} if args.device else {}

    results = model.predict(
        source=source,
        imgsz=args.imgsz,
        conf=args.conf,
        save=not args.no_save,
        project=str(project),
        name=args.name,
        exist_ok=True,
        save_txt=args.save_txt,
        line_width=args.line_width,
        verbose=True,
        **device_kw,
    )

    out_dir = project / args.name
    print(f"Done. Saved under: {out_dir}" if not args.no_save else "Done (no-save).")
    n = len(results)
    print(f"Processed {n} image(s) / frame batch(es).")


if __name__ == "__main__":
    main()
