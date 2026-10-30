# ROBOPILOT — DATA FLOW & SEQUENCE SPECIFICATION
# LUỒNG DỮ LIỆU VÀ TRÌNH TỰ TƯƠNG TÁC HỆ THỐNG

> **Tài liệu thuộc trách nhiệm:** Agent 0 (Project Orchestrator & System Architect)  
> **Trạng thái:** DRAFT / DESIGN PHASE  
> **Ngày ban hành:** 2026-10-29  

---

## 1. TỔNG QUAN VÒNG ĐỜI DỮ LIỆU (DATA LIFECYCLE)

Dữ liệu trong RoboPilot di chuyển qua 3 luồng chính:
1. **Luồng Huấn luyện & Đóng gói (Training & Packaging Flow):** Trạng thái tương tác giữa Agent RL và Môi trường Gymnasium $\rightarrow$ Cập nhật trọng số $\rightarrow$ Xuất tệp nhị phân và `metadata.json`.
2. **Luồng Điều khiển & Mô phỏng Thời gian thực (Real-Time Simulation Flow):** Lệnh từ Frontend $\rightarrow$ WebSocket Backend $\rightarrow$ Nạp Model $\rightarrow$ Suy luận bước đi $\rightarrow$ Stream khung dữ liệu Tick $\rightarrow$ Vẽ Canvas 2D.
3. **Luồng Đối chuẩn & Phân tích (Benchmark & Analytics Flow):** Kết quả chạy A* và RL $\rightarrow$ REST API $\rightarrow$ PostgreSQL $\rightarrow$ Biểu đồ so sánh trên Dashboard.

---

## 2. CÁC BIỂU ĐỒ TRÌNH TỰ (SEQUENCE DIAGRAMS)

### 2.1. Luồng 1: Huấn luyện và Đóng gói Mô hình (Offline Training Pipeline)

```mermaid
sequenceDiagram
    autonumber
    actor Developer as Researcher / Intern
    participant Colab as Training Script (Local / Colab)
    participant Env as WarehouseGridEnv (Agent 2)
    participant Agent as PyTorch DQN Agent (Agent 3)
    participant Reward as PBRS Engine (Agent 1)
    participant Registry as Model Artifact Store (/models)

    Developer->>Colab: Khởi chạy lệnh train (config, seed, episodes)
    Colab->>Env: reset(seed)
    Env-->>Colab: Trả về obs_0 ban đầu
    
    loop Mỗi Episode (Max N steps)
        Colab->>Agent: select_action(obs_t, epsilon)
        Agent-->>Colab: action_t
        Colab->>Env: step(action_t)
        Env->>Reward: compute_reward(s_t, action_t, s_next)
        Reward-->>Env: reward_t
        Env-->>Colab: obs_next, reward_t, terminated, truncated, info
        Colab->>Agent: store_transition(obs_t, action_t, reward_t, obs_next, done)
        Colab->>Agent: update_parameters(batch_size)
    end

    Developer->>Colab: Hoàn thành huấn luyện & Đánh giá (Evaluation)
    Colab->>Agent: serialize_weights() -> model.pt
    Colab->>Registry: Ghi tệp weights: /models/{model_id}/model.pt
    Colab->>Registry: Ghi tệp metadata: /models/{model_id}/metadata.json
```

---

### 2.2. Luồng 2: Mô phỏng Thời gian thực (Live Simulation Streaming via WebSocket)

```mermaid
sequenceDiagram
    autonumber
    actor User as Người dùng
    participant UI as Frontend React / Canvas (Agent 5)
    participant WS as WebSocket Hub (Agent 4)
    participant Sim as Simulation Engine (Agent 4)
    participant Model as Loaded Model (Inference Mode)
    participant DB as PostgreSQL (Agent 4)

    User->>UI: Chọn Map (15x15) & Model (DQN_v1), nhấn "Play"
    UI->>WS: Gửi ws://.../ws/simulation/session_123
    WS-->>UI: WebSocket Connected (Session Ready)
    
    UI->>WS: Send COMMAND: {"command": "START", "model_id": "dqn_v1", "speed": 10}
    WS->>Sim: init_simulation(map_id, model_id)
    Sim->>Model: verify_and_load(model_id)
    Model-->>Sim: Ready (in evaluation mode)
    
    loop Chu kỳ Tick (Tùy theo speed slider, ví dụ 10 Hz)
        Sim->>Model: predict_action(current_obs)
        Model-->>Sim: selected_action, q_values
        Sim->>Sim: step_environment(selected_action)
        Sim-->>WS: emit_tick(robot_pos, reward, q_values, is_collision, is_done)
        WS-->>UI: Send JSON TICK frame
        UI->>UI: Canvas 2D render robot, path trail, obstacle hit
    end

    alt Robot đến Goal hoặc Va chạm
        Sim-->>WS: emit_tick(status: FINISHED, total_steps, total_reward)
        WS-->>UI: Thông báo hoàn thành & Hiển thị kết quả
        Sim->>DB: Ghi log phiên chạy vào bảng simulation_logs
    end
```

---

### 2.3. Luồng 3: Đối chuẩn Thuật toán (A* vs RL Benchmark Comparison)

```mermaid
sequenceDiagram
    autonumber
    actor User as Người dùng
    participant UI as Analytics Dashboard (Agent 5)
    participant API as Backend REST API (Agent 4)
    participant AStar as A* Baseline Module (Agent 1)
    participant RL as DQN Inference Engine (Agent 4)
    participant DB as PostgreSQL Database

    User->>UI: Nhấn "Run Comparative Benchmark" trên Map đã chọn
    UI->>API: POST /api/v1/benchmarks/run {"map_id": "med_15x15", "model_id": "dqn_v1"}
    
    API->>AStar: compute_shortest_path(map_grid)
    AStar-->>API: astar_path, astar_steps, astar_time_ms
    
    API->>RL: run_evaluation_episodes(episodes=10)
    RL-->>API: rl_avg_steps, rl_success_rate, rl_collision_rate
    
    API->>DB: INSERT INTO benchmark_runs (astar_metrics, rl_metrics, ratio)
    DB-->>API: OK (Saved with run_id)
    
    API-->>UI: 200 OK: Trả về kết quả JSON so sánh
    UI->>UI: Hiển thị biểu đồ cột đối chuẩn (A* vs DQN: Path Length, Time, Success)
```

---

## 3. ĐẶC TẢ CẤU TRÚC DỮ LIỆU KHUNG TRUYỀN (DATA CONTRACT SCHEMAS)

### 3.1. Khung dữ liệu Tick thời gian thực (Server $\rightarrow$ Client)
```json
{
  "type": "SIM_TICK",
  "session_id": "sess_88294a",
  "step_index": 12,
  "data": {
    "robot_coordinates": {
      "x": 4,
      "y": 6,
      "heading": "RIGHT"
    },
    "goal_coordinates": {
      "x": 13,
      "y": 13
    },
    "action_taken": {
      "action_code": 3,
      "action_label": "RIGHT"
    },
    "q_values": [0.12, -0.45, 0.05, 0.89],
    "step_reward": -0.5,
    "cumulative_reward": 8.5,
    "flags": {
      "is_collision": false,
      "is_goal_reached": false,
      "is_timeout": false
    }
  }
}
```

### 3.2. Khung lệnh điều khiển mô phỏng (Client $\rightarrow$ Server)
```json
{
  "type": "SIM_COMMAND",
  "command": "SET_SPEED", // Các lệnh hỗ trợ: START, PAUSE, RESUME, RESET, STEP, SET_SPEED
  "payload": {
    "ticks_per_second": 15
  }
}
```

---

## 4. TÍNH BẢO MẬT VÀ TOÀN VẸN DỮ LIỆU
1. **Xác thực cấu trúc tệp:** Tệp `metadata.json` phải được kiểm tra schema nghiêm ngặt trước khi Backend cấp phát vùng nhớ nạp tệp `model.pt`.
2. **Kiểm tra biên an toàn (Safety Bounds):** Tọa độ robot nhận từ bất kỳ engine nào cũng được validate không vượt quá kích thước $W \times H$ của bản đồ.
3. **Session Isolation:** Mỗi kết nối WebSocket gắn với một `session_id` độc lập trên Backend, đảm bảo nhiều tab trình duyệt không làm nhiễu loạn trạng thái mô phỏng của nhau.
