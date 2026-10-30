# ROBOPILOT — SYSTEM ARCHITECTURE SPECIFICATION
# KIẾN TRÚC TỔNG THỂ HỆ THỐNG ROBOPILOT V1 (MVP)

> **Tài liệu thuộc trách nhiệm:** Agent 0 (Project Orchestrator & System Architect)  
> **Trạng thái:** DRAFT / DESIGN PHASE (Chờ phê duyệt tổng thể)  
> **Ngày ban hành:** 2026-10-29  

---

## 1. TỔNG QUAN VÀ TRIẾT LÝ THIẾT KẾ

RoboPilot được thiết kế theo kiến trúc module hóa phân tầng (Layered Modular Architecture), giải quyết triệt để 2 mục tiêu:
1. **AI/ML Research:** Môi trường thí nghiệm khoa học có thể kiểm chứng, tái lập thực nghiệm (multi-seed), tách biệt hoàn toàn giữa quá trình huấn luyện và phục vụ mô hình.
2. **Software Engineering:** Nền tảng ứng dụng web trực quan, có độ trễ thấp, kết hợp REST API và WebSocket để stream dữ liệu mô phỏng thời gian thực, triển khai toàn diện qua Docker.

### 1.1. Triết lý phân tách cốt lõi (Decoupled Subsystems)
- **Training Subsystem (Ngoại tuyến / Offline):** Độc lập với web server, có thể chạy trên máy tính cá nhân (CPU/GPU) hoặc Google Colab GPU. Đầu ra là **Model Artifact Package** (`model.pt` + `metadata.json`).
- **Serving & Visualization Subsystem (Trực tuyến / Online):** Hệ thống web ứng dụng (FastAPI + React Vite + PostgreSQL + Docker). Nạp model artifact đã train và chạy mô phỏng suy luận (Inference Mode), không thực hiện backpropagation hay training nặng trong runtime của web server.

```
+---------------------------------------------------------------------------------------+
|                                TRAINING SUBSYSTEM                                     |
|  [Google Colab GPU / Local CLI]                                                       |
|  - Gymnasium Environment (WarehouseGridEnv-v0)                                        |
|  - Agent 1: RL Formulations & Reward Shaping                                          |
|  - Agent 3: PyTorch DQN Engine, Replay Buffer, Target Sync                            |
|  - Multi-seed Evaluation Pipeline                                                     |
|  ===> OUTPUT: Model Artifact Package (/models/{model_id}/model.pt + metadata.json)    |
+---------------------------------------------------------------------------------------+
                                           |
                                           | Volume Mount / Artifact Registry
                                           v
+---------------------------------------------------------------------------------------+
|                              SERVING & PLATFORM SUBSYSTEM                             |
|  [Docker Compose Orchestration]                                                       |
|                                                                                       |
|   +------------------------------------+     +------------------------------------+   |
|   |         FRONTEND SERVICE           |     |          BACKEND SERVICE           |   |
|   |  - React 18 + TypeScript + Vite    |     |  - FastAPI (Python 3.10+)          |   |
|   |  - Agent 5: HTML5 Canvas 2D Arena  | <== |  - Agent 4: REST API Engine        |   |
|   |  - Agent Control & Speed Slider    | WSS |  - WebSocket Sim Stream Server     |   |
|   |  - Recharts Analytics Dashboard    |     |  - Dynamic Model Loader Service    |   |
|   +------------------------------------+     +------------------------------------+   |
|                                                                 |                     |
|                                                                 v                     |
|                                              +------------------------------------+   |
|                                              |          DATABASE SERVICE          |   |
|                                              |  - PostgreSQL 15                   |   |
|                                              |  - Metadata, Runs, Experiments     |   |
|                                              +------------------------------------+   |
+---------------------------------------------------------------------------------------+
```

---

## 2. PHÂN TẦNG HỆ THỐNG (ARCHITECTURAL LAYERS)

### 2.1. Tầng Môi trường & Mô hình toán học (Environment & Math Layer)
- **Trách nhiệm:** Agent 1 (RL Research) & Agent 2 (Simulation Designer).
- **Thành phần:**
  - `WarehouseGridEnv`: Tuân thủ nghiêm ngặt Gymnasium API (`reset`, `step`, `render`, `close`).
  - `ObservationBuilder`: Hỗ trợ 2 chế độ:
    - *Coordinate Mode:* `[robot_x, robot_y, goal_x, goal_y]` (cho Tabular Q-Learning).
    - *Proximity Raycast Mode:* 4 cảm biến khoảng cách vật cản $+ [\Delta x, \Delta y, \text{dist}]$ (cho DQN tổng quát hóa).
  - `RewardEngine`: Potential-based Reward Shaping ($F(s,s') = \gamma \Phi(s') - \Phi(s)$) ngăn chặn tuyệt đối hiện tượng Reward Hacking / cycling.
  - `CollisionDetector`: Kiểm tra ranh giới bản đồ và tọa độ kệ hàng dạng ma trận logic tĩnh $O(1)$.

### 2.2. Tầng Thuật toán & Huấn luyện (Algorithm & Training Layer)
- **Trách nhiệm:** Agent 1 & Agent 3.
- **Thành phần:**
  - `AStarPlanner`: Thuật toán tìm đường ngắn nhất tối ưu (Ground Truth Heuristic).
  - `QLearningAgent`: Bảng tra cứu $Q(s, a)$ với $\epsilon$-greedy decay.
  - `DQNAgent`: Mạng PyTorch MLP ($2$ hidden layers $\times 128$ units), Experience Replay Buffer ($50,000$ transitions), Target Q-Network với chu kỳ đồng bộ định kỳ ($C = 1,000$ steps).
  - `ArtifactExporter`: Tự động đóng gói model weights kèm `metadata.json` chứa đầy đủ cấu hình hyperparameter, input dimensions và metrics kiểm thử.

### 2.3. Tầng Dịch vụ Backend & MLOps (Backend & Serving Layer)
- **Trách nhiệm:** Agent 4.
- **Thành phần:**
  - `FastAPI Core`: API Gateway xử lý routing, CORS, middleware, dependency injection.
  - `DynamicModelLoader`: Tự động kiểm tra tính hợp lệ của `metadata.json`, nạp state_dict PyTorch vào RAM và thiết lập chế độ `model.eval()`.
  - `SimulationEngine`: Quản lý phiên mô phỏng (session), thực hiện từng bước di chuyển (tick), tính toán và truyền phát dữ liệu qua WebSocket.
  - `DataPersistence`: Quản lý kết nối PostgreSQL qua SQLAlchemy / asyncpg, lưu trữ thông tin map, lịch sử chạy benchmark và metadata của model.

### 2.4. Tầng Trực quan hóa & Giao diện (Presentation & UX Layer)
- **Trách nhiệm:** Agent 5.
- **Thành phần:**
  - `Canvas2D Renderer`: Vẽ lưới kho hàng, robot với góc nhìn hướng, các dãy kệ hàng, điểm Start/Goal, vệt đường đi đã qua (trajectory trail), hiệu ứng va chạm. Tối ưu hóa 60 FPS.
  - `AgentController`: Quản lý trạng thái mô phỏng: Run, Pause, Step-forward, Reset, điều chỉnh tốc độ từ $1$ FPS đến $20$ FPS.
  - `AnalyticsDashboard`: Trực quan hóa biểu đồ học tập (Moving average reward, Success rate, Collision rate) và bảng đối chuẩn so sánh song song giữa A* và RL.
  - `WebSocketClientManager`: Duy trì kết nối hai chiều bền bỉ với cơ chế tự động kết nối lại (auto-reconnect).

### 2.5. Tầng Đảm bảo Chất lượng & Đánh giá (QA & Validation Layer)
- **Trách nhiệm:** Agent 6.
- **Thành phần:**
  - Kiểm định toàn diện 11 hợp đồng kỹ thuật (Technical Contracts).
  - Bộ tiêu chí nghiệm thu định lượng (Acceptance Criteria Matrix).
  - Kiểm thử khả năng tái lập thực nghiệm (Multi-seed verification protocol).

---

## 3. MAPPING 5 MODULES SẢN PHẨM VÀO KIẾN TRÚC

| Module Sản phẩm | Trách nhiệm chính | Thành phần kỹ thuật | Phương thức giao tiếp |
| :--- | :--- | :--- | :--- |
| **Module 1: Simulation Arena** | Agent 2, Agent 5 | HTML5 Canvas 2D, Grid Renderer, Trajectory Tracker | WebSocket (`TICK` frame) |
| **Module 2: Agent Control** | Agent 4, Agent 5 | FastAPI WebSocket Manager, Session Controller, Speed Slider | WebSocket (`COMMAND` frame) |
| **Module 3: Training Analytics** | Agent 3, Agent 5 | Recharts Library, Metric Aggregator, Colab Exporter | REST API (`/api/v1/experiments/{id}`) |
| **Module 4: Experiment Management**| Agent 4, Agent 5 | PostgreSQL `experiments` table, SQLAlchemy ORM | REST API (`/api/v1/experiments`) |
| **Module 5: Model Management** | Agent 3, Agent 4 | Model Registry, `/models` Volume, Checkpoint Loader | REST API (`/api/v1/models`) |

---

## 4. QUẢN LÝ 11 HỢP ĐỒNG KỸ THUẬT BẮT BUỘC (TECHNICAL CONTRACTS)

Hệ thống yêu cầu sự thống nhất tuyệt đối của 11 hợp đồng sau trước khi bước vào Development Phase:

1. **Observation Space Contract:** Thống nhất giữa Agent 1, 2, 3 về shape, kiểu dữ liệu, phạm vi chuẩn hóa của vector quan sát.
2. **Action Space Contract:** Thống nhất mã hóa 4 hướng di chuyển: `0: UP`, `1: DOWN`, `2: LEFT`, `3: RIGHT`.
3. **Reward Function Contract:** Thống nhất công thức tính toán điểm thưởng giữa Agent 1 và Agent 2.
4. **Environment API Contract:** Chuẩn Gymnasium (`reset`, `step`, `render`, `close`) giữa Agent 2 và Agent 3.
5. **Training Pipeline Contract:** Định dạng tham số đầu vào và đầu ra của script training giữa Agent 1 và Agent 3.
6. **Model Artifact Contract:** Cấu trúc tệp nhị phân và schema của `metadata.json` giữa Agent 3 và Agent 4.
7. **Backend REST API Contract:** Đặc tả OpenAPI (Swagger) giữa Agent 4 và Agent 5.
8. **Database Schema Contract:** Cấu trúc bảng và quan hệ cơ sở dữ liệu giữa Agent 4 và Agent 0.
9. **Frontend Data Contract:** Cấu trúc dữ liệu khung truyền WebSocket giữa Agent 4 và Agent 5.
10. **Evaluation Metrics Contract:** Bộ công thức tính Success Rate, Collision Rate, Path Ratio giữa Agent 1, 3, 6.
11. **Docker Service Contract:** Cổng port, biến môi trường, network và volume mapping giữa Agent 4 và Agent 0.

---

## 5. RÀNG BUỘC PHI CHỨC NĂNG (NON-FUNCTIONAL SPECIFICATIONS)

- **Độ trễ suy luận (Inference Latency):** Mạng PyTorch DQN forward pass trên CPU thực hiện trong $< 2$ ms; tổng thời gian xử lý và gửi WebSocket tick $< 10$ ms.
- **Tốc độ khung hình (Rendering Frame Rate):** Đạt ổn định $60$ FPS trên trình duyệt thông thường với lưới kích thước lên tới $30 \times 30$.
- **Tính khả lập (Reproducibility):** Mọi lần huấn luyện và benchmark bắt buộc phải gán `seed` cụ thể; các chỉ số báo cáo là giá trị trung bình qua ít nhất 3-5 seeds ngẫu nhiên.
- **Dung lượng đóng gói:** Docker image backend tối ưu $< 600$ MB bằng multi-stage build và Python slim base image.
