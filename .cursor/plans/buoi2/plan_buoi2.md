## Buổi 2 – Thu thập & Tiền xử lý dữ liệu

### 1. Mục tiêu buổi 2

- Có bộ dữ liệu ban đầu cho bài toán nhận diện biển số xe Việt Nam:
  - Tối thiểu **300–500 ảnh** có chứa biển số VN (tự chụp hoặc từ video).
  - Ít nhất **200 ảnh đã được gán nhãn** bounding box biển số theo định dạng YOLO (class `license_plate`).
- Tổ chức dữ liệu rõ ràng trong thư mục `data/`.
- Có **script/Notebook EDA** để xem nhanh và thống kê dữ liệu.
- Có **hàm tiền xử lý ảnh cơ bản** (resize, augment nhẹ) phục vụ huấn luyện YOLO ở buổi sau.

---

### 2. Cấu trúc thư mục dữ liệu

**Nhiệm vụ**

1. Bên trong `data/`, tạo các thư mục con:
   - `data/raw/` – ảnh gốc (jpg/png) và/hoặc frame trích từ video.
   - `data/labels/` – file nhãn YOLO (`.txt`) tương ứng với từng ảnh.
   - `data/splits/` – các file text chứa danh sách ảnh cho train/val/test.

2. Quy ước tên file:
   - Ảnh: `plate_0001.jpg`, `plate_0002.jpg`, … (không bắt buộc nhưng nên nhất quán).
   - Nhãn: cùng tên với ảnh, khác phần mở rộng: `plate_0001.txt`, `plate_0002.txt`, …

**Kết quả mong đợi**

- Thư mục `data/` có cấu trúc rõ ràng, sẵn sàng cho LabelImg và YOLO sử dụng.

---

### 3. Thu thập dữ liệu ảnh

**Nhiệm vụ**

1. **Tự chụp ảnh/ghi video**:
   - Dùng điện thoại quay/chụp xe trong bãi gửi, ngoài đường… đảm bảo biển số rõ ở mức chấp nhận được.
   - Cố gắng đa dạng:
     - Ngày / đêm (nếu có thể).
     - Xe máy và ô tô.
     - Góc chụp khác nhau (chính diện, chéo, xa/gần).

2. **Trích frame từ video** (nếu dùng video):
   - Viết script Python đơn giản trong `notebooks/` hoặc `src/preprocess/` để:
     - Mở file video bằng OpenCV.
     - Mỗi N frame (ví dụ 5 hoặc 10) lưu một ảnh ra `data/raw/`.

3. **Lọc ảnh quá xấu**:
   - Loại bỏ ảnh mà biển số hoàn toàn không đọc được (quá mờ, cháy sáng, bị che hết…).

**Kết quả mong đợi**

- Có tối thiểu **300–500 ảnh** đặt trong `data/raw/` với tên file gọn, dễ đọc.

---

### 4. Gán nhãn bounding box bằng LabelImg (YOLO format)

**Nhiệm vụ**

1. **Cài đặt LabelImg** (làm 1 lần):
   - Có thể dùng bản cài sẵn (Windows exe) hoặc dùng Python:
     - `pip install labelImg` (trong môi trường `.venv`).
     - Chạy: `labelImg`.

2. **Cấu hình dự án gán nhãn**:
   - Thư mục ảnh: chọn `data/raw/`.
   - Thư mục nhãn: chọn `data/labels/`.
   - Chọn định dạng: **YOLO**.
   - Tạo class duy nhất: `license_plate`.

3. **Tiến hành gán nhãn**:
   - Với mỗi ảnh:
     - Vẽ bounding box quanh vùng biển số (nếu có nhiều biển thì gán tất cả).
     - Gán class `license_plate`.
   - Lưu lại file `.txt` cho từng ảnh (LabelImg tự tạo).

4. **Mục tiêu số lượng**:
   - Trong buổi 2: cố gắng annotated được **ít nhất 200 ảnh**.
   - Nếu có thời gian, càng nhiều càng tốt (300–400 ảnh gán nhãn sẽ giúp YOLO học tốt hơn).

**Kết quả mong đợi**

- Thư mục `data/labels/` chứa ≥ 200 file `.txt` YOLO tương ứng với ảnh trong `data/raw/`.

---

### 5. Chia train/val/test (splits)

**Nhiệm vụ**

1. Viết script Python nhỏ (đặt ở `src/detector/prepare_splits.py` hoặc notebook):
   - Đọc danh sách ảnh đã có nhãn (dựa vào `data/labels/`).
   - Random shuffle danh sách.
   - Chia tỷ lệ, ví dụ:
     - Train: 70%
     - Val: 20%
     - Test: 10%
   - Ghi ra 3 file:
     - `data/splits/train.txt`
     - `data/splits/val.txt`
     - `data/splits/test.txt`
   - Mỗi dòng trong file là **đường dẫn tương đối** tới ảnh (ví dụ: `data/raw/plate_0001.jpg` hoặc tuỳ cách dùng YOLO sau này).

2. Kiểm tra lại:
   - Mỗi ảnh trong train/val/test có file nhãn tương ứng trong `data/labels/`.

**Kết quả mong đợi**

- Có đủ 3 file splits, dùng được ngay cho huấn luyện YOLO ở buổi 3.

---

### 6. EDA (khám phá dữ liệu) cơ bản

**Nhiệm vụ**

1. Tạo notebook mới: `notebooks/eda_data.ipynb`.
2. Các bước nên làm trong notebook:
   - Đọc danh sách ảnh từ `data/raw/` và nhãn từ `data/labels/`.
   - Hiển thị ngẫu nhiên 10–20 ảnh kèm bounding box để kiểm tra nhãn.
   - Thống kê:
     - Số ảnh tổng, số ảnh được gán nhãn.
     - Trung bình số biển số/ảnh.
     - Kích thước ảnh (width, height) phổ biến.
     - Kích thước box biển số tương đối so với ảnh (diện tích box / diện tích ảnh).
   - (Tuỳ chọn) Gắn tag đơn giản cho một vài ảnh (ngày/đêm, gần/xa) để quan sát độ đa dạng.

**Kết quả mong đợi**

- Notebook EDA chạy hoàn chỉnh, có hình ảnh minh hoạ và vài thống kê cơ bản để đưa vào báo cáo sau này.

---

### 7. Tiền xử lý & augment cơ bản cho huấn luyện YOLO

**Nhiệm vụ**

1. Tạo module tiền xử lý trong `src/preprocess/`, ví dụ `src/preprocess/image_utils.py`:
   - Hàm đọc ảnh từ đường dẫn, resize về kích thước chuẩn (nếu cần).
   - Augment đơn giản:
     - Thay đổi độ sáng/độ tương phản.
     - Xoay nhẹ (±5–10 độ) nếu cần.
   - Lưu ý: YOLOv8 đã hỗ trợ augment nội bộ, nên phần này có thể rất nhẹ, chủ yếu để test.

2. Viết script nhỏ để áp dụng tiền xử lý/augment cho 1–2 ảnh và lưu kết quả ra `data/debug_aug/` để kiểm tra.

**Kết quả mong đợi**

- Có module/hàm tiền xử lý cơ bản, sẵn sàng dùng trong script train YOLO ở buổi 3.

---

### 8. Deliverables cuối buổi 2

- Thư mục `data/raw/` chứa ≥ 300 ảnh biển số VN (hoặc frame từ video).
- Thư mục `data/labels/` chứa ≥ 200 file nhãn YOLO (class `license_plate`).
- Bộ chia train/val/test trong `data/splits/`.
- Notebook `notebooks/eda_data.ipynb` với hình và thống kê cơ bản.
- Module tiền xử lý ảnh cơ bản trong `src/preprocess/` (có thể mới chỉ là khung hàm).

