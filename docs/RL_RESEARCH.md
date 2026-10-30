# ROBOPILOT — REINFORCEMENT LEARNING RESEARCH SPECIFICATION
# NGHIÊN CỨU LÝ THUYẾT VÀ MÔ HÌNH TOÁN HỌC HỌC TĂNG CƯỜNG (RL) CHO XE TỰ HÀNH (AMR)

> **Cơ quan phụ trách:** Tab 2 (@tab_2) — Robotics & RL Research Specialist  
> **Thẩm định:** Tab 7 (@tab_7) — QA Auditor | **Phê duyệt:** Tab 1 (@tab_1) — Orchestrator  
> **Trạng thái:** DRAFT / PHASE 1 (Sprint 1) | **Ngày ban hành:** 2026-10-30  

---

## 1. MÔ HÌNH HÓA BÀI TOÁN DỰA TRÊN QUÁ TRÌNH QUYẾT ĐỊNH MARKOV (MDP)

Bài toán điều hướng của Robot vận chuyển tự hành (Autonomous Mobile Robot - AMR) trong nhà kho mô phỏng 2D được mô hình hóa toán học chặt chẽ dưới dạng một **Quá trình Quyết định Markov Hữu hạn (Finite Markov Decision Process - MDP)** biểu diễn bởi bộ 5 thành phần $(\mathcal{S}, \mathcal{A}, \mathcal{P}, \mathcal{R}, \gamma)$:

```
                     +----------------------------------------------+
                     |                 ENVIRONMENT                  |
                     |     WarehouseGridEnv (Gymnasium-based)       |
                     +----------------------------------------------+
                            ^                             |
                            | Action                      | Observation o_t in S
                            | a_t in A                    | Reward r_t in R
                            |                             | Done d_t in {0, 1}
                            |                             v
                     +----------------------------------------------+
                     |                    AGENT                     |
                     |        Policy pi(a|s) / Q_theta(s, a)        |
                     +----------------------------------------------+
```

### 1.1. Không gian trạng thái và quan sát ($\mathcal{S}$ & $\Omega$)
Trong môi trường thế giới ô lưới (Grid World) kích thước $W \times H$, robot hoạt động dưới 2 cơ chế quan sát:

1. **Quan sát Tuyệt đối (Coordinate Global Mode - dành cho Tabular Q-Learning):**
   $$s = [x_r, y_r, x_g, y_g] \in \mathcal{S}_{\text{global}}$$
   - Không gian trạng thái rời rạc hữu hạn: $|\mathcal{S}| = W \times H \times W \times H$.
   - Trên bản đồ $10 \times 10$, với vị trí đích cố định, $|\mathcal{S}| = 100$ trạng thái. Phù hợp hoàn hảo để biểu diễn dưới dạng ma trận giá trị $Q(s, a)$.

2. **Quan sát Tương đối Lân cận (Egocentric Proximity Raycast Mode - dành cho Deep Q-Network):**
   Để robot có khả năng thích nghi và điều hướng trên bản đồ chưa từng thấy (Zero-shot Generalization), không gian quan sát $o_t$ được biểu diễn dưới dạng vector 7 chiều chuẩn hóa trong đoạn $[0, 1]$ hoặc $[-1, 1]$:
   $$o_t = \left[ d_{\text{up}}, d_{\text{down}}, d_{\text{left}}, d_{\text{right}}, \Delta \hat{x}, \Delta \hat{y}, \hat{D}_{\text{Manhattan}} \right]^\top \in [-1, 1]^7$$
   - $d_{\text{dir}} \in [0, 1]$: Khoảng cách từ vị trí hiện tại của robot tới chướng ngại vật hoặc tường gần nhất theo 4 hướng cardinal, chia tỉ lệ chuẩn hóa theo tầm nhìn tối đa $L_{\text{sensor}}$:
     $$d_{\text{dir}} = \frac{\text{dist}(\text{pos}, \text{obstacle}_{\text{dir}})}{L_{\text{sensor}}}$$
   - $\Delta \hat{x} = \frac{x_g - x_r}{W-1} \in [-1, 1]$: Khoảng cách tương đối theo trục hoành đến đích.
   - $\Delta \hat{y} = \frac{y_g - y_r}{H-1} \in [-1, 1]$: Khoảng cách tương đối theo trục tung đến đích.
   - $\hat{D}_{\text{Manhattan}} = \frac{|x_g - x_r| + |y_g - y_r|}{W + H - 2} \in [0, 1]$: Khoảng cách Manhattan chuẩn hóa.

### 1.2. Không gian hành động ($\mathcal{A}$)
Không gian hành động là tập hợp rời rạc 4 hướng di chuyển:
$$\mathcal{A} = \{0, 1, 2, 3\}$$
- $a = 0$: `UP` (Di chuyển theo hướng giảm $y$: $y' = y - 1$)
- $a = 1$: `DOWN` (Di chuyển theo hướng tăng $y$: $y' = y + 1$)
- $a = 2$: `LEFT` (Di chuyển theo hướng giảm $x$: $x' = x - 1$)
- $a = 3$: `RIGHT` (Di chuyển theo hướng tăng $x$: $x' = x + 1$)

### 1.3. Xác suất chuyển trạng thái ($\mathcal{P}$)
Trong phiên bản V1 MVP, môi trường là tất định (Deterministic Environment):
$$\mathcal{P}(s' \mid s, a) = \begin{cases} 
1 & \text{nếu } s' = \text{Trans}(s, a) \\
0 & \text{ngược lại}
\end{cases}$$
Quy tắc chuyển vị trí $\text{Trans}(s, a)$:
- Nếu ô dự kiến $s_{\text{candidate}}$ là ô trống (Walkable): $s' = s_{\text{candidate}}$.
- Nếu ô dự kiến $s_{\text{candidate}}$ là tường biên hoặc kệ hàng (Obstacle): Robot giữ nguyên vị trí $s' = s$ và kích hoạt cờ va chạm (`is_collision = True`).

### 1.4. Hệ số chiết khấu phần thưởng ($\gamma$)
Hệ số chiết khấu tương lai $\gamma \in [0.95, 0.99]$. Với bài toán nhà kho có số bước trung bình $20 - 50$ bước, giá trị tối ưu được chọn là:
$$\gamma = 0.99$$
Đảm bảo giá trị kỳ vọng tích lũy không bị phân kỳ và ưu tiên tìm đường ngắn nhất.

---

## 2. PHƯƠNG TRÌNH BELLMAN & LÝ THUYẾT TỐI ƯU HÓA HỌC TĂNG CƯỜNG

Hàm giá trị hành động tối ưu $Q^*(s, a)$ thỏa mãn phương trình Bellman Optimality Equation:
$$Q^*(s, a) = \mathcal{R}(s, a) + \gamma \sum_{s' \in \mathcal{S}} \mathcal{P}(s' \mid s, a) \max_{a' \in \mathcal{A}} Q^*(s', a')$$

Với môi trường tất định:
$$Q^*(s, a) = r(s, a, s') + \gamma \max_{a' \in \mathcal{A}} Q^*(s', a')$$

### 2.1. Cập nhật Tabular Q-Learning
Trong không gian trạng thái nhỏ, bảng $Q(s, a)$ được cập nhật bằng phương pháp Temporal Difference (TD(0)):
$$Q_{t+1}(s_t, a_t) = Q_t(s_t, a_t) + \alpha \left[ r_{t+1} + \gamma \max_{a} Q_t(s_{t+1}, a) - Q_t(s_t, a_t) \right]$$
Trong đó:
- $\alpha \in (0, 1]$: Tốc độ học (Learning rate), khuyến nghị $\alpha = 0.1$.
- TD Error: $\delta_t = r_{t+1} + \gamma \max_{a} Q_t(s_{t+1}, a) - Q_t(s_t, a_t)$.

---

## 3. LÝ DO KHOA HỌC LỰA CHỌN DUELING DOUBLE DQN (D3QN) CHO ROBOPILOT

Khi chuyển sang mạng nơ-ron xấp xỉ hàm giá trị $Q_\theta(s, a)$, thuật toán DQN nguyên bản (Vanilla DQN, Mnih et al., 2015) bộc lộ 2 điểm yếu chí tử trong bài toán điều hướng robot:
1. **Thiên kiến ước lượng thổi phồng (Maximization Bias / Overestimation):** Do toán tử $\max_a Q(s', a)$ vừa dùng để chọn hành động vừa dùng để đánh giá giá trị.
2. **Khó phân biệt giá trị trạng thái và lợi thế hành động:** Trong nhiều tình huống nguy hiểm (như đứng sát ngõ cụt), mọi hành động đều có kết cục xấu; mạng thông thường phải học cập nhật từng hành động một rất chậm.

RoboPilot khắc phục triệt để bằng cách kết hợp **Double DQN (Van Hasselt et al., 2016)** và **Dueling Architecture (Wang et al., 2016)**:

```
                    +-----------------------------+
                    |   Input Observation o_t     |  (7-dim vector)
                    +-----------------------------+
                                   |
                    +-----------------------------+
                    |   Shared Feature Extractor  |  Linear(7, 128) -> ReLU -> Linear(128, 128) -> ReLU
                    +-----------------------------+
                                   |
                   +---------------+---------------+
                   |                               |
                   v                               v
        +---------------------+         +---------------------+
        |  Value Stream V(s)  |         | Advantage Stream    |
        |  Linear(128, 1)     |         | A(s, a)             |
        |  Scalar             |         | Linear(128, 4)      |
        +---------------------+         +---------------------+
                   |                               |
                   +---------------+---------------+
                                   v
        +-----------------------------------------------------+
        |            Aggregation Module (Identifiability)     |
        |  Q(s, a) = V(s) + (A(s, a) - 1/|A| * sum(A(s, a'))) |
        +-----------------------------------------------------+
```

### 3.1. Công thức tổng hợp Dueling
Để đảm bảo tính xác định duy nhất (Identifiability) của $V(s)$ và $A(s, a)$, ta trừ đi giá trị trung bình của Advantage:
$$Q(s, a; \theta, \alpha, \beta) = V(s; \theta, \beta) + \left( A(s, a; \theta, \alpha) - \frac{1}{|\mathcal{A}|} \sum_{a' \in \mathcal{A}} A(s, a'; \theta, \alpha) \right)$$
- $\theta$: Trọng số mạng trích xuất đặc trưng chung.
- $\beta$: Trọng số nhánh Value.
- $\alpha$: Trọng số nhánh Advantage.

### 3.2. Cập nhật Double DQN Target
Mục tiêu TD của Double DQN tách riêng mạng chính (chọn action) và mạng mục tiêu (đánh giá Q-value):
$$y_t^{\text{DoubleQ}} = r_{t+1} + \gamma Q\left(s_{t+1}, \arg\max_{a} Q(s_{t+1}, a; \theta_t); \theta_t^-\right)$$
- Mạng chính $\theta_t$: Chọn hành động tốt nhất $a^* = \arg\max_a Q(s_{t+1}, a; \theta_t)$.
- Mạng mục tiêu $\theta_t^-$: Đánh giá giá trị của hành động $a^*$ đó.
- Loại bỏ hoàn toàn overestimation bias, giúp đường cong học tập ổn định đơn điệu hơn.

---

## 4. CHIẾN LƯỢC TỔNG QUÁT HÓA MÔ HÌNH (ZERO-SHOT TRANSFER THEORY)

Tại sao mạng D3QN huấn luyện trên bản đồ $10 \times 10$ có thể giải quyết được bản đồ $15 \times 15$ hoặc $20 \times 20$ mà không cần học lại từ đầu?
- **Nguyên lý Độc lập Không gian Tuyệt đối:** Vector đầu vào $o_t$ không chứa tọa độ $x, y$ tuyệt đối. Nó chỉ chứa thông tin cục bộ (cảm biến vật cản quanh thân) và vector phương hướng tương đối $(\Delta \hat{x}, \Delta \hat{y})$.
- **Chính sách Phản xạ Trực giác (Reactive Policy):**
  $$\pi(a \mid o) = \arg\max_a Q(o, a)$$
  Robot học được hàm ánh xạ: *"Nếu hướng đích ở bên phải ($\Delta \hat{x} > 0$) và cảm biến bên phải không có vật cản ($d_{\text{right}} > 0.5$), thì hành động tối ưu là RIGHT"*. Quy luật này đúng trên mọi kích thước bản đồ!

---

## 5. KẾT LUẬN & HƯỚNG BÀN GIAO TIẾP THEO

- Toàn bộ cơ sở lý thuyết toán học MDP và D3QN trên đây là căn cứ chuẩn mực để **Tab 4 (@tab_4)** thiết kế mạng nơ-ron PyTorch tại `docs/TRAINING_PIPELINE.md`.
- Vấn đề cốt lõi tiếp theo là thiết kế hàm thưởng $\mathcal{R}$ chống lại Reward Hacking, được trình bày chi tiết trong tài liệu liên kết [docs/REWARD_DESIGN.md](REWARD_DESIGN.md).
