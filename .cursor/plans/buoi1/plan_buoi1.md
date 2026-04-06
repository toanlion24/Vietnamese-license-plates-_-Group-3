## Buổi 1 – Khởi động & Lập kế hoạch (bản gọn 1 trang)

### 1) Mục tiêu buổi
- Chốt phạm vi đề tài: **Detection (YOLO) + OCR + hậu xử lý biển số VN**.
- Hoàn tất môi trường làm việc và cấu trúc repo.
- Có mô tả bài toán, sơ đồ pipeline, timeline 7 buổi để bắt đầu triển khai.

### 2) Checklist triển khai nhanh
1. **Setup project**
   - Tạo/kiểm tra thư mục: `data/`, `notebooks/`, `src/`, `docs/`.
   - Giữ dataset local (ví dụ `datakangle/`) ngoài git; trên repo giữ `data/data.yaml` và script chuẩn bị dữ liệu.
2. **Môi trường**
   - Python 3.10+, tạo `.venv`, cài tối thiểu: `opencv-python numpy matplotlib`.
   - Tuỳ chọn sớm: `ultralytics`, `easyocr`.
3. **Mô tả bài toán**
   - Viết `docs/mo_ta_bai_toan.md`: input, output, ứng dụng, giới hạn.
   - Mục tiêu định lượng tham chiếu: OCR >= 85% trên >= 200 ảnh test thực.
4. **Chốt pipeline kỹ thuật**
   - Luồng chuẩn: `YOLO -> Crop -> Preprocess -> OCR -> Postprocess`.
   - Thống nhất stack: Python + Ultralytics + OpenCV + EasyOCR/Tesseract.
5. **Phân tích format biển số VN**
   - Ghi format phổ biến + regex khởi đầu + lỗi OCR thường gặp (`O/0`, `I/1`, thiếu `-` hoặc `.`).
6. **Kế hoạch thực thi**
   - Chốt timeline 7 buổi, phân công (nếu làm nhóm), tiêu chí done cho từng buổi.

### 3) Done Criteria (kết thúc buổi 1)
- [ ] Chạy được môi trường `.venv` và import thư viện cơ bản.
- [ ] Có `docs/mo_ta_bai_toan.md` với input/output + mục tiêu đo lường.
- [ ] Có sơ đồ pipeline (Mermaid hoặc ảnh trong `docs/`).
- [ ] Có timeline 7 buổi + người phụ trách (nếu có).
- [ ] Sẵn sàng bước sang buổi 2 (thu thập + gán nhãn + EDA).

### 4) Lỗi thường gặp & xử lý nhanh
- **PowerShell không activate venv**: chỉnh execution policy cho máy cá nhân.
- **Commit nhầm dataset nặng**: kiểm tra `.gitignore`, chỉ commit config + script.
- **Mục tiêu quá rộng**: bám MVP trước (1 class `license_plate`, ảnh tĩnh -> video/webcam sau).

### 5) Liên kết tham khảo trong buổi 1
- Toán + thuật toán minh hoạ: `buoi1_toan_va_thuat_toan_pipeline.md`
- Demo script: `demo_buoi1_pipeline_minh_hoa.py`
- Demo notebook: `demo_buoi1_pipeline_minh_hoa.ipynb`
