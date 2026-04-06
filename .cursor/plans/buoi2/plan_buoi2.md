## Buổi 2 – Dữ liệu, nhãn, EDA, tiền xử lý (bản gọn 1 trang)

### 1) Mục tiêu buổi
- Có dataset dùng được cho YOLO:
  - **>= 300 ảnh** chứa biển số.
  - **>= 200 ảnh có nhãn YOLO bbox** (class `license_plate`).
- Có `train/val/test` và notebook EDA để kiểm tra chất lượng dữ liệu.
- Có module tiền xử lý/augment cơ bản để test trước buổi train.

### 2) Checklist triển khai nhanh
1. **Tổ chức thư mục dữ liệu**
   - Thực tế đang dùng layout tương thích YOLO: `data/images/raw`, `data/labels/raw`, `data/splits`.
   - Quy ước tên đồng nhất: `plate_0001.*`, `plate_0002.*` (ảnh và nhãn cùng stem).
2. **Thu thập dữ liệu**
   - Chụp/quay đa dạng: ngày/đêm, xa/gần, xe máy/ô tô.
   - Nếu dùng video: trích frame định kỳ bằng script (`src/preprocess/extract_video_frames.py`).
   - Loại ảnh quá mờ/cháy sáng/che biển số.
3. **Gán nhãn**
   - LabelImg: image dir = `data/images/raw`, label dir = `data/labels/raw`, format YOLO.
   - Class thống nhất: `license_plate` (id 0).
4. **Chia split**
   - Dùng `src/detector/prepare_splits.py` theo tỷ lệ `70/20/10`.
   - Chạy verify để kiểm tra ảnh và nhãn đều tồn tại.
5. **EDA**
   - Notebook `notebooks/eda_data.ipynb`:
     - số ảnh có/không nhãn,
     - bbox/ảnh,
     - histogram kích thước ảnh và diện tích bbox,
     - hiển thị mẫu ảnh + box để kiểm tra nhãn.
6. **Tiền xử lý & augment nhẹ**
   - `src/preprocess/image_utils.py` + demo `src/preprocess/debug_augment_demo.py`.
   - Các phép tối thiểu: resize, sáng/tương phản, xoay nhẹ.

### 3) Lệnh chạy nhanh
```bash
python -m src.detector.organize_datakangle_for_buoi2
python -m src.detector.prepare_splits
python -m src.detector.prepare_splits --verify-only
python -m src.preprocess.debug_augment_demo
jupyter notebook notebooks/eda_data.ipynb
```

### 4) Done Criteria (kết thúc buổi 2)
- [ ] `data/images/raw` có >= 300 ảnh.
- [ ] `data/labels/raw` có >= 200 file nhãn hợp lệ.
- [ ] `data/splits/train.txt`, `val.txt`, `test.txt` tồn tại và verify pass.
- [ ] Notebook EDA chạy được, có biểu đồ + ảnh minh hoạ bbox.
- [ ] Script preprocess/augment chạy và tạo output test.

### 5) Lỗi thường gặp & xử lý nhanh
- **Lệch đường dẫn giữa raw/labels**: luôn kiểm tra cùng stem `plate_xxxx`.
- **Không train được vì không tìm thấy nhãn**: đảm bảo đường dẫn ảnh chứa `images` (Ultralytics map `images -> labels`).
- **Split có ảnh không có nhãn**: chạy `--verify-only`, gán nhãn bổ sung rồi tạo split lại.
- **Nhãn sai vị trí**: kiểm tra bằng lưới ảnh trong EDA trước khi train.

