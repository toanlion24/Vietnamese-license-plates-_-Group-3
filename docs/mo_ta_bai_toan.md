# Đồ án: Nhận diện biển số xe Việt Nam

## 1. Bài toán

Mục tiêu của đồ án là xây dựng một hệ thống nhận diện biển số xe Việt Nam từ ảnh hoặc video.
Hệ thống cần thực hiện hai nhiệm vụ chính:

- **Phát hiện** được vùng chứa biển số trên ảnh (bài toán object detection).
- **Nhận dạng ký tự** trên biển số (bài toán OCR – Optical Character Recognition).

Ứng dụng thực tế của hệ thống:

- Tự động ghi nhận biển số xe tại bãi giữ xe, chung cư, tòa nhà.
- Hỗ trợ quản lý xe ra/vào, giảm công việc nhập tay cho nhân viên bảo vệ.
- Có thể mở rộng cho các bài toán giám sát giao thông, phạt nguội, trạm thu phí tự động,…

## 2. Input / Output

- **Input**:
  - Ảnh tĩnh (định dạng phổ biến như JPG, PNG) có chứa xe và biển số.
  - Hoặc video (ví dụ MP4) / luồng webcam quay cảnh có xe di chuyển.

- **Output**:
  - Ảnh hoặc frame video được vẽ khung (bounding box) quanh từng biển số phát hiện được.
  - Chuỗi ký tự biển số tương ứng với mỗi khung, ví dụ: `51F-123.45`.
  - Có thể xuất danh sách biển số đọc được ra màn hình, file log hoặc cơ sở dữ liệu đơn giản.

## 3. Mục tiêu định lượng

Để đánh giá chất lượng hệ thống, đề tài đặt ra một số mục tiêu định lượng như sau:

- **Detection (phát hiện biển số)**:
  - Mô hình YOLO sau khi huấn luyện đạt mAP trên tập test nhỏ khoảng **≥ 0.8** (mốc tham khảo, có thể điều chỉnh theo thực nghiệm).

- **OCR (nhận dạng ký tự)**:
  - Độ chính xác ký tự (character accuracy) **≥ 85%** trên **ít nhất 200 ảnh biển số thực tế** (không dùng để train).
  - Bổ sung thêm metric plate accuracy (tỷ lệ biển số được đọc đúng toàn bộ) để phân tích.

- **Demo**:
  - Hệ thống chạy được trên ít nhất một video thực tế hoặc luồng webcam, hiển thị kết quả gần thời gian thực (real-time hoặc near real-time).

## 4. Stack công nghệ dự kiến

- **Ngôn ngữ**: Python.
- **Phát hiện biển số (detection)**: mô hình YOLOv8 (thư viện Ultralytics).
- **Nhận dạng ký tự (OCR)**: EasyOCR (ưu tiên), Tesseract làm lựa chọn dự phòng.
- **Xử lý ảnh**: OpenCV (đọc/ghi ảnh, crop, resize, chuyển xám, threshold,…).
- **Demo giao diện**: Streamlit hoặc Gradio cho web đơn giản, hoặc GUI dựa trên OpenCV.

**Lý do lựa chọn**:

- YOLOv8 là mô hình detection hiện đại, có sẵn code huấn luyện và suy luận (inference), phù hợp với dataset vừa và nhỏ, nhiều tài liệu hướng dẫn.
- EasyOCR hỗ trợ tốt ký tự Latin và chữ số, dễ sử dụng, không bắt buộc phải tự huấn luyện từ đầu.
- OpenCV là thư viện chuẩn cho xử lý ảnh trong Python, hỗ trợ hầu hết thao tác cần thiết.

## 5. Cấu trúc biển số Việt Nam (phác thảo)

Một số ví dụ biển số phổ biến:

- `59S2-123.45`
- `51F-123.45`
- `30A-123.45`
- `73D1-56789`

Dạng chung (đơn giản hóa) có thể mô tả như sau:

- `XXY-ZZZ.ZZ` hoặc `XXY ZZZ.ZZ`
  - `XX`: 2 chữ số – mã tỉnh/thành.
  - `Y`: chữ cái (A, B, C,…).
  - `ZZZ.ZZ`: 4–5 chữ số, có thể có hoặc không có dấu chấm.

Mẫu regex tham khảo ban đầu (sẽ điều chỉnh sau theo thực nghiệm):

- `^[0-9]{2}[A-Z][A-Z0-9]-?[0-9]{4,5}$`

Một số lỗi OCR dự đoán có thể xảy ra:

- Nhầm lẫn giữa chữ cái và chữ số: `O` ↔ `0`, `I` ↔ `1`, `S` ↔ `5`.
- Thiếu dấu gạch ngang hoặc dấu chấm nhưng phần số vẫn đúng.

Các quy tắc này sẽ được dùng ở bước hậu xử lý để sửa một số lỗi đơn giản từ kết quả OCR.

## 6. Pipeline hệ thống (mô tả)

Pipeline tổng thể của hệ thống được mô tả bằng các bước sau:

1. **Input**: đọc ảnh hoặc frame video từ file/video/webcam.
2. **YOLO Detector**: sử dụng mô hình YOLOv8 để phát hiện vùng chứa biển số, trả về danh sách bounding box và độ tự tin (confidence).
3. **Crop & Preprocess**:
   - Cắt (crop) từng vùng biển số từ ảnh gốc theo bounding box.
   - Tiền xử lý: chuyển sang ảnh xám (grayscale), resize về kích thước chuẩn, thử các phương pháp threshold để làm rõ ký tự.
4. **OCR (EasyOCR/Tesseract)**:
   - Nhận ảnh biển số đã tiền xử lý, đọc ra chuỗi ký tự thô (chưa làm sạch).
5. **Post-processing**:
   - Làm sạch chuỗi ký tự: chuyển sang uppercase, loại bỏ ký tự lạ, chuẩn hóa dấu.
   - Áp dụng regex/luật cấu trúc biển số Việt Nam để phát hiện và sửa một số lỗi đơn giản.
6. **Output**:
   - Ảnh/video với khung biển số và text hiển thị ngay trên khung.
   - Danh sách các biển số dạng text phục vụ cho việc lưu trữ, tra cứu hoặc thống kê.

## 7. Timeline 7 buổi (tóm tắt)

- **Buổi 1**: Khởi động & lập kế hoạch, chuẩn môi trường, viết tài liệu mô tả (file hiện tại).
- **Buổi 2**: Thu thập dữ liệu, gán nhãn ≥ 200 ảnh biển số, thực hiện EDA cơ bản.
- **Buổi 3**: Cấu hình YOLO, huấn luyện mô hình detection baseline, chạy thử inference.
- **Buổi 4**: Thử ≥ 2 cấu hình/kiến trúc YOLO, so sánh kết quả, chọn mô hình tốt nhất.
- **Buổi 5**: Tích hợp OCR + hậu xử lý, đánh giá end-to-end trên ≥ 200 ảnh biển số thực tế.
- **Buổi 6**: Xây dựng demo (CLI/web/GUI), chạy với video/webcam, sửa lỗi phát sinh.
- **Buổi 7**: Hoàn thiện báo cáo, slide, diễn tập bảo vệ, đóng gói mã nguồn và hướng dẫn chạy.

## 8. Buổi 3 — Detector baseline (lệnh tham chiếu)

- **Cấu hình dataset**: `data/data.yaml`, splits trong `data/splits/`.
- **Huấn luyện**: `python -m src.detector.train_baseline` — thử nhanh `--epochs 3`; baseline đủ theo kế hoạch buổi 3: `--epochs 50` (có GPU), kèm `--val-initial` nếu cần metric trước train.
- **Inference** (ảnh / thư mục / video / tập test): `python -m src.detector.infer_baseline --weights <best.pt> --source <ảnh hoặc thư mục>` hoặc `--from-split test --max-images 20 --name infer_test_sample`.
- **Phân tích TP/FP/FN**: `python -m src.detector.analyze_detection_errors --weights <best.pt>` (mặc định val); thêm `--split-file data/splits/test.txt` cho tập test.
- **Notebook**: `notebooks/eda_data.ipynb` — phần Buổi 3 tổng hợp metric, curves và ảnh inference mẫu.

