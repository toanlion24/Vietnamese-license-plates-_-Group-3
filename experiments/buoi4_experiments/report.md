# Buoi 4 - Cai tien mo hinh va thuc nghiem

## 1) Cau hinh da chay

- Preset: `quick2`
- Epochs: `1`
- Batch: `16`
- Device: `cpu`
- Fraction du lieu train: `0.15`
- Muc tieu: chay nhanh de so sanh 2 cau hinh trong mot phien lam viec.

## 2) Ket qua tong hop

Nguon: `experiments/buoi4_experiments/summary.json`

| Run | Weights | Img size | Augment | Precision | Recall | mAP50 | mAP50-95 |
|---|---|---:|---|---:|---:|---:|---:|
| `buoi4_experiments_y8n_416_default` | `yolov8n.pt` | 416 | mac dinh | 0.00309 | 0.80934 | **0.09983** | **0.07741** |
| `buoi4_experiments_y8n_320_lightaug` | `yolov8n.pt` | 320 | nhe (`hsv+degrees+mosaic`) | 0.00433 | 0.84271 | 0.04309 | 0.01778 |

## 3) Run tot nhat

- Theo tieu chi `mAP50-95`: `buoi4_experiments_y8n_416_default` (0.07741).
- Theo `mAP50`: `buoi4_experiments_y8n_416_default` (0.09983).

## 4) Phan tich nhanh

- Cung dung `yolov8n`, viec giam `imgsz` xuong 320 va them augment nhe trong 1 epoch chua cai thien duoc mAP.
- Recall cao nhung precision rat thap -> model dang xu huong du doan khong on dinh khi moi train rat ngan.
- Error analysis mau 120 anh (`error_y8n_416_default_val.json`, `error_y8n_320_lightaug_val.json`) cho thay TP=0 o nguong hien tai, xac nhan can train lau hon de model hoi tu.

## 5) Ket luan cho Buoi 4

- Ket qua thuc nghiem nhanh da hoan tat va co the dung de minh hoa quy trinh so sanh cau hinh.
- Cau hinh duoc de xuat giu lam baseline cho vong tiep theo: `y8n_416_default`.
- De co ket qua co y nghia hoc thuat/bao cao cuoi:
  - tang `epochs` (>= 30),
  - mo rong so cau hinh (`fast2` hoac `full3`),
  - giu nguyen luong danh gia trong `demo_buoi4_experiments.ipynb`.

## 6) Lenh tai lap

```powershell
python -m src.detector.run_buoi4_experiments --preset quick2 --epochs 1 --batch 16 --fraction 0.15 --workers 0 --device cpu
```

```powershell
python -m src.detector.run_buoi4_experiments --preset fast2 --epochs 10 --batch 16 --device cpu
```
