# ROBOPILOT — STATE & ACTION SPACE SPECIFICATION
# ĐẶC TẢ HỢP ĐỒNG KHÔNG GIAN TRẠNG THÁI (OBSERVATION) VÀ HÀNH ĐỘNG (ACTION)

> **Cơ quan phụ trách:** Tab 3 (@tab_3) — Simulation & Environment Designer  
> **Thẩm định:** Tab 7 (@tab_7) — QA Auditor | **Phê duyệt:** Tab 1 (@tab_1) — Orchestrator  
> **Trạng thái:** DRAFT / PHASE 1 (Sprint 1) | **Ngày ban hành:** 2026-10-30  

---

## 1. ĐẶC TẢ KHÔNG GIAN HÀNH ĐỘNG (ACTION SPACE CONTRACT)

Hợp đồng không gian hành động được chuẩn hóa tuyệt đối giữa Môi trường Gymnasium, Thuật toán AI, Backend và Frontend:

```python
self.action_space = spaces.Discrete(4)
```

### Bảng Ánh xạ Hành động (Action Mapping Table)

| Mã Action | Ký hiệu Chuẩn | Tên hành động | Biến thiên tọa độ $(\Delta x, \Delta y)$ | Hướng nhìn mới (`heading`) |
| :---: | :---: | :--- | :---: | :---: |
| **0** | `UP` | Di chuyển lên phía trên (Bắc) | $(0, -1)$ | `UP` |
| **1** | `DOWN` | Di chuyển xuống phía dưới (Nam) | $(0, +1)$ | `DOWN` |
| **2** | `LEFT` | Di chuyển sang bên trái (Tây) | $(-1, 0)$ | `LEFT` |
| **3** | `RIGHT` | Di chuyển sang bên phải (Đông) | $(+1, 0)$ | `RIGHT` |

- **Ràng buộc di chuyển:** Mỗi action di chuyển chính xác 1 ô lưới.
- **Không có hành động rỗng (No No-Op):** Robot bắt buộc phải chọn 1 trong 4 hướng di chuyển ở mỗi tick mô phỏng.

---

## 2. ĐẶC TẢ KHÔNG GIAN QUAN SÁT (OBSERVATION SPACE CONTRACTS)

Môi trường hỗ trợ 2 chế độ quan sát chuyên biệt cho từng họ thuật toán:

### 2.1. Chế độ A: Quan sát Tọa độ (Coordinate Mode — Cho Tabular Q-Learning)
Phục vụ bảng tra cứu giá trị $Q(s, a)$ với không gian trạng thái rời rạc cố định.

- **Dạng không gian Gymnasium:**
  ```python
  # Vector [robot_x, robot_y, goal_x, goal_y]
  self.observation_space = spaces.Box(
      low=np.array([0, 0, 0, 0], dtype=np.int32),
      high=np.array([W - 1, H - 1, W - 1, H - 1], dtype=np.int32),
      dtype=np.int32
  )
  ```
- **Chỉ số trạng thái phẳng (Flat State Index cho Q-Table):**
  $$s_{\text{index}} = y_r \times W + x_r \in [0, W \times H - 1]$$
  *(Với vị trí đích cố định trên bản đồ)*.

---

### 2.2. Chế độ B: Cảm biến Tương đối Lân cận (Egocentric Sensor Mode — Cho PyTorch D3QN)
**Đây là chế độ quan sát chuẩn mặc định của RoboPilot V1**, bảo đảm khả năng suy luận và chuyển giao sang bản đồ lạ (Zero-shot Generalization).

- **Dạng không gian Gymnasium:**
  ```python
  self.observation_space = spaces.Box(
      low=-1.0,
      high=1.0,
      shape=(7,),
      dtype=np.float32
  )
  ```

### Bảng Chi tiết 7 Phần tử của Vector Quan sát $o_t \in \mathbb{R}^7$:

| Vị trí Index | Tên trường | Miền giá trị | Công thức toán học tính toán | Ý nghĩa điều hướng |
| :---: | :--- | :---: | :--- | :--- |
| **0** | `ray_up` | $[0.0, 1.0]$ | $\min(d_{\text{up}}, L_{\text{sensor}}) / L_{\text{sensor}}$ | Khoảng cách an toàn phía trên. |
| **1** | `ray_down` | $[0.0, 1.0]$ | $\min(d_{\text{down}}, L_{\text{sensor}}) / L_{\text{sensor}}$ | Khoảng cách an toàn phía dưới. |
| **2** | `ray_left` | $[0.0, 1.0]$ | $\min(d_{\text{left}}, L_{\text{sensor}}) / L_{\text{sensor}}$ | Khoảng cách an toàn bên trái. |
| **3** | `ray_right` | $[0.0, 1.0]$ | $\min(d_{\text{right}}, L_{\text{sensor}}) / L_{\text{sensor}}$ | Khoảng cách an toàn bên phải. |
| **4** | `delta_x` | $[-1.0, 1.0]$ | $(x_g - x_r) / (W - 1)$ | Độ lệch ngang tới trạm đích ($>0$: Đích ở bên phải; $<0$: Đích ở bên trái). |
| **5** | `delta_y` | $[-1.0, 1.0]$ | $(y_g - y_r) / (H - 1)$ | Độ lệch dọc tới trạm đích ($>0$: Đích ở bên dưới; $<0$: Đích ở bên trên). |
| **6** | `dist_norm`| $[0.0, 1.0]$ | $(|x_g - x_r| + |y_g - y_r|) / (W + H - 2)$ | Khoảng cách Manhattan chuẩn hóa tới đích. |

---

## 3. TÍNH NHẤT QUÁN TOÀN HỆ THỐNG (CROSS-MODULE CONSISTENCY)

Để tránh bất kỳ lỗi mismatch nào giữa các Tab:
1. **Tab 4 (`Training Architect`):** Khởi tạo mạng `DQN_MLP` với lớp đầu vào bắt buộc:
   ```python
   self.fc_input = nn.Linear(in_features=7, out_features=128)
   self.fc_output = nn.Linear(in_features=128, out_features=4)
   ```
2. **Tab 5 (`Backend MLOps`):** Trước khi nạp weights vào RAM, Dynamic Model Loader bắt buộc kiểm tra trường:
   ```json
   "environment": {
     "observation_dim": 7,
     "action_dim": 4
   }
   ```
   Nếu tệp weights nạp vào không khớp số chiều này $\to$ Báo lỗi `400 Bad Request` và từ chối nạp, ngăn ngừa sập tiến trình web server.
