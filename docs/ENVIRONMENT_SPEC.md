# ROBOPILOT — GYMNASIUM ENVIRONMENT SPECIFICATION
# ĐẶC TẢ KỸ THUẬT MÔI TRƯỜNG MÔ PHỎNG WAREHOUSEGRIDENV (GYMNASIUM API)

> **Cơ quan phụ trách:** Tab 3 (@tab_3) — Simulation & Environment Designer  
> **Thẩm định:** Tab 7 (@tab_7) — QA Auditor | **Phê duyệt:** Tab 1 (@tab_1) — Orchestrator  
> **Trạng thái:** DRAFT / PHASE 1 (Sprint 1) | **Ngày ban hành:** 2026-10-30  

---

## 1. TỔNG QUAN VÀ CHUẨN MỰC TƯƠNG THÍCH (GYMNASIUM COMPLIANCE)

Lớp môi trường chính `WarehouseGridEnv` kế thừa trực tiếp từ `gymnasium.Env` của Farama Foundation. Môi trường bắt buộc vượt qua bài kiểm tra tự động `gymnasium.utils.env_checker.check_env(env)` mà không có bất kỳ warning hay exception nào.

```python
import gymnasium as gym
from gymnasium import spaces
import numpy as np

class WarehouseGridEnv(gym.Env):
    metadata = {
        "render_modes": ["ansi", "rgb_array"],
        "render_fps": 30
    }
```

---

## 2. HỆ TỌA ĐỘ VÀ PHÂN LOẠI Ô LƯỚI (COORDINATE SYSTEM & TILES)

### 2.1. Quy ước Hệ tọa độ
- **Gốc tọa độ $[0, 0]$:** Đặt tại góc trên bên trái (Top-Left corner) của bản đồ.
- **Trục hoành ($x$):** Điểm cột tăng dần từ trái sang phải ($0 \le x \le W - 1$).
- **Trục tung ($y$):** Hàng tăng dần từ trên xuống dưới ($0 \le y \le H - 1$).
- Tọa độ robot luôn được biểu diễn dưới dạng cặp số nguyên: `(x, y)`.

```
      x = 0       x = 1       ...       x = W-1
y=0  [ (0,0) ]   [ (1,0) ]   ...       [ (W-1, 0) ]
y=1  [ (0,1) ]   [ (1,1) ]   ...       [ (W-1, 1) ]
...     ...         ...      ...           ...
y=H-1[ (0,H-1) ] [ (1,H-1) ] ...       [ (W-1, H-1) ]
```

### 2.2. Bảng Mã hóa Ô Lưới (Grid Tile IDs)

| Mã số (ID) | Tên ký hiệu | Ý nghĩa thực tế | Khả năng đi qua | Màu quy ước UI |
| :---: | :--- | :--- | :---: | :---: |
| **0** | `EMPTY` | Lối đi trống trong nhà kho | **Có** | Trắng / Xám nhạt (`#F3F4F6`) |
| **1** | `OBSTACLE` | Kệ hàng tĩnh / Tường ngăn cách | **Không** | Xám đậm / Đen (`#1F2937`) |
| **2** | `START` | Vị trí xuất phát của xe AMR | **Có** | Xanh dương (`#3B82F6`) |
| **3** | `GOAL` | Trạm bốc dỡ hàng hóa (Delivery Bay) | **Có** | Xanh lá (`#10B981`) |
| **4** | `CHARGER` | Trạm sạc pin tự động (Docking Station)| **Có** | Vàng kim (`#F59E0B`) |

---

## 3. ĐẶC TẢ CÁC HÀM CỐT LÕI (CORE API METHODS)

### 3.1. Phương thức `reset(seed=None, options=None) -> tuple[np.ndarray, dict]`
Khởi tạo lại trạng thái môi trường cho episode mới.

- **Tham số:**
  * `seed` (Optional[int]): Hạt giống ngẫu nhiên phục vụ tính tái lập (Reproducibility).
  * `options` (Optional[dict]): Các tùy chọn bổ sung (ví dụ thay đổi vị trí Start/Goal ngẫu nhiên hoặc nạp map tùy biến).
- **Giá trị trả về:**
  * `observation` (np.ndarray): Vector trạng thái ban đầu của robot (shape tùy theo chế độ quan sát, dtype `np.float32`).
  * `info` (dict): Siêu dữ liệu ban đầu.

### 3.2. Phương thức `step(action: int) -> tuple[np.ndarray, float, bool, bool, dict]`
Thực thi một bước di chuyển của robot trong môi trường.

- **Tham số:**
  * `action` (int): Số nguyên $\in \{0, 1, 2, 3\}$.
- **Logic thực thi:**
  1. Tính toán tọa độ dự kiến: $s_{\text{candidate}} = \text{pos} + \Delta_{\text{action}}$.
  2. Kiểm tra va chạm biên ($x < 0$ hoặc $x \ge W$ hoặc $y < 0$ hoặc $y \ge H$).
  3. Kiểm tra va chạm kệ hàng ($\text{Grid}[y_{\text{candidate}}][x_{\text{candidate}}] == 1$).
  4. Nếu va chạm: Giữ nguyên vị trí $\text{pos}_{t+1} = \text{pos}_t$, kích hoạt `is_collision = True`.
  5. Nếu không va chạm: Cập nhật vị trí $\text{pos}_{t+1} = s_{\text{candidate}}$.
  6. Tiêu hao năng lượng pin: $\text{battery} = \max(0.0, \text{battery} - 0.5\%)$. Nếu đến trạm `CHARGER`, nạp đầy $\text{battery} = 100.0\%$.
  7. Tính toán phần thưởng $r_t$ theo công thức PBRS từ `REWARD_DESIGN.md`.
  8. Kiểm tra điều kiện kết thúc (`terminated`, `truncated`).
- **Giá trị trả về:**
  * `observation` (np.ndarray): Trạng thái mới $o_{t+1}$.
  * `reward` (float): Phần thưởng tức thời $r_t$.
  * `terminated` (bool): `True` khi robot đến ô `GOAL` hoặc pin cạn $0\%$.
  * `truncated` (bool): `True` khi `step_count >= max_steps`.
  * `info` (dict): Chứa telemetry chi tiết của bước đi.

### 3.3. Cấu trúc trường `info` Dictionary
```json
{
  "step_count": 14,
  "robot_pos": [4, 6],
  "goal_pos": [9, 9],
  "last_action": 1,
  "action_name": "DOWN",
  "is_collision": false,
  "is_goal": false,
  "battery_level": 93.0,
  "distance_to_goal": 8,
  "raw_reward": -0.5,
  "shaping_reward": 0.08,
  "total_reward": -0.42
}
```

---

## 4. GIỚI HẠN THỜI GIAN VÀ BẢO ĐẢM TÍNH KẾT THÚC (TRUNCATION INVARIANT)

Để tránh hiện tượng robot bị kẹt hoặc lặp vô tận, giới hạn bước tối đa mỗi episode ($\text{MaxSteps}$) được quy định theo kích thước bản đồ:
$$\text{MaxSteps} = \text{round}\left( 2.5 \times (W + H) \right)$$
- Bản đồ $10 \times 10$: $\text{MaxSteps} = 2.5 \times (10 + 10) = 50$ bước.
- Bản đồ $15 \times 15$: $\text{MaxSteps} = 2.5 \times (15 + 15) = 75$ bước.
- Bản đồ $20 \times 20$: $\text{MaxSteps} = 2.5 \times (20 + 20) = 100$ bước.

Khi bước đi thứ $\text{MaxSteps}$ được thực hiện mà chưa về đích:
- `truncated = True`, `terminated = False`.
- Nhận hình phạt timeout: $R_{\text{timeout}} = -20.0$.
