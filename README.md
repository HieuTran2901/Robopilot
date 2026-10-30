# 🤖 RoboPilot: Autonomous Mobile Robot Learning & Simulation Platform

<div align="center">

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C.svg?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![Gymnasium](https://img.shields.io/badge/Gymnasium-v0.29%2B-darkgreen.svg)](https://gymnasium.farama.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg?logo=react&logoColor=black)](https://react.dev/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Repository](https://img.shields.io/badge/GitHub-HieuTran2901%2FRobopilot-181717.svg?logo=github&logoColor=white)](https://github.com/HieuTran2901/Robopilot.git)

**Teaching Autonomous Mobile Robots (AMR) to Navigate Through Reinforcement Learning**  
*Một nền tảng kỹ thuật phần mềm & nghiên cứu AI hoàn chỉnh: từ mô phỏng môi trường nhà kho thông minh, huấn luyện học tăng cường đến trực quan hóa thời gian thực trên Web và đóng gói Docker.*

[🌐 GitHub Repository](https://github.com/HieuTran2901/Robopilot.git) • [📖 Kiến trúc Hệ thống](SYSTEM_ARCHITECTURE.md) • [🗺️ Lộ trình Phát triển](ROADMAP.md) • [📑 Nhật ký Quyết định](DECISION_LOG.md)

</div>

---

## 📌 1. TỔNG QUAN DỰ ÁN (PROJECT OVERVIEW)

**RoboPilot** là nền tảng mô phỏng và huấn luyện xe tự hành (Autonomous Mobile Robot - AMR) trong môi trường nhà kho thông minh (Smart Warehouse) sử dụng **Reinforcement Learning (Học tăng cường)**.

Dự án không dừng lại ở một file Jupyter Notebook đơn lẻ, mà được thiết kế như một **sản phẩm phần mềm hoàn chỉnh (Production-grade AI System)** dung hòa giữa hai trụ cột:
1. **AI/ML Research:** Mô hình hóa bài toán Markov Decision Process (MDP), nghiên cứu thuật toán **Dueling Double DQN (D3QN)**, giải quyết triệt để lỗi *Reward Hacking* bằng **Potential-based Reward Shaping (PBRS)**, và đối chuẩn công bằng (Fair Benchmarking) với thuật toán kinh điển **A\* Search**.
2. **Software Engineering & MLOps:** Kiến trúc phân tầng độc lập giữa khâu Huấn luyện (Offline Training) và Phục vụ suy luận (Online Serving), streaming dữ liệu mô phỏng qua **WebSocket**, trực quan hóa Canvas 2D 60 FPS mượt mà bằng **React 18 Vite**, quản lý metadata bằng **PostgreSQL** và triển khai 1-lệnh bằng **Docker Compose**.

---

## 🌟 2. CÁC ĐIỂM NHẤN CÔNG NGHỆ NỔI BẬT (KILLER FEATURES)

- ⚔️ **Sàn đấu đối chuẩn A\* vs Dueling Double DQN:** Đối chiếu trực tiếp giữa thuật toán tìm đường ngắn nhất tối ưu lý thuyết ($A^*$) và mạng nơ-ron học tăng cường ($D3QN$) về: số bước di chuyển, thời gian suy luận (Inference Latency $< 2\text{ms}$), và khả năng thích nghi.
- 🧮 **Toán học Hàm thưởng chống Reward Cycling:** Áp dụng lý thuyết Potential-based Reward Shaping ($F(s, s') = \gamma \Phi(s') - \Phi(s)$ với Manhattan Heuristic), triệt tiêu hoàn toàn hiện tượng robot đi lùi - tiến để "farm" điểm thưởng.
- 🎯 **Khả năng tổng quát hóa (Zero-shot Generalization):** Sử dụng cơ chế quan sát cảm biến lân cận (Proximity Raycast Sensors + Vector hướng đích), cho phép robot tự điều hướng thành công trên các bản đồ hoàn toàn mới chưa từng học.
- ⚡ **Thả vật cản thời gian thực (Dynamic Obstacle Injection):** Cho phép người dùng click chuột thả chướng ngại vật ngay trước mũi robot trên Web để kiểm tra phản xạ né tránh tức thì.
- 🔋 **Ràng buộc Công nghiệp Thực tế (Battery & Docking Station):** Robot phải tự nhận thức mức năng lượng; khi pin $< 20\%$, robot tự định tuyến rẽ vào trạm sạc nạp điện trước khi tiếp tục giao hàng.
- 📦 **Model Artifact Registry chuẩn mực:** Mọi checkpoint xuất xưởng gồm cặp tệp `model.pt` + `metadata.json` mô tả đầy đủ kiến trúc, siêu tham số và chỉ số đánh giá, phục vụ nạp mô hình động (Dynamic Loading) không cần restart server.

---

## 🏗️ 3. KIẾN TRÚC HỆ THỐNG (SYSTEM ARCHITECTURE)

Hệ thống tuân thủ nguyên tắc **Tách biệt phân tầng (Decoupled Subsystems)**: Không chạy huấn luyện nặng trong web container; Backend chỉ đóng vai trò nạp model và mô phỏng suy luận.

```
+-----------------------------------------------------------------------------------------+
|                                TRAINING SUBSYSTEM                                       |
|  [Local CLI / Google Colab GPU Notebooks]                                               |
|  - Môi trường: WarehouseGridEnv (Gymnasium-compliant)                                   |
|  - Lõi AI: A* Search Baseline | Tabular Q-Learning | PyTorch Dueling Double DQN        |
|  - Multi-seed Evaluation Engine (3-5 seeds: Success Rate, Collision, Path Optimality)   |
|  ===> OUTPUT: Model Artifact Package (/models/{model_id}/model.pt + metadata.json)     |
+-----------------------------------------------------------------------------------------+
                                           |
                                           | Volume Mount / Artifact Registry
                                           v
+-----------------------------------------------------------------------------------------+
|                              SERVING & PLATFORM SUBSYSTEM                               |
|  [Docker Compose Orchestration - Single Command Startup]                                |
|                                                                                         |
|   +------------------------------------+       +------------------------------------+   |
|   |         FRONTEND CLIENT            |       |          BACKEND API               |   |
|   |  - React 18 + TypeScript + Vite    | <===> |  - FastAPI (Python 3.10+)          |   |
|   |  - HTML5 Canvas 2D Simulation (60fps)      |  - Dynamic Model Loader Service    |   |
|   |  - Agent Control Panel (Tick/Speed)| WSS / |  - Headless Simulation Loop Engine |   |
|   |  - Recharts Analytics Dashboard    | REST  |  - WebSocket Streaming Hub         |   |
|   +------------------------------------+       +------------------------------------+   |
|                                                                  |                      |
|                                                                  v                      |
|                                                +------------------------------------+   |
|                                                |         DATABASE LAYER             |   |
|                                                |  - PostgreSQL 15                   |   |
|                                                |  - Experiments, Models, Benchmarks |   |
|                                                +------------------------------------+   |
+-----------------------------------------------------------------------------------------+
```

---

## 🗺️ 4. LỘ TRÌNH PHÁT TRIỂN (ROADMAP)

Dự án được định hướng phát triển bài bản qua 3 phiên bản lớn:

```
[V1: SMART NAVIGATION (MVP)]  -->  [V2: AUTONOMOUS MOBILITY]  -->  [V3: INTELLIGENT ROBOTICS]
- 2D Discrete Grid World            - Continuous Motion (v, ω)      - 3D Physics (MuJoCo / Isaac)
- 4 Rời rạc: Up, Down, Left, Right  - Differential Drive Kinematics - Soft Actor-Critic (SAC)
- A* vs Q-Learning vs PyTorch DQN   - Virtual LiDAR Raycasting      - Domain Randomization
- Canvas 2D + FastAPI + Docker      - PPO (Actor-Critic) Engine     - Vision-based Navigation
```

### Chi tiết các Sprint của Phiên bản V1 (Hiện tại)

- [x] **Phase 0: System Design & Architecture Blueprint**
  - Phân tích Master Brief, chốt phạm vi MVP, ban hành 10 quyết định kiến trúc ([DECISION_LOG.md](DECISION_LOG.md)).
  - Thiết lập ma trận nhiệm vụ cho 7 AI Agents chuyên biệt ([AGENT_TASKS.md](AGENT_TASKS.md)).
- [ ] **Phase 1: Environment & Mathematical Core (Sprint 1)**
  - Xây dựng `WarehouseGridEnv` chuẩn Gymnasium API (`reset`, `step`, `render`, `close`).
  - Thiết kế bộ 3 bản đồ chuẩn: Easy ($10\times 10$), Medium ($15\times 15$), Hard ($20\times 20$).
  - Chuẩn hóa Potential-based Reward Shaping ($PBRS$) và không gian quan sát cảm biến lân cận.
- [ ] **Phase 2: Algorithms & Training Benchmark (Sprint 2)**
  - Triển khai thuật toán đối chuẩn $A^*$ Search.
  - Cài đặt Tabular Q-Learning và PyTorch Dueling Double DQN (MLP, Replay Buffer, Target Sync).
  - Pipeline huấn luyện Colab GPU / Local CLI và đóng gói Model Artifact.
- [ ] **Phase 3: Backend API & Data Persistence (Sprint 3)**
  - Xây dựng FastAPI service, REST API (`/api/v1/maps`, `/models`, `/experiments`).
  - WebSocket Server (`/ws/simulation/{session_id}`) truyền luồng tick thời gian thực.
  - Khởi tạo PostgreSQL schema DDL (lưu metadata, tách biệt weights binary).
- [ ] **Phase 4: Frontend Simulation Arena & Analytics (Sprint 4)**
  - Trực quan hóa đấu trường Canvas 2D siêu mượt 60 FPS.
  - Bảng điều khiển Agent Control (Play, Pause, Step-by-step, Slider tốc độ).
  - Dashboard phân tích biểu đồ học tập và đối chuẩn song song giữa $A^*$ và DQN.
- [ ] **Phase 5: Dockerization & E2E Validation (Sprint 5)**
  - Tối ưu Dockerfile cho Backend và Frontend.
  - Docker Compose 1-lệnh tích hợp: `backend`, `frontend`, `db`.
- [ ] **Phase 6: Multi-seed Benchmarks & Final Release (Sprint 6)**
  - Chạy kiểm thử tự động trên nhiều seed ngẫu nhiên ($Mean \pm Std$).
  - Xuất báo cáo khoa học `EVALUATION_REPORT.md` và nghiệm thu hoàn thành V1.

---

## 💻 5. CÔNG NGHỆ SỬ DỤNG (TECH STACK)

| Phân hệ | Công nghệ | Mục đích sử dụng |
| :--- | :--- | :--- |
| **Lõi AI / RL** | Python 3.10+, PyTorch, Gymnasium, NumPy | Xây dựng môi trường mô phỏng, mạng nơ-ron DQN, Replay Buffer. |
| **Thuật toán đối chuẩn** | A\* Search Algorithm, Manhattan Heuristic | Mốc đối chuẩn đường đi ngắn nhất tối ưu (Ground Truth). |
| **Backend API** | FastAPI, Uvicorn, WebSockets, Pydantic | Xử lý REST API, stream dữ liệu di chuyển từng tick theo thời gian thực. |
| **Cơ sở dữ liệu** | PostgreSQL 15, SQLAlchemy ORM, Alembic | Quản lý metadata mô hình, cấu hình thí nghiệm và kết quả đối chuẩn. |
| **Frontend UI** | React 18, TypeScript, Vite, HTML5 Canvas 2D | Render đấu trường mô phỏng 60 FPS, bảng điều khiển và dashboard phân tích. |
| **Thư viện Biểu đồ** | Recharts / Chart.js | Vẽ biểu đồ Episode Reward, Success Rate, Collision Rate. |
| **Hạ tầng / DevOps** | Docker, Docker Compose, GitHub Actions | Đóng gói ứng dụng đa dịch vụ, tự động hóa kiểm thử CI/CD. |

---

## 📂 6. CẤU TRÚC THƯ MỤC DỰ ÁN (PROJECT REPOSITORY STRUCTURE)

```
Robopilot/
├── .github/
│   └── workflows/              # CI/CD workflows (pytest, linting)
├── docs/                       # Tài liệu thiết kế kỹ thuật của các Agent
│   ├── RL_RESEARCH.md          # Nghiên cứu thuật toán RL (Agent 1)
│   ├── REWARD_DESIGN.md        # Thiết kế hàm thưởng & PBRS (Agent 1)
│   ├── ENVIRONMENT_SPEC.md     # Đặc tả môi trường Gymnasium (Agent 2)
│   ├── TRAINING_PIPELINE.md    # Đặc tả pipeline huấn luyện (Agent 3)
│   ├── BACKEND_DESIGN.md       # Thiết kế kiến trúc Backend (Agent 4)
│   ├── UI_UX_SPEC.md           # Thiết kế giao diện & Canvas (Agent 5)
│   └── ACCEPTANCE_CRITERIA.md  # Tiêu chí nghiệm thu (Agent 6)
├── maps/                       # Bộ bản đồ chuẩn (Benchmark JSON Maps)
│   ├── benchmark_easy_10x10.json
│   ├── benchmark_medium_15x15.json
│   └── benchmark_hard_20x20.json
├── models/                     # Thư mục lưu Model Artifacts (Mounted Volume)
│   └── dqn_v1_example/
│       ├── model.pt            # Trọng số mạng PyTorch
│       └── metadata.json       # Siêu dữ liệu kiến trúc & siêu tham số
├── src/                        # Mã nguồn ứng dụng (Bắt đầu ở Development Phase)
│   ├── ai_core/                # Module AI độc lập: Gym Env, A*, Q-Learning, DQN
│   ├── backend/                # FastAPI application, Routers, Services, DB Models
│   └── frontend/               # React 18 + Vite TypeScript application, Canvas 2D
├── docker-compose.yml          # Triển khai 1-lệnh Backend + Frontend + PostgreSQL
├── PROJECT_OVERVIEW.md         # Tổng quan dự án, sứ mệnh và phân tầng kiến trúc
├── PROJECT_SCOPE.md            # Đặc tả phạm vi V1, ranh giới In/Out of Scope
├── ROADMAP.md                  # Lộ trình phát triển chi tiết từng giai đoạn
├── SYSTEM_ARCHITECTURE.md      # Đặc tả kiến trúc tổng thể & 11 Technical Contracts
├── COMPONENT_DIAGRAM.md        # Sơ đồ khối thành phần Mermaid
├── DATA_FLOW.md                # Biểu đồ trình tự luồng dữ liệu (Sequence Diagrams)
├── DECISION_LOG.md             # Nhật ký quyết định kiến trúc (ADR-001 -> ADR-010)
├── AGENT_TASKS.md              # Bảng phân công nhiệm vụ và hợp đồng giao tiếp 7 Agents
├── .gitignore                  # Cấu hình bỏ qua tệp môi trường và binary
└── README.md                   # Tài liệu giới thiệu chính của dự án
```

---

## 👥 7. MÔ HÌNH VẬN HÀNH 7 CHUYÊN GIA AI (7-AGENT GOVERNANCE)

Dự án được điều phối và thiết kế bởi đội ngũ 7 AI Agents chuyên biệt tuân thủ nghiêm ngặt nguyên tắc **Design-First** và **Contract-Driven**:

| Agent | Vai trò chuyên biệt | Phạm vi phụ trách chính |
| :---: | :--- | :--- |
| **Agent 0** | **Project Orchestrator & System Architect** | Quản lý tiến độ tổng thể, phân công công việc, kiểm soát scope, giải quyết xung đột hợp đồng ([AGENT_TASKS.md](AGENT_TASKS.md)). |
| **Agent 1** | **Robotics & RL Research Specialist** | Nghiên cứu lý thuyết RL, mô hình MDP, hàm thưởng PBRS chống Reward Hacking. |
| **Agent 2** | **Simulation & Environment Designer** | Thiết kế môi trường Warehouse 2D chuẩn Gymnasium, hệ tọa độ ma trận, cơ chế phát hiện va chạm. |
| **Agent 3** | **ML/RL Engineer & Training Architect** | Thiết kế kiến trúc mạng PyTorch DQN, Replay Buffer, pipeline Colab và xuất Model Artifact. |
| **Agent 4** | **Backend & MLOps Architect** | Thiết kế Backend FastAPI, WebSocket stream, dynamic model loader, PostgreSQL DDL, Docker Compose. |
| **Agent 5** | **Frontend & UX/UI Designer** | Thiết kế giao diện React 18 Canvas 2D 60 FPS, Agent Control, Analytics Dashboard 5 modules. |
| **Agent 6** | **QA & Research Validation Specialist** | Kiểm định độc lập, rà soát 11 hợp đồng kỹ thuật, kiểm tra nguy cơ overfitting, lập kế hoạch test. |

---

## 🚀 8. HƯỚNG DẪN KHỞI CHẠY NHANH (QUICKSTART)

*(Áp dụng khi dự án hoàn thành giai đoạn Design và chuyển sang Development Phase)*

### Cách 1: Khởi chạy 1-Lệnh bằng Docker Compose (Khuyến nghị)
```bash
# 1. Clone repository từ GitHub
git clone https://github.com/HieuTran2901/Robopilot.git
cd Robopilot

# 2. Khởi chạy toàn bộ hệ thống bằng Docker Compose
docker compose up --build
```
- **Frontend Dashboard:** Mở trình duyệt tại `http://localhost:3000`
- **Backend API & Swagger Docs:** Truy cập `http://localhost:8000/docs`
- **PostgreSQL Database:** Hoạt động tại cổng `localhost:5432`

### Cách 2: Chạy độc lập Module Huấn luyện AI (Local CLI / Colab)
```bash
# Huấn luyện mô hình DQN trên bản đồ chuẩn 10x10 với seed 42
python -m src.ai_core.train --algorithm DQN --map maps/benchmark_easy_10x10.json --episodes 1000 --seed 42

# Đánh giá đối chuẩn mô hình đã train với A* Search
python -m src.ai_core.evaluate --model models/dqn_v1_easy/model.pt --compare-astar
```

---

## 📄 9. BẢN QUYỀN VÀ ĐÓNG GÓP (LICENSE & CONTRIBUTING)

- Dự án được phát hành theo giấy phép mã nguồn mở **MIT License**.
- Tác giả: **Trần Trung Hiếu** ([@HieuTran2901](https://github.com/HieuTran2901)) cùng đội ngũ **RoboPilot AI Agents**.
- Mọi đóng góp, báo cáo lỗi và đề xuất cải tiến xin vui lòng mở [Issue](https://github.com/HieuTran2901/Robopilot/issues) hoặc tạo [Pull Request](https://github.com/HieuTran2901/Robopilot/pulls) tại repository chính thức.

<div align="center">
  <sub>Built with ❤️ for Autonomous Robotics & Reinforcement Learning Research</sub>
</div>
