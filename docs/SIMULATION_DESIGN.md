# ROBOPILOT — SIMULATION & COLLISION DESIGN
# THIẾT KẾ CƠ CHẾ MÔ PHỎNG, PHÁT HIỆN VA CHẠM VÀ KIỂM ĐỊNH BẢN ĐỒ

> **Cơ quan phụ trách:** Tab 3 (@tab_3) — Simulation & Environment Designer  
> **Thẩm định:** Tab 7 (@tab_7) — QA Auditor | **Phê duyệt:** Tab 1 (@tab_1) — Orchestrator  
> **Trạng thái:** DRAFT / PHASE 1 (Sprint 1) | **Ngày ban hành:** 2026-10-30  

---

## 1. THUẬT TOÁN PHÁT HIỆN VA CHẠM BẤT BIẾN $O(1)$ (COLLISION INVARIANTS)

Để đảm bảo hiệu năng tối đa khi huấn luyện RL (hàng triệu bước di chuyển mỗi phút) và độ mượt 60 FPS trên giao diện, cơ chế kiểm tra va chạm được thiết kế dưới dạng tra cứu ma trận trực tiếp với độ phức tạp thời gian **$O(1)$**:

```
[ Vị trí hiện tại: (x, y) ] ──(Hành động a)──> [ Tọa độ dự kiến: (x_new, y_new) ]
                                                      │
                       ┌──────────────────────────────┴──────────────────────────────┐
                       ▼                                                             ▼
         [ KIỂM TRA BIÊN (BOUNDARY) ]                                  [ KIỂM TRA VẬT CẢN (MATRIX) ]
         x_new < 0 OR x_new >= W                                       grid_matrix[y_new][x_new] == 1
         y_new < 0 OR y_new >= H                                                     │
                       │                                                             │
                       └──────────────────────────────┬──────────────────────────────┘
                                                      │ (Thỏa mãn 1 trong 2 điều kiện)
                                                      v
                                        [ PHÁT HIỆN VA CHẠM (COLLISION) ]
                                        • Tọa độ giữ nguyên: (x, y)
                                        • is_collision = True
                                        • Phạt va chạm: -10.0
                                        • Pin tiêu hao thêm: -1.0%
```

### 1.1. Mã giả Thuật toán Bước đi An toàn (Safe Step Function)
```python
def step_safe(current_pos: tuple[int, int], action: int, grid: np.ndarray) -> tuple[tuple[int, int], bool]:
    # 1. Bảng dịch chuyển hướng
    deltas = {
        0: (0, -1), # UP
        1: (0, 1),  # DOWN
        2: (-1, 0), # LEFT
        3: (1, 0)   # RIGHT
    }
    dx, dy = deltas[action]
    target_x = current_pos[0] + dx
    target_y = current_pos[1] + dy
    H, W = grid.shape

    # 2. Kiểm tra biên bản đồ O(1)
    if target_x < 0 or target_x >= W or target_y < 0 or target_y >= H:
        return current_pos, True # Va chạm tường biên

    # 3. Kiểm tra chướng ngại vật O(1)
    if grid[target_y, target_x] == 1:
        return current_pos, True # Va chạm kệ hàng

    # 4. Di chuyển hợp lệ
    return (target_x, target_y), False
```

---

## 2. THUẬT TOÁN KIỂM ĐỊNH TÍNH GIẢI ĐƯỢC CỦA BẢN ĐỒ (SOLVABILITY VERIFICATION)

Một trong những nguyên nhân khiến mô hình RL học thất bại là bản đồ bị lỗi (không có đường đi từ Start đến Goal). 

RoboPilot bắt buộc chạy thuật toán **Tìm kiếm theo chiều rộng (Breadth-First Search - BFS)** để kiểm định mọi bản đồ (kể cả bản đồ do người dùng tự vẽ) trước khi cho phép huấn luyện hoặc mô phỏng:

```
[ START NODE ] ──(Queue FIFO)──> [ Lan truyền Loang (Flood-Fill) ] ──> [ Chạm GOAL ? ]
                                                                             │
                                           ┌─────────────────────────────────┴─────────────────────────────────┐
                                           ▼                                                                   ▼
                                  [ CÓ ĐƯỜNG ĐI (VALID) ]                                           [ BẾ TẮC (INVALID MAP) ]
                                  • Trả về khoảng cách tối thiểu                                    • Từ chối nạp bản đồ
                                  • Chấp thuận nạp vào Simulation                                   • Báo lỗi cho người dùng
```

### 2.1. Độ phức tạp và Tính đúng đắn
- **Độ phức tạp thời gian:** $O(W \times H)$. Với bản đồ tối đa $30 \times 30 = 900$ ô, thời gian chạy BFS $< 0.5\text{ ms}$.
- **Tính tối ưu:** BFS trên đồ thị không trọng số đảm bảo tìm ra số bước ngắn nhất tuyệt đối $L_{\min}$ từ Start đến Goal.

---

## 3. CƠ CHẾ THẢ VẬT CẢN THỜI GIAN THỰC (DYNAMIC OBSTACLE INJECTION)

Trên giao diện Frontend React Canvas 2D, khi người dùng click chuột vào ô $(x_{\text{click}}, y_{\text{click}})$ để thử thách phản xạ của robot:

1. **Điều kiện an toàn bắt buộc:**
   - $(x_{\text{click}}, y_{\text{click}}) \ne \text{robot\_pos}$ (Không được thả đè lên xe robot).
   - $(x_{\text{click}}, y_{\text{click}}) \ne \text{goal\_pos}$ (Không được thả đè lên trạm bốc hàng).
2. **Cập nhật ma trận tĩnh tức thì:**
   $$\text{Grid}[y_{\text{click}}][x_{\text{click}}] = 1$$
3. **Phản xạ của bộ não AI:**
   - Tại tick tiếp theo, cảm biến lân cận (`ray_up`, `ray_down`, `ray_left`, `ray_right`) lập tức phát hiện vật cản mới xuất hiện cách robot $k$ ô.
   - Vector quan sát $o_t$ đổi giá trị $\to$ Mạng D3QN forward-pass $\to$ Chọn ngay nhánh rẽ an toàn khác trong vòng $1.2\text{ ms}$ mà không cần re-plan toàn bộ bản đồ!
