# ROBOPILOT — ROBOT SPECIFICATION
# ĐẶC TẢ KỸ THUẬT XE TỰ HÀNH (AMR - AUTONOMOUS MOBILE ROBOT)

> **Cơ quan phụ trách:** Tab 3 (@tab_3) — Simulation & Environment Designer  
> **Thẩm định:** Tab 7 (@tab_7) — QA Auditor | **Phê duyệt:** Tab 1 (@tab_1) — Orchestrator  
> **Trạng thái:** DRAFT / PHASE 1 (Sprint 1) | **Ngày ban hành:** 2026-10-30  

---

## 1. HÌNH THỂ VÀ THÔNG SỐ VẬT LÝ TRONG MÔI TRƯỜNG LƯỚI 2D

Trong phiên bản V1 MVP, xe tự hành (AMR) được mô phỏng dưới dạng thực thể hình học chiếm dụng đúng $1 \times 1$ ô lưới tiêu chuẩn:

| Thuộc tính | Kiểu dữ liệu | Phạm vi giá trị | Mô tả chi tiết |
| :--- | :---: | :---: | :--- |
| **Tọa độ vị trí (`pos`)** | `tuple[int, int]` | $(x, y) \in [0, W-1] \times [0, H-1]$ | Tọa độ ô hiện tại robot đang chiếm giữ. |
| **Hướng quay (`heading`)** | `str` | `["UP", "DOWN", "LEFT", "RIGHT"]` | Hướng mũi xe nhìn tới, dùng để render icon trực quan trên Canvas 2D. |
| **Góc định hướng (`angle`)**| `int` | $\{0^\circ, 90^\circ, 180^\circ, 270^\circ\}$ | Góc quay hình học phục vụ animation mượt mà trên Canvas. |
| **Tốc độ bước đi** | `float` | $1.0$ ô / tick | Di chuyển tịnh tiến đúng 1 ô mỗi bước hợp lệ. |
| **Bán kính bao an toàn** | `float` | $r = 0.5$ cell unit | Không thể đi xuyên qua 2 vật cản nằm chéo nhau nếu không có lối mở. |

---

## 2. HỆ THỐNG CẢM BIẾN ẢO (VIRTUAL SENSORS PROFILE)

Robot được trang bị 2 cụm cảm biến ảo để cung cấp thông tin cho bộ não AI:

```
                         [ Ray 0: UP ]
                               ^
                               |
       [ Ray 2: LEFT ] <--- [ 🤖 ] ---> [ Ray 3: RIGHT ]
                               |
                               v
                        [ Ray 1: DOWN ]
```

### 2.1. Cụm Cảm biến Khoảng cách 4 Hướng (Proximity Raycast Sensor)
- Phát ra 4 tia quét ảo dọc theo các hướng chính: Trên, Dưới, Trái, Phải.
- Tầm quét tối đa ($L_{\text{sensor}}$): $5$ ô lưới (hoặc $\max(W, H)$ tùy cấu hình).
- Giá trị đo đạc: Số lượng ô trống trước khi chạm vào tường biên hoặc kệ hàng:
  $$d_{\text{raw}} \in \{0, 1, 2, 3, 4, 5\}$$
- Chuẩn hóa đầu vào mạng nơ-ron:
  $$d_{\text{norm}} = \frac{d_{\text{raw}}}{L_{\text{sensor}}} \in [0.0, 1.0]$$
  * $d_{\text{norm}} = 0.0$: Đang đứng sát chướng ngại vật (cực kỳ nguy hiểm).
  * $d_{\text{norm}} = 1.0$: Hành lang thông thoáng ít nhất 5 ô.

### 2.2. Cảm biến Định vị Mục tiêu (Target Beacon Sensor)
- Đo đạc độ lệch tương đối giữa robot và trạm đích:
  $$\Delta x = x_g - x_r, \quad \Delta y = y_g - y_r$$
- Khoảng cách Manhattan: $D_{\text{Manhattan}} = |\Delta x| + |\Delta y|$.
- Khoảng cách Euclidean: $D_{\text{Euclid}} = \sqrt{\Delta x^2 + \Delta y^2}$.

---

## 3. MÔ HÌNH QUẢN LÝ NĂNG LƯỢNG (BATTERY & POWER LIFECYCLE)

Để mô phỏng chính xác các điều kiện công nghiệp thực tế, robot được tích hợp hệ thống quản lý năng lượng:

```
[ PIN: 100% ] ──(Mỗi bước đi: -0.5%)──> [ PIN < 20%: CẢNH BÁO ] ──> [ SẠC ĐẦY TẠI DOCK ]
      │                                             │
      └──(Va chạm kệ hàng: -1.0%)───────────────────┘
```

1. **Dung lượng tối đa:** $100.0\%$. Khởi đầu episode luôn ở mức $100.0\%$.
2. **Mức tiêu hao bình thường:** $-0.5\%$ cho mỗi bước di chuyển thành công.
3. **Mức tiêu hao va chạm:** Khi đâm vào tường/kệ hàng, chịu sốc năng lượng: trừ thêm $-1.0\%$.
4. **Ngưỡng pin nguy cấp (Critical Threshold):** Khi pin $< 20.0\%$, robot rơi vào trạng thái báo động vàng (`is_low_battery = True`).
5. **Cơ chế nạp điện tại Trạm sạc (`CHARGER` Dock):**
   * Khi robot bước vào ô có mã `CHARGER` (ID: 4), pin lập tức được nạp đầy $100.0\%$ và nhận điểm thưởng phục hồi $+5.0$.
   * Nếu pin chạm mốc $0.0\%$ trước khi về đích hoặc vào trạm sạc: Robot bị "chết máy giữa đường", nhận hình phạt $-50.0$ và episode lập tức dừng (`terminated = True`).

---

## 4. BẢNG TRẠNG THÁI TELEMETRY CỦA ROBOT (ROBOT STATE DTO)

Cấu trúc đối tượng trạng thái robot xuất ra mỗi tick phục vụ Canvas 2D render:

```json
{
  "robot_id": "AMR_01",
  "coordinates": {
    "x": 4,
    "y": 7,
    "heading": "UP",
    "angle_deg": 0
  },
  "sensor_readings": {
    "ray_up": 3,
    "ray_down": 0,
    "ray_left": 1,
    "ray_right": 4,
    "norm_vector": [0.6, 0.0, 0.2, 0.8]
  },
  "battery": {
    "percentage": 87.5,
    "is_critical": false,
    "is_charging": false
  },
  "status": "NAVIGATING" // "NAVIGATING" | "COLLIDED" | "CHARGING" | "GOAL_REACHED" | "DEPLETED"
}
```
