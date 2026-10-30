# ROBOPILOT — PROJECT SCOPE & SPECIFICATION
# PHẠM VI VÀ ĐẶC TẢ KỸ THUẬT PHIÊN BẢN V1 (MVP)

---

## 1. MỤC TIÊU PHIÊN BẢN V1 (SMART NAVIGATION MVP)

RoboPilot V1 là phiên bản sản phẩm khả dụng tối thiểu (MVP - Minimum Viable Product). Mục tiêu tối thượng của V1 là **chứng minh tính khả thi hoàn chỉnh của chu trình khép kín: Huấn luyện AI điều hướng -> Đóng gói Model Artifact -> Nạp vào Backend -> Trực quan hóa & Tương tác trên Web Dashboard bằng Docker.**

---

## 2. DANH MỤC TRONG PHẠM VI (IN-SCOPE FOR V1)

### 2.1. Môi trường mô phỏng (Environment - 2D Grid World)
- **Cấu trúc không gian:** Lưới ô vuông 2 chiều rời rạc (Discrete 2D Grid). Kích thước hỗ trợ:
  - Bản đồ chuẩn: $10 \times 10$ (Easy - dành cho Q-Learning & DQN kiểm thử nhanh).
  - Bản đồ trung bình: $15 \times 15$ (Medium - nhà kho có nhiều dãy kệ).
  - Bản đồ nâng cao: $20 \times 20$ (Hard - nhiều chướng ngại vật phức tạp).
- **Phân loại ô trên lưới:**
  - Ô trống (Empty / Walkable path).
  - Ô vật cản / kệ hàng (Obstacle / Shelf - không thể đi xuyên qua).
  - Ô xuất phát (Start position).
  - Ô đích đến (Goal position / Delivery station).
- **Quy tắc di chuyển:**
  - 4 hướng rời rạc (Discrete 4 Actions): `0: UP`, `1: DOWN`, `2: LEFT`, `3: RIGHT`.
  - Bước di chuyển cố định: 1 ô / bước.
  - Xử lý va chạm biên hoặc va chạm vật cản: Robot giữ nguyên vị trí, nhận hình phạt va chạm (collision penalty), episode có thể bị kết thúc sớm hoặc tiếp tục tùy cấu hình môi trường.
  - Số bước tối đa mỗi episode (Max Steps per Episode): Tránh lặp vô hạn (ví dụ $2 \times (W + H)$ hoặc tối đa 100-200 bước).

### 2.2. Không gian quan sát (Observation Space)
V1 sẽ hỗ trợ và chuẩn hóa 2 chế độ quan sát:
1. **Chế độ Tọa độ (Coordinate / Relative Vector):**
   - Vector gồm: `[robot_x, robot_y, goal_x, goal_y, dx, dy]` (chuẩn hóa về $[0, 1]$ hoặc $[-1, 1]$).
   - Thích hợp cho Tabular Q-Learning và DQN trên bản đồ cố định.
2. **Chế độ Cảm biến Lân cận (Proximity / Local Radar - Recommended for Generalization):**
   - Khoảng cách đến chướng ngại vật gần nhất ở 4 hướng hoặc 8 hướng (Raycast mô phỏng khoảng cách ô rời rạc).
   - Vector hướng tới đích: $[\Delta x, \Delta y]$ và khoảng cách Euclidean / Manhattan.
   - Cho phép mô hình DQN có khả năng suy luận trên các bản đồ chưa từng thấy trong quá trình train (Zero-shot map transfer).

### 2.3. Thiết kế hàm thưởng (Reward Shaping)
- Đến đích an toàn: $+100.0$ (kèm cờ `terminated = True`).
- Va chạm vật cản / tường: $-10.0$ hoặc $-50.0$ (phạt mạnh hành vi mất an toàn).
- Chi phí mỗi bước di chuyển (Step Penalty): $-0.5$ đến $-1.0$ (tạo áp lực thời gian, buộc robot chọn đường ngắn nhất).
- Phần thưởng hướng đích (Potential-based Reward Shaping):
  $$F(s, s') = \gamma \Phi(s') - \Phi(s)$$
  với $\Phi(s) = - \text{Distance}(s_{\text{robot}}, s_{\text{goal}})$. 
  *(Cơ chế này được chứng minh toán học là không gây ra hiện tượng Reward Hacking/Cycling).*

### 2.4. Thuật toán AI/ML
1. **Baseline 1 — Random Policy:** Lấy mẫu hành động ngẫu nhiên, đóng vai trò mốc kiểm chứng sàn (Floor baseline).
2. **Baseline 2 — A\* Search:** 
   - Thuật toán tìm kiếm theo đồ thị kinh điển với hàm Heuristic Manhattan Distance: $h(n) = |x_n - x_g| + |y_n - y_g|$.
   - Cung cấp đường đi tối ưu lý thuyết (Optimal Path Length) để đo tỷ lệ tối ưu của RL.
3. **RL Model 1 — Tabular Q-Learning:**
   - Cập nhật bảng $Q(s, a)$ theo phương trình Bellman:
     $$Q(s, a) \leftarrow Q(s, a) + \alpha [r + \gamma \max_{a'} Q(s', a') - Q(s, a)]$$
   - Sử dụng $\epsilon$-greedy exploration schedule decay.
4. **RL Model 2 — Deep Q-Network (DQN) bằng PyTorch:**
   - Multi-Layer Perceptron (MLP) gồm 2-3 hidden layers (ví dụ 64 hoặc 128 units, activation ReLU).
   - Các kỹ thuật chuẩn ổn định DQN:
     - Experience Replay Buffer (Dung lượng 10,000 - 50,000 transitions).
     - Target Network với chu kỳ cập nhật định kỳ (Hard update mỗi $C$ steps hoặc Soft Polyak update $\tau=0.005$).
     - Loss: Smooth L1 Loss (Huber Loss) hoặc MSE Loss.
     - Optimizer: Adam ($\text{lr} = 10^{-3}$ đến $10^{-4}$).

### 2.5. Hệ thống phần mềm & Giao diện (Fullstack)
- **Backend (FastAPI):**
  - Chạy mô phỏng cục bộ để phục vụ trực quan hóa.
  - Endpoint REST API: Quản lý bản đồ, cấu hình, nạp model, xuất kết quả benchmark.
  - WebSocket API: Truyền phát luồng trạng thái mô phỏng (Step ticks: tọa độ robot, $Q$-values, actions, rewards) theo thời gian thực tới Frontend.
- **Frontend (React 18 + Vite + TypeScript):**
  - Simulation Arena: Render Canvas 2D mượt mà (60 FPS), hiển thị bản đồ, robot, chướng ngại vật, trail đường đi.
  - Agent Control: Các nút Play/Pause/Reset, thanh trượt tốc độ mô phỏng, dropdown chọn thuật toán/model.
  - Analytics & Visualizer: Biểu đồ đường cong học tập, tỷ lệ thành công, so sánh thời gian và bước đi giữa A* và RL.
- **Database (PostgreSQL 15):**
  - Lưu trữ: Bản đồ (Maps), Thí nghiệm (Experiments), Phiên bản mô hình (Model Checkpoints metadata), Kết quả đối chuẩn (Benchmark Runs).
- **Deployment & Packaging (Docker):**
  - Docker Compose tích hợp 3 services: `backend`, `frontend`, `db` (PostgreSQL).
  - Volume mount thư mục `/models` để nạp tệp trọng số từ bên ngoài vào Backend container mà không cần rebuild image.

---

## 3. DANH MỤC NGOÀI PHẠM VI (OUT-OF-SCOPE FOR V1)

Các tính năng sau đây **tuyệt đối không triển khai trong V1**, được hoãn lại cho các phiên bản tiếp theo:

| Hạng mục hoãn lại | Lý do loại trừ khỏi V1 | Phiên bản dự kiến |
| :--- | :--- | :--- |
| **Chuyển động liên tục (Continuous Action & State)** | Làm tăng độ phức tạp mô phỏng vật lý, đòi hỏi thuật toán Actor-Critic (PPO, SAC). | V2 (Autonomous Navigation) |
| **Mô hình vi sai bánh xe (Differential Drive Robot)** | Cần tính toán động học robot (Kinematics: vận tốc tuyến tính $v$, vận tốc góc $\omega$). | V2 |
| **Chướng ngại vật động (Dynamic Moving Obstacles)** | Môi trường non-stationary làm tăng độ khó hội tụ của DQN cơ bản. | V2 |
| **Mô phỏng 3D vật lý (MuJoCo, Isaac Gym, PyBullet)** | Đòi hỏi GPU nặng, phức tạp trong tích hợp Web, không phù hợp mục tiêu gọn nhẹ của V1. | V3 (Intelligent Robotics) |
| **Kiến trúc Microservices phân tán cao cấp** | Gây lãng phí tài nguyên và khó khăn khi cài đặt cho người dùng cơ bản. | Không nằm trong lộ trình |
| **Huấn luyện trực tiếp mô hình nặng bên trong Web App** | Web app chỉ chạy Inference và lightweight demo step. Quá trình training thực tế được thực hiện qua script độc lập hoặc Colab. | Giữ nguyên nguyên tắc tách biệt |

---

## 4. TIÊU CHÍ NGHIỆM THU PHIÊN BẢN V1 (ACCEPTANCE CRITERIA)

Dự án V1 được đánh giá hoàn thành khi thỏa mãn đầy đủ 8 tiêu chí định lượng sau:

1. **[Môi trường]** `WarehouseGridEnv` đạt chuẩn Gymnasium API (`reset()`, `step()`, `render()`), vượt qua kiểm thử unit test tự động.
2. **[Hội tụ thuật toán]**
   - Q-Learning đạt **Success Rate $\ge 95\%$** trên bản đồ cố định $10 \times 10$ sau tối đa 2,000 episodes.
   - PyTorch DQN đạt **Success Rate $\ge 90\%$** và **Collision Rate $\le 5\%$** trên bộ benchmark maps sau quá trình huấn luyện.
3. **[Đối chuẩn A\*]** Thuật toán A* giải được $100\%$ các bản đồ hợp lệ (có đường đi), cung cấp đường đi ngắn nhất chuẩn để so sánh.
4. **[Đóng gói Model Artifact]** Xuất thành công tệp weights kèm `metadata.json` chứa đầy đủ cấu hình hyperparameter, input dimensions và seed.
5. **[Backend Serving]** Backend FastAPI nạp được model artifact từ thư mục quy định, thực thi inference bước tiếp theo với độ trễ $< 5$ ms.
6. **[Frontend Render]** Canvas 2D hiển thị đầy đủ bản đồ, robot chuyển động mượt mà không giật lag, cập nhật đúng vị trí và trạng thái va chạm.
7. **[Báo cáo Khoa học]** Bảng số liệu so sánh chi tiết giữa: Random Policy vs A* vs Q-Learning vs DQN trên 3 bộ bản đồ chuẩn (Easy, Medium, Hard).
8. **[Triển khai 1-Lệnh]** Toàn bộ ứng dụng khởi chạy thành công thông qua lệnh `docker compose up --build`.

---

## 5. RÀNG BUỘC PHI CHỨC NĂNG (NON-FUNCTIONAL REQUIREMENTS)

- **Hiệu năng (Performance):** Backend inference phản hồi dưới 10ms/bước; Frontend duy trì tốc độ khung hình tối thiểu 30-60 FPS khi mô phỏng.
- **Tính khả lập (Reproducibility):** Mọi thí nghiệm AI phải khai báo `seed` rõ ràng để tái hiện chính xác kết quả.
- **Tính module hóa (Modularity):** Module AI (`robopilot_ai`) hoàn toàn có thể chạy độc lập dưới dạng CLI hoặc thư viện mà không cần bật Backend hay Frontend.
- **Khả năng quan sát (Observability):** Mọi sự kiện mô phỏng, lỗi nạp mô hình, và trạng thái inference đều được ghi log có cấu trúc (structured logging).
