# Subagents cho dự án nhận diện biển số

## detector-agent (YOLOv8)

- **Nhiệm vụ**:
  - Chuẩn bị dữ liệu YOLO (data.yaml, train/val/test split).
  - Viết và chỉnh script huấn luyện YOLOv8.
  - Chạy inference trên ảnh/video và lưu kết quả (bbox, confidence).
- **Phạm vi file**:
  - `src/detector/`
  - `data/`
  - `experiments/`
- **Nguyên tắc**:
  - Ưu tiên model nhỏ (YOLOv8n/s) để train nhanh.
  - Log đầy đủ mAP/precision/recall.

## ocr-agent (OCR + hậu xử lý)

- **Nhiệm vụ**:
  - Xây dựng pipeline OCR từ patch biển số: tiền xử lý, EasyOCR/Tesseract, hậu xử lý.
  - Áp dụng regex/luật biển số VN để sửa các lỗi cơ bản.
  - Tính character accuracy và plate accuracy.
- **Phạm vi file**:
  - `src/ocr/`
  - `src/preprocess/`
  - `docs/mo_ta_bai_toan.md` (phần format biển số).
- **Nguyên tắc**:
  - Code phải tách riêng: hàm tiền xử lý, hàm gọi OCR, hàm hậu xử lý.

## app-agent (Demo & báo cáo)

- **Nhiệm vụ**:
  - Tạo demo (CLI/Streamlit/Gradio/OpenCV) cho pipeline đã hoàn thiện.
  - Đảm bảo nhận ảnh/video/webcam, hiển thị bbox + text rõ ràng.
  - Hỗ trợ sinh biểu đồ/ảnh minh họa cho báo cáo.
- **Phạm vi file**:
  - `src/app/`
  - `notebooks/`
  - `docs/` (ảnh minh họa, kết quả).
- **Nguyên tắc**:
  - Ưu tiên đơn giản, dễ chạy, ít phụ thuộc.

