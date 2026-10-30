# ROBOPILOT — MASTER ROADMAP
# LỘ TRÌNH PHÁT TRIỂN DỰ ÁN CHI TIẾT

---

## 1. TỔNG QUAN CÁC GIAI ĐOẠN

```
+-------------------------------------------------------------------------------+
| PHASE 0: SYSTEM DESIGN & ARCHITECTURAL CONTRACTS (Current)                    |
| - Hoàn thiện đặc tả, thiết kế API, Database Schema, Model Spec, Risk Analysis |
+-------------------------------------------------------------------------------+
                                      |
                                      v
+-------------------------------------------------------------------------------+
| PHASE 1: AI/ML CORE & SIMULATION ENVIRONMENT (V1 - Sprint 1)                  |
| - WarehouseGridEnv (Gymnasium), Benchmark Maps, Sensor Models, Unit Tests     |
+-------------------------------------------------------------------------------+
                                      |
                                      v
+-------------------------------------------------------------------------------+
| PHASE 2: ALGORITHMS & TRAINING BENCHMARK (V1 - Sprint 2)                      |
| - A* Search, Q-Learning, PyTorch DQN, Colab/Local Pipeline, Artifact Exporter |
+-------------------------------------------------------------------------------+
                                      |
                                      v
+-------------------------------------------------------------------------------+
| PHASE 3: BACKEND API & DATA PERSISTENCE (V1 - Sprint 3)                       |
| - FastAPI Engine, WebSocket Simulation Stream, Model Loader, PostgreSQL DDL   |
+-------------------------------------------------------------------------------+
                                      |
                                      v
+-------------------------------------------------------------------------------+
| PHASE 4: FRONTEND SIMULATION ARENA & ANALYTICS (V1 - Sprint 4)                |
| - React 18 Canvas 2D Arena, Agent Controls, Live Metrics & Comparison Charts  |
+-------------------------------------------------------------------------------+
                                      |
                                      v
+-------------------------------------------------------------------------------+
| PHASE 5: SYSTEM INTEGRATION & DOCKERIZATION (V1 - Sprint 5)                   |
| - Docker Compose E2E, Model Volume Mounts, Cross-module Testing, Healthchecks  |
+-------------------------------------------------------------------------------+
                                      |
                                      v
+-------------------------------------------------------------------------------+
| PHASE 6: BENCHMARK SUITE, EVALUATION REPORT & V1 RELEASE (V1 - Sprint 6)      |
| - Multi-seed Experiments, Evaluation Report, Video Demo, Release Checklist    |
+-------------------------------------------------------------------------------+
                                      |
                 +--------------------+--------------------+
                 |                                         |
                 v                                         v
+---------------------------------+       +---------------------------------+
| FUTURE V2: AUTONOMOUS MOBILITY  |       | FUTURE V3: INTELLIGENT ROBOTICS |
| - Continuous Control (PPO)      |       | - 3D Physics (MuJoCo / Isaac)   |
| - Differential Drive Kinematics |       | - SAC, Domain Randomization     |
| - Virtual LiDAR & Dynamic Obst. |       | - Vision-based Navigation       |
+---------------------------------+       +---------------------------------+
```

---

## 2. CHI TIẾT CÁC SPRINT PHIÊN BẢN V1 (SMART NAVIGATION MVP)

### PHASE 0: SYSTEM DESIGN & ARCHITECTURE (Giai đoạn hiện tại - Đang thực hiện)
- **Mục tiêu:** Hoàn thành toàn bộ tài liệu thiết kế kiến trúc, hợp đồng giao tiếp (Contracts), đặc tả kỹ thuật và phân tích rủi ro trước khi bắt đầu code.
- **Hồ sơ sản phẩm:**
  - `PROJECT_OVERVIEW.md`
  - `PROJECT_SCOPE.md`
  - `ROADMAP.md`
  - `DECISION_LOG.md`
  - Bảng nhiệm vụ chi tiết giao cho Agent 1 và Agent 2.
  - Bộ câu hỏi phê duyệt gửi Chủ dự án (USER).

---

### PHASE 1: AI/ML CORE & SIMULATION ENVIRONMENT (Sprint 1)
- **Phụ trách:** Agent 1.
- **Nội dung công việc:**
  1. Xây dựng môi trường `WarehouseGridEnv` tuân thủ chuẩn Gymnasium API:
     - `reset(seed, options)`
     - `step(action) -> obs, reward, terminated, truncated, info`
     - `render()`
  2. Tạo bộ 3 bản đồ chuẩn phục vụ nghiên cứu và đánh giá:
     - `benchmark_easy_10x10.json` (Ít vật cản, kiểm tra khả năng hội tụ cơ bản).
     - `benchmark_medium_15x15.json` (Các dãy kệ hàng song song dạng kho thực tế).
     - `benchmark_hard_20x20.json` (Nhiều hành lang hẹp và ngõ cụt để thử thách khả năng thoát kẹt).
  3. Cài đặt các cơ chế quan sát (Observation Modes):
     - Mode A: Relative Goal Coordinates + Robot Position.
     - Mode B: Proximity Raycast (4/8 hướng) + Goal Direction (hỗ trợ chuyển giao bản đồ).
  4. Bộ kiểm thử môi trường (Environment Validation Tests):
     - Kiểm tra va chạm biên.
     - Kiểm tra va chạm vật cản.
     - Kiểm tra điều kiện dừng (đạt đích hoặc vượt quá max steps).

---

### PHASE 2: ALGORITHM IMPLEMENTATION & BENCHMARKS (Sprint 2)
- **Phụ trách:** Agent 1.
- **Nội dung công việc:**
  1. Triển khai thuật toán **A\* Search** làm mốc đối chuẩn tối ưu lý thuyết (Optimal Ground Truth).
  2. Triển khai thuật toán **Tabular Q-Learning** với $\epsilon$-greedy schedule.
  3. Triển khai thuật toán **Deep Q-Network (DQN)** bằng PyTorch:
     - Module Q-Network MLP.
     - Target Network với chu kỳ đồng bộ trọng số.
     - Experience Replay Buffer (Circular memory array).
  4. Xây dựng Pipeline huấn luyện độc lập (chạy được cả trên Local CPU/GPU và Google Colab qua script hoặc notebook).
  5. Thiết kế và triển khai cơ chế xuất đóng gói mô hình:
     - Tệp trọng số `.pt` (PyTorch) hoặc `.pkl` (Q-table).
     - Tệp siêu dữ liệu `metadata.json` (kiến trúc, siêu tham số, kích thước observation/action, chỉ số đánh giá).
  6. Chạy thực nghiệm với ít nhất 3 random seeds để thu thập số liệu chuẩn mực (Success Rate, Collision Rate, Episode Reward, Steps to Goal).

---

### PHASE 3: BACKEND API & DATA PERSISTENCE (Sprint 3)
- **Phụ trách:** Agent 2 (phối hợp Agent 1 về Model Loader).
- **Nội dung công việc:**
  1. Khởi tạo kiến trúc ứng dụng FastAPI theo mô hình dịch vụ module hóa:
     - Routers: `/api/v1/maps`, `/api/v1/models`, `/api/v1/experiments`, `/api/v1/simulation`.
     - Services: `SimulationService`, `ModelManagerService`, `ExperimentService`.
  2. Cài đặt WebSocket Endpoint `/ws/simulation`:
     - Nhận lệnh điều khiển từ Client (Start, Pause, Reset, Step, SetSpeed).
     - Phát luồng dữ liệu từng bước mô phỏng: tọa độ robot, trạng thái lưới, action đã chọn, Q-values dự đoán, reward tức thời.
  3. Xây dựng bộ nạp mô hình động (Dynamic Model Loader):
     - Đọc và validate package (`weights` + `metadata.json`).
     - Hỗ trợ chuyển đổi tức thì giữa các mô hình đã nạp.
  4. Thiết kế và khởi tạo cơ sở dữ liệu PostgreSQL (SQLAlchemy / Alembic / asyncpg):
     - Bảng `maps`, `experiments`, `models`, `benchmark_runs`.

---

### PHASE 4: FRONTEND SIMULATION ARENA & ANALYTICS (Sprint 4)
- **Phụ trách:** Agent 2.
- **Nội dung công việc:**
  1. Thiết lập dự án React 18 + Vite + TypeScript với UI component kit hiện đại (Tailwind CSS hoặc shadcn/ui).
  2. Xây dựng **Simulation Arena (HTML5 Canvas 2D)**:
     - Render bản đồ dạng lưới siêu mượt với màu sắc phân biệt rõ ràng.
     - Robot hiển thị kèm hướng di chuyển, hiệu ứng vệt đường đi (path trail) và hiệu ứng va chạm.
  3. Xây dựng **Agent Control Panel**:
     - Nút điều khiển tương tác trực quan: Play, Pause, Step-forward, Reset.
     - Slider điều chỉnh tốc độ mô phỏng (Ticks per second).
     - Dropdown chọn bản đồ và chọn model/thuật toán (A*, Q-Learning, DQN).
  4. Xây dựng **Analytics Dashboard**:
     - Tích hợp thư viện biểu đồ (Chart.js hoặc Recharts).
     - Biểu đồ thời gian thực: Reward theo episode, Success rate, Collision rate.
     - Bảng so sánh hiệu năng trực tiếp giữa A* và RL.
  5. Quản lý trạng thái và kết nối WebSocket bền bỉ (auto-reconnect).

---

### PHASE 5: SYSTEM INTEGRATION & DOCKERIZATION (Sprint 5)
- **Phụ trách:** Agent 0 & Agent 2.
- **Nội dung công việc:**
  1. Xây dựng `Dockerfile` tối ưu cho Backend (Python slim image, multi-stage nếu cần).
  2. Xây dựng `Dockerfile` cho Frontend (Node build -> Nginx serving).
  3. Xây dựng tệp `docker-compose.yml` hoàn chỉnh gắn kết:
     - Service `backend` (FastAPI).
     - Service `frontend` (Nginx).
     - Service `db` (PostgreSQL 15 với healthcheck).
     - Volume mapping cho thư mục `./models` và `./maps` để nạp dữ liệu thuận tiện.
  4. Chạy kiểm thử End-to-End toàn diện:
     - Luồng: Tải bản đồ -> Nạp model DQN -> Bắt đầu mô phỏng -> Quan sát trên Arena -> Xuất báo cáo.

---

### PHASE 6: BENCHMARK SUITE, EVALUATION REPORT & RELEASE (Sprint 6)
- **Phụ trách:** Toàn bộ Agent team.
- **Nội dung công việc:**
  1. Chạy bài kiểm tra đối chuẩn tự động (Automated Benchmark Suite) trên toàn bộ 3 bản đồ chuẩn.
  2. So sánh và đối chiếu số liệu khoa học giữa:
     - Random Policy vs A* Search vs Q-Learning vs DQN.
  3. Tổng hợp Báo cáo Thực nghiệm Nghiên cứu (`EVALUATION_REPORT.md`):
     - Đánh giá khả năng tổng quát hóa trên bản đồ mới.
     - Đánh giá độ trễ tính toán (Inference latency).
  4. Hoàn thiện tài liệu hướng dẫn cài đặt và sử dụng (`README.md`, `SETUP_GUIDE.md`).
  5. Nghiệm thu bàn giao phiên bản V1.

---

## 3. LỘ TRÌNH MỞ RỘNG TƯƠNG LAI (FUTURE ROADMAP)

### V2 — AUTONOMOUS NAVIGATION (Dự kiến)
- Chuyển đổi môi trường từ Discrete Grid sang **Continuous State & Action Space**.
- Mô phỏng động học robot 2 bánh vi sai (**Differential Drive Kinematics**: $v, \omega$).
- Tích hợp cảm biến khoảng cách liên tục (Virtual LiDAR Raycasting 16-32 tia).
- Nghiên cứu và áp dụng thuật toán **PPO (Proximal Policy Optimization)**.
- Thử nghiệm với chướng ngại vật di động (Dynamic obstacles).

### V3 — INTELLIGENT ROBOTICS (Dự kiến)
- Chuyển sang mô phỏng vật lý 3D hoàn chỉnh sử dụng **MuJoCo** hoặc **NVIDIA Isaac Gym**.
- Thuật toán **SAC (Soft Actor-Critic)** và điều khiển nhiều bậc tự do.
- Kỹ thuật **Domain Randomization** để thu hẹp khoảng cách Sim-to-Real (Simulation-to-Reality Gap).
- Điều hướng dựa trên thị giác (Vision-based Navigation với camera RGB-D).
