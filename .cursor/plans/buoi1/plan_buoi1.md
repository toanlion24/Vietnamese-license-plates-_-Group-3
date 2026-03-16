## Buổi 1 – Khởi động & Lập kế hoạch

### 1. Thông tin chung

- **Đề tài**: Nhận diện biển số xe Việt Nam (phát hiện + OCR)  
- **Mục tiêu tổng thể**:
  - Xây dựng hệ thống nhận diện biển số gồm:
    - Phát hiện vùng biển số (object detection).
    - Nhận dạng ký tự trên biển số (OCR).
  - Đạt **độ chính xác OCR ≥ 85%** trên **≥ 200 ảnh biển số thực tế** (không dùng để train).
  - Có **demo** chạy được trên ảnh/video/webcam, kèm **báo cáo + slide** hoàn chỉnh.

### 2. Chuẩn bị môi trường làm việc

**Nhiệm vụ**

1. Tạo cấu trúc thư mục ban đầu trong `ComputerVisionPj`:
   - `data/` – dữ liệu gốc và nhãn.
   - `notebooks/` – EDA, thử nghiệm.
   - `src/` – mã nguồn chính.
   - `docs/` – tài liệu, kế hoạch, báo cáo.

2. Cài đặt Python (nếu chưa có):  
   - Phiên bản: **Python 3.10+**.  
   - Khi cài, tick **“Add Python to PATH”**.

3. Tạo môi trường ảo:
   - Trong thư mục project:
     - `python -m venv .venv`
     - Kích hoạt (PowerShell): `.\.venv\Scripts\Activate.ps1`

4. Cài các thư viện cơ bản:
   - `pip install opencv-python numpy matplotlib`

**Kết quả mong đợi**

- Có cấu trúc thư mục project rõ ràng.  
- Môi trường ảo `.venv` hoạt động, import được OpenCV, NumPy, Matplotlib trong Python.

### 3. Mô tả bài toán & mục tiêu chi tiết

**Nhiệm vụ**

1. Viết mô tả bài toán (1–2 trang, lưu vào `docs/mo_ta_bai_toan.md` hoặc `.docx`):
   - Bài toán: “Nhận diện biển số xe Việt Nam từ ảnh/video (phát hiện + OCR)”.
   - Ứng dụng: bãi giữ xe, trạm thu phí, camera giao thông, hệ thống quản lý ra/vào.
   - Lợi ích: tự động hóa, giảm công sức con người, tăng độ chính xác.

2. Xác định rõ **input / output**:
   - **Input**:
     - Ảnh tĩnh chứa xe (jpg/png).
     - Hoặc video (mp4) / luồng webcam.
   - **Output**:
     - Ảnh/video có vẽ khung (bounding box) quanh biển số.
     - Chuỗi text tương ứng với từng biển số (ví dụ: `51F-123.45`).

3. Ghi rõ các **mục tiêu định lượng**:
   - Detection:
     - mAP trên tập test nhỏ khoảng ≥ 0.8 (mốc tham khảo, có thể điều chỉnh).
   - OCR:
     - Character accuracy ≥ 85% trên ≥ 200 ảnh biển số thực tế.
   - Demo:
     - Chạy được trên ít nhất 1 video/quay webcam, hiển thị kết quả thời gian thực hoặc near real-time.

**Kết quả mong đợi**

- Có file mô tả bài toán, nêu rõ bối cảnh, input/output, và goal định lượng để sau này bám theo.

### 4. Khảo sát & chốt stack công nghệ

**Nhiệm vụ**

1. Hiểu pipeline giải pháp ở mức khái niệm:
   - Bước 1: YOLO phát hiện vùng biển số trong ảnh.
   - Bước 2: Cắt (crop) vùng đó ra.
   - Bước 3: Tiền xử lý ảnh biển số (gray, resize, threshold…).
   - Bước 4: EasyOCR/Tesseract đọc ký tự.
   - Bước 5: Hậu xử lý bằng quy tắc (regex) biển số Việt Nam.

2. Ghi lại lựa chọn công nghệ:
   - Ngôn ngữ: **Python**.
   - Detection: **YOLOv8** (thư viện Ultralytics).
   - OCR: **EasyOCR** (ưu tiên) / Tesseract (dự phòng).
   - Xử lý ảnh: **OpenCV**.
   - Demo: **Streamlit/Gradio** hoặc GUI với OpenCV.

3. Ghi ngắn gọn lý do:
   - YOLOv8: hiện đại, tài liệu nhiều, dễ train/finetune.
   - EasyOCR: dễ dùng, hỗ trợ số và chữ cái Latinh, không cần train từ đầu.
   - OpenCV: thư viện chuẩn cho xử lý ảnh.

**Kết quả mong đợi**

- Có một đoạn tài liệu trong `docs/mo_ta_bai_toan.md` (hoặc file riêng) nêu rõ stack công nghệ và vai trò của từng thành phần.

### 5. Phân tích format biển số Việt Nam

**Nhiệm vụ**

1. Ghi lại một số dạng biển số thông dụng (xe máy, ô tô):  
   - Ví dụ: `59S2-123.45`, `51F-123.45`, `30A-123.45`, `73D1-56789`, …

2. Mô tả cấu trúc tổng quát:
   - `XXY-ZZZ.ZZ` hoặc `XXY ZZZ.ZZ`  
     - `XX`: 2 chữ số – mã tỉnh.  
     - `Y`: chữ cái.  
     - `ZZZ.ZZ`: 4–5 chữ số, có thể có dấu chấm.

3. Đề xuất 1–2 mẫu regex đơn giản (sẽ hoàn thiện sau), ví dụ:
   - `^[0-9]{2}[A-Z][A-Z0-9]-?[0-9]{4,5}$`

4. Liệt kê dự đoán các lỗi OCR dễ xảy ra:
   - `O ↔ 0`, `I ↔ 1`, `S ↔ 5`, thiếu dấu gạch/dấu chấm,…

**Kết quả mong đợi**

- Một mục nhỏ trong tài liệu mô tả cấu trúc biển số VN và một vài regex cơ bản để dùng làm hậu xử lý sau này.

### 6. Vẽ sơ đồ pipeline hệ thống

**Nhiệm vụ**

1. Vẽ sơ đồ khối (trên giấy, PowerPoint, hoặc lưu vào `docs/pipeline.png`), gồm các bước:

   1. `Input` (Ảnh / Video / Webcam)  
   2. `YOLO Detector` → phát hiện bounding box biển số  
   3. `Crop & Preprocess` (OpenCV)  
   4. `OCR` (EasyOCR/Tesseract)  
   5. `Post-processing` (regex, sửa lỗi)  
   6. `Output` (Ảnh/video có bbox + text, danh sách biển số dạng text)

2. Viết mô tả 1–2 câu cho từng khối trong file tài liệu.

**Kết quả mong đợi**

- Có hình/sơ đồ pipeline và mô tả tương ứng để đưa thẳng vào báo cáo/slide sau này.

### 7. Lập timeline 7 buổi & phân công

**Nhiệm vụ**

1. Ghi lại timeline (tóm tắt):

   - **Buổi 1**: Khởi động & lập kế hoạch (file hiện tại).  
   - **Buổi 2**: Thu thập dữ liệu + gán nhãn + EDA cơ bản.  
   - **Buổi 3**: Huấn luyện mô hình YOLO baseline, chạy inference thử.  
   - **Buổi 4**: Cải tiến mô hình, thử ≥ 2 cấu hình, so sánh kết quả.  
   - **Buổi 5**: Tích hợp OCR + tiền xử lý + đánh giá toàn pipeline.  
   - **Buổi 6**: Xây demo (CLI/web/GUI) và test với dữ liệu thực tế.  
   - **Buổi 7**: Hoàn thiện báo cáo, slide, diễn tập bảo vệ.

2. Nếu làm nhóm: phân công người phụ trách từng mảng (dữ liệu, YOLO, OCR, demo, báo cáo).

**Kết quả mong đợi**

- Có ghi chú timeline + phân công rõ ràng (một bảng hoặc danh sách trong tài liệu).

### 8. Tổng kết buổi 1

**Deliverables cuối buổi 1**

- Cấu trúc thư mục project + môi trường Python hoạt động.  
- Tài liệu mô tả bài toán + mục tiêu + stack công nghệ + format biển số VN.  
- Sơ đồ pipeline hệ thống.  
- Timeline 7 buổi và (nếu có) phân công thành viên.

**TODO cho buổi 2**

- Thu thập ≥ 300 ảnh biển số VN (ảnh hoặc trích frame video).  
- Gán nhãn ≥ 200 ảnh bằng LabelImg/Roboflow (class `license_plate`).  
- Viết script/Notebook EDA hiển thị vài ảnh + box, thống kê sơ bộ dữ liệu.

