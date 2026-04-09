## Flashcard on nhanh (Buoi 3)

> Format: **Thuat ngu** -> **Dinh nghia 1 dong** -> **Cach tra loi khi bi hoi**

1. **Baseline** -> Mo hinh moc ban dau de lam chuan so sanh cai tien. -> *"Nhom chon baseline de co moc P/R/mAP truoc khi toi uu o Buoi 4."*
2. **YOLOv8n** -> Phien ban YOLO nho, train nhanh, phu hop thu nghiem som. -> *"Em dung YOLOv8n de co ket qua nhanh roi moi tang cau hinh."*
3. **Detection** -> Bai toan tim vi tri doi tuong bang bounding box. -> *"Buoc nay chi tim vung bien so, chua doc chu."*
4. **bbox (bounding box)** -> Khung chu nhat bao quanh bien so trong anh. -> *"bbox dung la dieu kien can de OCR phia sau doc dung."*
5. **train / val / test** -> Train de hoc, val de theo doi khi huan luyen, test de danh gia cuoi. -> *"Nhom tach split de tranh danh gia lac quan do trung du lieu."*
6. **data.yaml** -> File khai bao duong dan du lieu va class cho YOLO. -> *"Neu data.yaml sai thi train/infer se sai ngay tu dau."*
7. **Epoch** -> Mot vong mo hinh di qua toan bo tap train. -> *"Epoch cang du thi mo hinh cang hoc on dinh hon, nhung can tranh overfit."*
8. **Batch size** -> So anh xu ly moi lan cap nhat trong so. -> *"Batch phu thuoc GPU; em chon muc vua du de train on dinh."*
9. **imgsz** -> Kich thuoc anh dua vao model (vi du 640). -> *"imgsz lon giup giu chi tiet bien nho nhung ton tai nguyen hon."*
10. **Inference** -> Dung model da train de du doan tren anh/video moi. -> *"Sau train em infer tren test de co anh minh hoa dung/sai cho bao cao."*
11. **Precision (P)** -> Trong cac du doan duong tinh, ty le dung la bao nhieu. -> *"Precision cao nghia la it bao nham (FP thap)."*
12. **Recall (R)** -> Trong cac doi tuong that, mo hinh bat duoc bao nhieu. -> *"Recall cao nghia la it bo sot (FN thap)."*
13. **mAP50** -> Chi so chat luong detection tai nguong IoU = 0.5. -> *"mAP50 cho cai nhin nhanh ve kha nang detect tong the."*
14. **mAP50-95** -> mAP trung binh nhieu nguong IoU (0.5->0.95), khat khe hon. -> *"Chi so nay phan anh do chinh xac vi tri bbox chat hon mAP50."*
15. **IoU** -> Muc chong lap giua bbox du doan va bbox ground-truth. -> *"IoU cang cao thi du doan cang khop vi tri that."*
16. **TP / FP / FN** -> Dung / bao nham / bo sot trong detection. -> *"Nhom dung TP/FP/FN de biet model sai kieu gi va sua dung cho."*
17. **Error analysis** -> Phan tich mau loi thay vi chi nhin 1 con so metric. -> *"Em liet ke top anh loi de thay nguyen nhan: bien nho, mo, nghieng, nen nhieu."*
18. **Checkpoint (`best.pt`, `last.pt`)** -> File trong so model duoc luu khi train. -> *"best.pt dung cho infer/bao cao vi la moc tot nhat theo metric."*
19. **Pretrained COCO** -> Trong so khoi tao tu du lieu COCO truoc khi fine-tune bien so. -> *"Pretrained giup hoi tu nhanh hon so voi train tu dau."*
20. **Fine-tune** -> Tinh chinh model pretrained tren du lieu bien so VN. -> *"Truoc fine-tune metric thap; sau du epoch metric phan anh dung hon."*

---

### 6 cau tra loi mau sieu ngan (hoc thuoc)

- **Vi sao can Buoi 3?** -> *"De co baseline dinh luong va anh minh hoa truoc khi toi uu."*
- **Vi sao khong lam OCR ngay?** -> *"Detection sai thi OCR sai day chuyen, nen phai lam chac detection truoc."*
- **Vi sao phai co val/test?** -> *"De do khach quan, tranh tu danh gia tren du lieu da hoc."*
- **Vi sao can error analysis?** -> *"Metric khong chi ra nguyen nhan sai; error analysis chi ra huong cai thien cu the."*
- **Ket qua Buoi 3 dung de lam gi?** -> *"Lam moc so sanh cho Buoi 4 va tai lieu cho bao cao/bao ve."*
- **Buoc tiep theo la gi?** -> *"So sanh cau hinh YOLO, roi noi pipeline OCR end-to-end."*
