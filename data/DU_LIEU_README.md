# Tổ chức thư mục dữ liệu (buổi 2) — sau migrate từ `datakangle`

## Cấu trúc thư mục

| Thư mục / file | Mục đích |
|----------------|----------|
| `data/images/raw/` | Ảnh gốc (tương đương “raw” trong plan: ảnh chưa đổi tên nguồn đã gom một chỗ). |
| `data/labels/raw/` | File nhãn YOLO `.txt` (bbox `class xc yc w h`), **cùng stem** với ảnh. |
| `data/splits/` | `train.txt`, `val.txt`, `test.txt` — mỗi dòng một đường dẫn ảnh tương đối từ **gốc repo**. |
| `data/data.yaml` | Cấu hình YOLO (Ultralytics), trỏ tới các file split. |
| `data/migration_from_datakangle.json` | Bản đồ tên cũ → `plate_XXXX` (tạo khi chạy script migrate). |

**Vì sao dùng `images/raw` thay vì chỉ `raw`?**  
Ultralytics YOLO tự tìm nhãn bằng cách thay đoạn `images` thành `labels` trong đường dẫn ảnh. Nếu đặt ảnh ở `data/raw/...` (không có chữ `images`), huấn luyện mặc định **không** khớp được `data/labels/...`.

## Quy ước đặt tên

- **Ảnh:** `plate_0001.png`, `plate_0002.png`, … (số thứ tự 4 chữ số, giữ phần mở rộng gốc: `.png` / `.jpg` / …).
- **Nhãn:** cùng stem, đuôi `.txt`: `plate_0001.txt`, `plate_0002.txt`, …
- **Một lớp detection:** toàn bộ class gốc (ví dụ BSD/BSV trong datakangle) được gom về class `0` = `license_plate` trong `data.yaml`.

## Lệnh thường dùng

Từ thư mục gốc repo:

```bash
# Migrate / cập nhật từ datakangle (ghi đè ảnh+nhãn trong data/images/raw và data/labels/raw)
python -m src.detector.organize_datakangle_for_buoi2

# Xem trước, không ghi file
python -m src.detector.organize_datakangle_for_buoi2 --dry-run

# Tạo lại train/val/test (70/20/10, seed 42)
python -m src.detector.prepare_splits
```

Nếu trong `datakangle` chỉ có nhãn polygon (thư mục `labels/`), chạy trước:

```bash
python -m src.detector.convert_polygon_to_yolo_bbox --dataset-root datakangle --swap-for-yolo-detect
```

sau đó mới `organize_datakangle_for_buoi2` (mặc định ưu tiên `labels_bbox/`).

## Thu thập thêm (plan mục 3)

Trích frame từ video vào cùng thư mục ảnh:

```bash
python -m src.preprocess.extract_video_frames --video path/to/video.mp4 --every 10
python -m src.preprocess.extract_video_frames --video clip.mp4 --every 5 --auto-index
```

Ảnh quá mờ / không đọc được biển: xoá tay hoặc không copy vào `data/images/raw/`.

## LabelImg (plan mục 4)

- **Open Dir:** `data/images/raw`
- **Change Save Dir:** `data/labels/raw`
- Định dạng **YOLO**, class: `license_plate` (một class, id `0` trong file `.txt`).

## EDA (plan mục 6)

```bash
jupyter notebook notebooks/eda_data.ipynb
```

## Tiền xử lý / augment thử (plan mục 7)

```bash
python -m src.preprocess.debug_augment_demo
python -m src.detector.prepare_splits --verify-only
```

Module: `src/preprocess/image_utils.py` (`load_image_bgr`, `resize_to_max_side`, `adjust_brightness_contrast`, `rotate_degrees`, …).
