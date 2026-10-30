# ROBOPILOT AI COGNITIVE CONSTITUTION & CODE QUALITY (GEMINI.md)

> **CHỈ THỊ BỘ NÃO BẮT BUỘC**: Mọi Model AI khởi động tại workspace BẮT BUỘC tuân thủ 100% các chuẩn mực sau:

## 1. NGUYÊN TẮC GIAI ĐOẠN (DESIGN PHASE INVARIANT)
- Dự án đang ở **DESIGN PHASE**: TUYỆT ĐỐI CẤM viết code sản phẩm, cấm tạo file triển khai ứng dụng, cấm cài dependencies.
- Được phép: Nghiên cứu toán học, viết tài liệu Markdown, vẽ sơ đồ Mermaid, thiết kế JSON Schema và viết Pseudocode.
- Chỉ chuyển sang DEVELOPMENT PHASE khi có lệnh phê duyệt chính thức từ Chủ dự án (Boss).

## 2. CHUẨN MỰC KỸ THUẬT & TRUNG THỰC KHOA HỌC (ZERO TOLERANCE)
- **Không fake số liệu**: Tuyệt đối cấm bịa đặt số liệu hội tụ hay kết quả RL. Đánh giá bắt buộc chạy qua ít nhất 3-5 random seeds (Mean ± Std).
- **Chống Reward Hacking**: Bắt buộc áp dụng Potential-based Reward Shaping ($PBRS$) $F(s,s') = \gamma \Phi(s') - \Phi(s)$ để triệt tiêu hiện tượng robot đi lùi - tiến kiếm điểm.
- **Không Hardcode**: Cấm hardcode tọa độ né vật cản trong logic di chuyển của robot. Robot phải di chuyển hoàn toàn dựa trên chính sách AI và cảm biến.
- **Ép kiểu dữ liệu nghiêm ngặt**:
  * Python: Type hints đầy đủ 100%, kiểm tra bằng `mypy --strict`, chuẩn PEP 8.
  * TypeScript: Bật `"strict": true`, cấm tuyệt đối kiểu `any` và `@ts-ignore`.

## 3. CHUẨN MỰC NGÔN NGỮ TIẾNG VIỆT CÓ DẤU
- 100% tin nhắn báo cáo, handoff, review và trao đổi giữa các Agent BẮT BUỘC dùng **Tiếng Việt có dấu** đầy đủ, chuẩn chính tả. Tuyệt đối cấm nhắn tiếng Việt không dấu.
