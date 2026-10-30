# ROBOPILOT — PROJECT OVERVIEW
# TỔNG QUAN NỀN TẢNG MÔ PHỎNG & HUẤN LUYỆN ROBOT TỰ HÀNH

---

## 1. GIỚI THIỆU DỰ ÁN

- **Tên dự án:** RoboPilot
- **Tên đầy đủ:** Autonomous Mobile Robot Learning & Simulation Platform
- **Slogan:** *Teaching Autonomous Robots to Navigate Through Reinforcement Learning*
- **Giai đoạn hiện tại:** **DESIGN PHASE** (Không triển khai code sản phẩm, không cài dependencies cho đến khi hoàn thành thiết kế)
- **Đơn vị chủ trì:** Agent 0 (System Lead & Architect) phối hợp cùng Agent 1 (AI/ML) và Agent 2 (Software Engineering).

### 1.1. Sứ mệnh & Tầm nhìn
RoboPilot giải quyết bài toán cốt lõi trong tự động hóa kho hàng thông minh: **Làm thế nào để robot vận chuyển tự hành (AMR - Autonomous Mobile Robot) có thể học được chiến lược điều hướng tối ưu, tránh chướng ngại vật tĩnh và thích nghi linh hoạt thông qua tương tác môi trường (Reinforcement Learning), thay vì chỉ phụ thuộc vào các đường đi cứng (hardcoded paths) hoặc bản đồ cố định.**

Đồng thời, RoboPilot được xây dựng như một sản phẩm kỹ thuật phần mềm hoàn chỉnh, cầu nối giữa:
1. **AI/ML Research:** Nghiên cứu thuật toán RL (Q-Learning, DQN), thiết kế hàm thưởng (reward shaping), đánh giá thực nghiệm đa hạt nhân (multi-seed benchmarks) và đối chuẩn công bằng với thuật toán tìm đường cổ điển (A*).
2. **Software Engineering:** Kiến trúc chuẩn mực với Backend FastAPI, cơ sở dữ liệu PostgreSQL lưu trữ metadata, giao diện trực quan hóa React Vite (Canvas 2D render thời gian thực) và container hóa bằng Docker Compose.

---

## 2. Ý TƯỞNG CỐT LÕI & MÔ HÌNH TOÁN HỌC

```
                  +----------------------------------------------+
                  |                 ENVIRONMENT                  |
                  |     WarehouseGridEnv (Gymnasium-based)       |
                  +----------------------------------------------+
                         ^                             |
                         | Action                      | State (Observation)
                         | a_t in A                    | s_t in S
                         |                             | Reward r_t, Done d_t
                         |                             v
                  +----------------------------------------------+
                  |                    AGENT                     |
                  |  [A* Baseline | Q-Learning | PyTorch DQN]   |
                  +----------------------------------------------+
```

### 2.1. Không gian bài toán (Markov Decision Process - MDP)
Bài toán điều hướng kho hàng được mô hình hóa dưới dạng một quá trình quyết định Markov hữu hạn $(\mathcal{S}, \mathcal{A}, \mathcal{P}, \mathcal{R}, \gamma)$:
- **$\mathcal{S}$ (State Space):** Tập hợp các trạng thái mô tả robot và môi trường. Trong V1 (Grid World), trạng thái bao gồm vị trí tương đối/tuyệt đối của robot, vị trí mục tiêu (goal), và cảm biến vật cản lân cận.
- **$\mathcal{A}$ (Action Space):** Tập hợp hành động rời rạc: $\{ \text{Up}, \text{Down}, \text{Left}, \text{Right} \}$.
- **$\mathcal{P}$ (Transition Probability):** Xác suất chuyển trạng thái $P(s_{t+1} \mid s_t, a_t)$. Trong môi trường xác định (deterministic grid), robot di chuyển chính xác theo hướng chọn nếu không gặp tường/vật cản.
- **$\mathcal{R}$ (Reward Function):** Tín hiệu phản hồi từ môi trường nhằm khuyến khích robot đến đích an toàn, rút ngắn thời gian di chuyển và triệt tiêu va chạm.
- **$\gamma$ (Discount Factor):** Hệ số chiết khấu phần thưởng tương lai ($\gamma \in [0.95, 0.99]$).

### 2.2. Triết lý đối chuẩn (Fair Baseline Principle)
RoboPilot **không mặc định Reinforcement Learning luôn vượt trội hơn các phương pháp tìm đường cổ điển**. 
- **A\* Search** tìm được đường đi ngắn nhất tuyệt đối nếu có toàn bộ bản đồ tĩnh (Perfect Global Information).
- **Q-Learning / DQN** thể hiện khả năng học chính sách (policy $\pi(a|s)$) thông qua thử sai, có khả năng phản xạ nhanh khi suy luận (inference thời gian thực tính bằng mili-giây với một forward-pass) và là nền tảng để mở rộng cho môi trường động, bất định trong V2 và V3.
- Mọi đánh giá phải được lượng hóa bằng số liệu: Success Rate, Collision Rate, Path Optimality Ratio (so với A*), Episode Length, Inference Latency.

---

## 3. KIẾN TRÚC TỔNG THỂ HỆ THỐNG

Kiến trúc RoboPilot V1 được thiết kế theo mô hình phân tầng module hóa cao độ, đảm bảo nguyên tắc tách biệt độc lập giữa **Training Pipeline** và **Inference/Serving Platform**.

```
+-----------------------------------------------------------------------------------------+
|                                TRAINING SUBSYSTEM                                       |
|  - Local CLI / Google Colab Notebooks                                                   |
|  - Training Engine: WarehouseGridEnv + Q-Learning / PyTorch DQN                         |
|  - Multi-seed Evaluation & Experiment Tracking                                          |
|  - Output: Model Artifacts (model.pt, q_table.pkl, metadata.json)                       |
+-----------------------------------------------------------------------------------------+
                                           |
                                           | Artifact Delivery (Filesystem / Volume Mount)
                                           v
+-----------------------------------------------------------------------------------------+
|                                APPLICATION SUBSYSTEM (Docker)                           |
|                                                                                         |
|   +------------------------------------+       +------------------------------------+   |
|   |         FRONTEND CLIENT            |       |          BACKEND API               |   |
|   |  - React 18 + TypeScript + Vite    | <===> |  - FastAPI (Python 3.10+)          |   |
|   |  - Canvas 2D Simulation Arena      | HTTP/ |  - Model Inference Engine          |   |
|   |  - Agent Control Panel             | WSS   |  - Simulation Loop Controller      |   |
|   |  - Analytics & Benchmark Charts    |       |  - WarehouseGridEnv Mirror         |   |
|   +------------------------------------+       +------------------------------------+   |
|                                                                  |                      |
|                                                                  v                      |
|                                                +------------------------------------+   |
|                                                |         DATABASE LAYER             |   |
|                                                |  - PostgreSQL 15                   |   |
|                                                |  - Experiment & Model Metadata     |   |
|                                                |  - Benchmark Runs & Map Layouts    |   |
|                                                +------------------------------------+   |
+-----------------------------------------------------------------------------------------+
```

---

## 4. CÁC PHÂN HỆ CHỨC NĂNG (5 CORE MODULES)

### Module 1: Simulation Arena (Đấu trường mô phỏng 2D)
- Render lưới kho hàng tương tác cao bằng HTML5 Canvas 2D.
- Thể hiện trực quan: Vị trí Robot (với icon/màu sắc nhận diện), Hướng nhìn, Điểm Start, Điểm Goal, Kệ hàng/Chướng ngại vật tĩnh.
- Hiển thị dấu vết di chuyển (Trajectory Trail) và điểm xảy ra va chạm (Collision Indicator).
- Hỗ trợ tải các bản đồ mẫu (Benchmark Maps: Easy 10x10, Medium 15x15, Hard 20x20 Warehouse).

### Module 2: Agent Control (Điều khiển tác tử)
- Lựa chọn thuật toán: `Random Policy`, `A* Search (Baseline)`, `Q-Learning`, `DQN (PyTorch)`.
- Chế độ hoạt động:
  - **Inference Mode:** Nạp checkpoint đã huấn luyện, chạy điều hướng trên bản đồ, không cập nhật trọng số.
  - **Step-by-Step Mode:** Cho phép bước từng tick để quan sát quyết định của AI ($Q$-values / action probabilities).
  - **Continuous Run Mode:** Chạy liên tục với thanh điều chỉnh tốc độ (Simulation FPS: 1x, 2x, 5x, 10x).
- Điều khiển: Start, Pause, Resume, Reset Environment.

### Module 3: Training & Inference Analytics (Phân tích hiệu năng)
- Dashboard biểu đồ thời gian thực (Line Charts, Bar Charts):
  - Episode Reward Curve (Moving Average 100 episodes).
  - Success Rate (% đến đích an toàn).
  - Collision Rate (% đâm vào tường/vật cản).
  - Average Episode Length / Steps to Goal.
- So sánh song song (Side-by-side comparison): A* vs Q-Learning vs DQN trên cùng một bản đồ.

### Module 4: Experiment Management (Quản lý thí nghiệm)
- Lưu trữ lịch sử huấn luyện: Mã thí nghiệm (Experiment ID), Hyperparameters (learning rate $\alpha$, discount $\gamma$, epsilon decay, batch size, buffer capacity), seed.
- Bảng tổng hợp Leaderboard: Xếp hạng các model tốt nhất theo Success Rate và độ dài đường đi tối ưu.

### Module 5: Model Management (Quản trị mô hình AI)
- Danh mục Model Checkpoints với chi tiết phiên bản, ngày tạo, thuật toán, kích thước tệp trọng số.
- Nạp động (Dynamic Loading) model vào Backend runtime mà không cần khởi động lại server.
- Xác thực tính hợp lệ của Model Artifact Package (`model.pt` + `metadata.json`) trước khi nạp.

---

## 5. PHÂN BỔ TRÁCH NHIỆM 7 CHUYÊN GIA AI (7-AGENT ORGANIZATION)

| Agent | Vai trò chuyên biệt | Phạm vi phụ trách chính trong Design Phase | Tài liệu bàn giao |
| :--- | :--- | :--- | :--- |
| **Agent 0** | **Project Orchestrator & System Architect** | Quản lý dự án tổng thể, phân công nhiệm vụ, kiến trúc hệ thống, kiểm soát scope và quản lý nhật ký quyết định. | `PROJECT_OVERVIEW.md`, `PROJECT_SCOPE.md`, `ROADMAP.md`, `SYSTEM_ARCHITECTURE.md`, `COMPONENT_DIAGRAM.md`, `DATA_FLOW.md`, `DECISION_LOG.md` |
| **Agent 1** | **Robotics & RL Research Specialist** | Nghiên cứu thuật toán RL (Q-Learning, DQN, PPO, SAC), baseline A*, Reward Shaping (PBRS) và chống Reward Hacking. | `RL_RESEARCH.md`, `ALGORITHM_COMPARISON.md`, `REWARD_DESIGN.md` |
| **Agent 2** | **Simulation & Environment Designer** | Thiết kế môi trường Warehouse 2D, Gymnasium API (`reset`, `step`, `render`, `close`), tọa độ, robot, vật cản, va chạm. | `ENVIRONMENT_SPEC.md`, `ROBOT_SPEC.md`, `STATE_ACTION_SPEC.md`, `SIMULATION_DESIGN.md` |
| **Agent 3** | **ML/RL Engineer & Training Architect** | Thiết kế pipeline huấn luyện, PyTorch DQN architecture (Replay Buffer, Target Sync), Colab workflow, Model Artifact Contract. | `TRAINING_PIPELINE.md`, `MODEL_LIFECYCLE.md`, `EXPERIMENT_DESIGN.md` |
| **Agent 4** | **Backend & MLOps Architect** | Thiết kế Backend FastAPI, REST & WebSocket API, Model Loader, PostgreSQL Schema, Docker Compose infrastructure. | `BACKEND_DESIGN.md`, `API_SPEC.md`, `DATABASE_SCHEMA.md`, `DOCKER_DESIGN.md` |
| **Agent 5** | **Frontend & UX/UI Designer** | Thiết kế giao diện React 18 Vite TypeScript, Canvas 2D Arena, Dashboard 5 modules, WebSocket client state. | `UI_UX_SPEC.md`, `FRONTEND_ARCHITECTURE.md`, `DASHBOARD_DESIGN.md` |
| **Agent 6** | **QA & Research Validation Specialist** | Kiểm thử độc lập, rà soát 11 hợp đồng kỹ thuật, kiểm tra nguy cơ reward hacking/overfitting, xây dựng tiêu chí nghiệm thu. | `TEST_PLAN.md`, `EVALUATION_PLAN.md`, `ACCEPTANCE_CRITERIA.md` |

---

## 6. NGUYÊN TẮC THIẾT KẾ VÀ RÀNG BUỘC KỸ THUẬT

1. **Tuân thủ Design-First:** Tuyệt đối không viết code ứng dụng, không cài thư viện trong giai đoạn thiết kế. Mọi interface phải được mô tả rõ dạng hợp đồng dữ liệu (API Specs, JSON Schema).
2. **Reproducibility:** Mọi thực nghiệm AI phải kiểm soát được Random Seed. Báo cáo thực nghiệm phải có Mean và Standard Deviation qua ít nhất 3-5 seeds.
3. **Decoupled Architecture:** Huấn luyện có thể diễn ra độc lập (Local/Colab). Backend chỉ đóng vai trò serving & environment simulation for inference.
4. **Không Over-engineering:** Giữ V1 gọn gàng, tập trung tối đa vào độ ổn định của Discrete Grid 2D trước khi nghĩ đến Continuous Motion trong V2 hay 3D MuJoCo trong V3.
