# ROBOPILOT — COMPONENT DIAGRAM SPECIFICATION
# SƠ ĐỒ THÀNH PHẦN HỆ THỐNG VÀ QUAN HỆ TƯƠNG TÁC

> **Tài liệu thuộc trách nhiệm:** Agent 0 (Project Orchestrator & System Architect)  
> **Trạng thái:** DRAFT / DESIGN PHASE  
> **Ngày ban hành:** 2026-10-29  

---

## 1. SƠ ĐỒ THÀNH PHẦN TỔNG THỂ (SYSTEM COMPONENT DIAGRAM)

Biểu đồ dưới đây mô tả mối quan hệ, ranh giới và giao thức kết nối giữa các khối thành phần trong toàn bộ hệ sinh thái RoboPilot V1:

```mermaid
flowchart TD
    subgraph Offline_Training ["TRAINING ECOSYSTEM (Local / Colab)"]
        A1_Math["Agent 1: Mathematical Formulations\n(MDP, Reward Shaping, PBRS)"]
        A2_Env["Agent 2: Gymnasium Environment\n(WarehouseGridEnv-v0)"]
        A3_Engine["Agent 3: Training Engine\n(PyTorch DQN, ReplayBuffer, Q-Learn)"]
        A3_Exporter["Agent 3: Artifact Exporter\n(Weights & metadata.json)"]
        
        A1_Math --> A2_Env
        A2_Env --> A3_Engine
        A3_Engine --> A3_Exporter
    end

    subgraph Storage_Layer ["PERSISTENCE & MODEL REGISTRY"]
        Model_Dir[("/models Directory (Volume Mount)\nmodel.pt + metadata.json")]
        Map_Dir[("/maps Directory\nBenchmark JSON Maps")]
        Postgres_DB[("PostgreSQL 15 Database\nMetadata, Runs, Experiments")]
    end

    subgraph Backend_Service ["BACKEND SUBSYSTEM (FastAPI - Port 8000)"]
        Model_Loader["Agent 4: Dynamic Model Loader\n(Artifact Validator & PyTorch Eval)"]
        Sim_Engine["Agent 4: Headless Sim Engine\n(Step loop, Tick controller)"]
        WS_Manager["Agent 4: WebSocket Hub\n(/ws/simulation/{session_id})"]
        REST_Router["Agent 4: REST API Router\n(/api/v1/maps, models, experiments)"]
        DB_Adapter["Agent 4: SQLAlchemy ORM Adapter"]
        
        Model_Loader --> Sim_Engine
        Sim_Engine --> WS_Manager
        DB_Adapter --> Postgres_DB
    end

    subgraph Frontend_Service ["FRONTEND SUBSYSTEM (React 18 Vite - Port 3000)"]
        Arena["Agent 5: Simulation Arena\n(HTML5 Canvas 2D Engine)"]
        Control_Panel["Agent 5: Agent Control Panel\n(Play, Pause, Step, Speed Slider)"]
        Analytics_Dash["Agent 5: Analytics Dashboard\n(Recharts Reward & Success Curves)"]
        Model_Map_UI["Agent 5: Model & Map Manager\n(Select, Upload, Inspect)"]
        WS_Client["Agent 5: WebSocket Client Manager\n(Auto-reconnect, Tick parser)"]
    end

    subgraph QA_Validation ["QA & AUDIT (Cross-Cutting)"]
        A6_QA["Agent 6: QA & Research Validation\n(Test Plans, Verification Matrices)"]
    end

    %% Flow connections
    A3_Exporter -->|Writes Artifacts| Model_Dir
    Model_Dir -->|Read on Start / Dynamic Load| Model_Loader
    Map_Dir -->|Load Benchmark Maps| REST_Router
    
    WS_Client <-->|WebSocket Stream Tick & Commands| WS_Manager
    Control_Panel --> WS_Client
    WS_Client --> Arena
    
    REST_Router <-->|HTTP REST JSON| Analytics_Dash
    REST_Router <-->|HTTP REST JSON| Model_Map_UI
    
    A6_QA -.->|Audits & Verifies| Offline_Training
    A6_QA -.->|Audits & Verifies| Backend_Service
    A6_QA -.->|Audits & Verifies| Frontend_Service
```

---

## 2. CHI TIẾT TỪNG THÀNH PHẦN KỸ THUẬT

### 2.1. Nhóm thành phần Training (Agent 1, Agent 2, Agent 3)
- **`WarehouseGridEnv` (Gymnasium Core):** Cung cấp không gian trạng thái, ma trận bản đồ tĩnh và hàm chuyển trạng thái $s_{t+1} \sim \mathcal{P}(s_{t+1} \mid s_t, a_t)$.
- **`PBRS Engine` (Reward Shaping):** Tính toán phần thưởng tức thời $r_t$ và giá trị định hướng tiềm năng $F(s_t, s_{t+1}) = \gamma \Phi(s_{t+1}) - \Phi(s_t)$, loại bỏ hiện tượng đi lặp vòng tròn.
- **`PyTorch DQN Engine`:** Chứa mạng nơ-ron đánh giá $Q_\theta(s, a)$, mạng mục tiêu $Q_{\theta^-}(s, a)$, bộ nhớ đệm Replay Buffer với dung lượng $50,000$ mẫu, và bộ tối ưu hóa Adam.
- **`Model Artifact Exporter`:** Tự động tạo cấu trúc thư mục chứa tệp nhị phân (`model.pt`) và tệp siêu dữ liệu (`metadata.json`).

### 2.2. Nhóm thành phần Backend & Persistence (Agent 4)
- **`Dynamic Model Loader`:** Đọc tệp `metadata.json`, xác thực kiến trúc mạng (số layers, hidden units, observation dimension), sau đó nạp `model.pt` vào bộ nhớ RAM ở chế độ suy luận (`torch.no_grad()`).
- **`Headless Simulation Engine`:** Bản sao nhẹ của môi trường mô phỏng trên backend, tiếp nhận hành động từ model suy luận, cập nhật tọa độ robot và kiểm tra điều kiện kết thúc.
- **`WebSocket Connection Hub`:** Điều phối kết nối hai chiều với frontend, nhận lệnh điều khiển và phát luồng dữ liệu từng bước di chuyển (Tick DTO).
- **`PostgreSQL Database`:** Quản lý dữ liệu quan hệ gồm 4 thực thể chính: `maps`, `models`, `experiments`, `benchmark_runs`.

### 2.3. Nhóm thành phần Frontend (Agent 5)
- **`Canvas 2D Simulation Arena`:** Thành phần trung tâm vẽ bản đồ, lưới ô vuông, kệ hàng vật cản, robot kèm hướng nhìn, vệt đường đi đã đi qua (trajectory) và hiệu ứng va chạm tại tọa độ xảy ra sự cố.
- **`Agent Control Panel`:** Thanh điều khiển trực quan gồm các nút Play, Pause, Resume, Step (bước từng tick) và thanh trượt Ticks Per Second ($1 - 20$ Hz).
- **`Analytics Dashboard`:** Trực quan hóa các chỉ số thống kê từ các đợt huấn luyện và chạy thử nghiệm (Reward, Success Rate, Collision Rate, Steps to Goal).
- **`WebSocket Client Manager`:** Quản lý vòng đời kết nối socket, tự động bắt tay (handshake), lắng nghe dữ liệu và giải mã frame trạng thái để kích hoạt render trên Canvas.

### 2.4. Khối Đảm bảo Chất lượng & Độc lập Thẩm định (Agent 6)
- Đóng vai trò xuyên suốt (Cross-cutting concern), thực hiện rà soát độc lập các hợp đồng giao tiếp giữa các thành phần, giám sát rủi ro kỹ thuật và xây dựng kế hoạch kiểm thử tự động.
