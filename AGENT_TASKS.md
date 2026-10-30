# ROBOPILOT — 7-AGENT TASK MATRIX & CONTRACT REGISTRY
# PHÂN CÔNG NHIỆM VỤ CHI TIẾT VÀ QUẢN LÝ HỢP ĐỒNG 7 AGENTS

> **Cơ quan quản lý:** Agent 0 (Project Orchestrator & System Architect)  
> **Giai đoạn:** DESIGN PHASE (Nghiêm cấm viết code sản phẩm, không cài dependencies)  
> **Cập nhật lần cuối:** 2026-10-29  

---

## 1. NGUYÊN TẮC HOẠT ĐỘNG VÀ BÁO CÁO CỦA 7 AGENTS

### 1.1. Nguyên tắc cốt lõi
1. **Tuân thủ Master Project Brief:** Tài liệu định hướng tối cao của dự án.
2. **Quyền sở hữu tài liệu độc quyền (Single Source of Truth):** Mỗi tài liệu chỉ do 1 Agent sở hữu và chịu trách nhiệm chỉnh sửa chính. Các agent khác phản biện thông qua trao đổi và đề xuất, không tự ý ghi đè.
3. **Thống nhất hợp đồng trước khi code (Contract-First):** Phải hoàn thành và chốt toàn bộ 11 hợp đồng kỹ thuật trong Design Phase trước khi chuyển sang Development Phase.
4. **Trung thực về dữ liệu khoa học:** Tuyệt đối không tự bịa đặt hoặc tạo số liệu thực nghiệm RL giả.
5. **Đơn giản hóa cho MVP:** Phù hợp với năng lực triển khai thực tế của AI/ML Intern, không đưa các thành phần microservices hay 3D phức tạp vào V1.

### 1.2. Mẫu báo cáo hoàn thành nhiệm vụ bắt buộc (Reporting Template)
Mỗi agent khi hoàn thành hạng mục thiết kế phải gửi báo cáo theo cấu trúc 9 phần:
- **Summary:** Tóm tắt ngắn gọn kết quả đạt được.
- **Completed Tasks:** Danh sách công việc đã hoàn thành.
- **Decisions:** Các quyết định kỹ thuật kèm trạng thái (PROPOSED / APPROVED / REJECTED / BLOCKED).
- **Assumptions:** Các giả định kỹ thuật đang áp dụng.
- **Dependencies:** Phụ thuộc vào đầu ra của agent nào.
- **Risks:** Rủi ro kỹ thuật, toán học hoặc kiến trúc phát hiện được.
- **Conflicts:** Các điểm chưa thống nhất với agent khác.
- **Open Questions:** Những vấn đề cần Agent 0 hoặc Người dùng làm rõ.
- **Deliverables:** Danh sách tệp tài liệu đã tạo hoặc cập nhật.

---

## 2. MA TRẬN NHIỆM VỤ CHI TIẾT 7 AGENTS (DESIGN PHASE)

```
                               +-------------------------------+
                               |            AGENT 0            |
                               | (Lead Orchestrator/Architect) |
                               +-------------------------------+
                                               |
         +-------------------+-----------------+-------------------+-------------------+
         |                   |                 |                   |                   |
         v                   v                 v                   v                   v
+-----------------+ +-----------------+ +-----------------+ +-----------------+ +-----------------+
|     AGENT 1     | |     AGENT 2     | |     AGENT 3     | |     AGENT 4     | |     AGENT 5     |
| (RL Research)   | | (Simulation)    | | (ML/RL Training)| | (Backend/MLOps) | | (Frontend/UI)   |
+-----------------+ +-----------------+ +-----------------+ +-----------------+ +-----------------+
         ^                   ^                 ^                   ^                   ^
         |                   |                 |                   |                   |
         +-------------------+-----------------+-------------------+-------------------+
                                               |
                                               v
                               +-------------------------------+
                               |            AGENT 6            |
                               |   (QA & Research Validation)  |
                               +-------------------------------+
```

---

### AGENT 0: PROJECT ORCHESTRATOR & SYSTEM ARCHITECT
- **Trách nhiệm:** Quản lý tiến độ, kiến trúc tổng thể, kiểm soát scope, giải quyết xung đột hợp đồng.
- **Tài liệu phụ trách:**
  - `PROJECT_OVERVIEW.md`
  - `PROJECT_SCOPE.md`
  - `ROADMAP.md`
  - `SYSTEM_ARCHITECTURE.md`
  - `COMPONENT_DIAGRAM.md`
  - `DATA_FLOW.md`
  - `DECISION_LOG.md`
- **Tiêu chí hoàn thành:** Bộ hồ sơ kiến trúc đồng bộ, các agent hiểu rõ ranh giới và interface kết nối được với nhau.

---

### AGENT 1: ROBOTICS & RL RESEARCH SPECIALIST
- **Trách nhiệm:** Nghiên cứu lý thuyết RL, mô hình toán học MDP, thuật toán (A*, Q-Learning, DQN, PPO, SAC), thiết kế hàm thưởng (Potential-based Reward Shaping) và ngăn chặn Reward Hacking.
- **Tài liệu phụ trách:**
  - `docs/RL_RESEARCH.md` (Cơ chế MDP, Bellman equation, trade-offs)
  - `docs/ALGORITHM_COMPARISON.md` (Phân tích chi tiết A* vs Q-Learning vs DQN vs PPO/SAC)
  - `docs/REWARD_DESIGN.md` (Công thức hàm thưởng, toán học PBRS, chống cycling)
- **Tiêu chí hoàn thành:** Thiết kế RL có cơ sở toán học vững chắc, giải quyết triệt để rủi ro reward hacking cho MVP.

---

### AGENT 2: SIMULATION & ENVIRONMENT DESIGNER
- **Trách nhiệm:** Thiết kế môi trường Warehouse 2D tuân thủ chuẩn Gymnasium API (`reset`, `step`, `render`, `close`), hệ tọa độ ma trận, cơ chế phát hiện va chạm, điều kiện dừng, và 3 bản đồ chuẩn.
- **Tài liệu phụ trách:**
  - `docs/ENVIRONMENT_SPEC.md` (Gymnasium API spec, map representation, coordinate convention)
  - `docs/ROBOT_SPEC.md` (Vị trí, hướng nhìn, tốc độ, trạng thái va chạm)
  - `docs/STATE_ACTION_SPEC.md` (Đặc tả 4 Actions rời rạc và 2 Observation Modes)
  - `docs/SIMULATION_DESIGN.md` (Quy tắc di chuyển, va chạm, tạo bản đồ ngẫu nhiên/cố định)
- **Tiêu chí hoàn thành:** Đặc tả môi trường mô phỏng chi tiết, logic va chạm rõ ràng, tương thích 100% với Agent 1 và Agent 3.

---

### AGENT 3: ML/RL ENGINEER & TRAINING ARCHITECT
- **Trách nhiệm:** Thiết kế pipeline huấn luyện RL, kiến trúc mạng PyTorch DQN (MLP, Replay Buffer, Target Network), quy trình huấn luyện Colab GPU/Local, cơ chế lưu checkpoint, quy trình đánh giá multi-seed và chuẩn hóa Model Artifact Package.
- **Tài liệu phụ trách:**
  - `docs/TRAINING_PIPELINE.md` (Quy trình huấn luyện Local/Colab, GPU acceleration, loop training)
  - `docs/MODEL_LIFECYCLE.md` (Checkpointing, serialization, Model Artifact Specification)
  - `docs/EXPERIMENT_DESIGN.md` (Kế hoạch thí nghiệm, hyperparameter search, multi-seed protocol)
- **Tiêu chí hoàn thành:** Pipeline huấn luyện có tính tái lập cao, cơ chế lưu trữ và bàn giao model sang Backend rõ ràng.

---

### AGENT 4: BACKEND & MLOPS ARCHITECT
- **Trách nhiệm:** Thiết kế Backend FastAPI, REST API endpoints, WebSocket server stream dữ liệu thời gian thực (`/ws/simulation`), Dynamic Model Loader, PostgreSQL schema DDL, lưu trữ nhị phân ngoài DB, Docker Compose configuration.
- **Tài liệu phụ trách:**
  - `docs/BACKEND_DESIGN.md` (Kiến trúc FastAPI, modular service layer, dependency injection)
  - `docs/API_SPEC.md` (Đặc tả REST OpenAPI & WebSocket frame protocol)
  - `docs/DATABASE_SCHEMA.md` (PostgreSQL ERD & SQL DDL cho maps, experiments, models, runs)
  - `docs/DOCKER_DESIGN.md` (Dockerfile cho backend/frontend, docker-compose.yml, volume mounts)
- **Tiêu chí hoàn thành:** Kiến trúc backend hoàn chỉnh, API nhất quán, database chuẩn mực, khởi chạy 1-lệnh bằng Docker.

---

### AGENT 5: FRONTEND & UX/UI DESIGNER
- **Trách nhiệm:** Thiết kế ứng dụng React 18 TypeScript Vite, Simulation Arena bằng HTML5 Canvas 2D (60 FPS), thanh điều khiển Agent Control, Dashboard phân tích 5 modules, quản lý kết nối WebSocket client.
- **Tài liệu phụ trách:**
  - `docs/UI_UX_SPEC.md` (Design system, wireframe 5 modules, visual styles, error/loading states)
  - `docs/FRONTEND_ARCHITECTURE.md` (React component hierarchy, state management, custom hooks)
  - `docs/DASHBOARD_DESIGN.md` (Thiết kế biểu đồ Recharts, bảng đối chuẩn A* vs RL)
- **Tiêu chí hoàn thành:** Giao diện trực quan, hiện đại, Canvas 2D phản ánh chính xác trạng thái vật lý từ simulation backend.

---

### AGENT 6: QA & RESEARCH VALIDATION SPECIALIST
- **Trách nhiệm:** Kiểm định độc lập toàn bộ thiết kế, phát hiện mâu thuẫn giữa 11 hợp đồng kỹ thuật, xây dựng kịch bản kiểm thử mô phỏng/API/Docker, kiểm tra rủi ro Reward Hacking/Overfitting, thiết lập Acceptance Criteria định lượng.
- **Tài liệu phụ trách:**
  - `docs/TEST_PLAN.md` (Kế hoạch kiểm thử Environment, logic va chạm, API, WebSocket, Docker)
  - `docs/EVALUATION_PLAN.md` (Phương pháp đánh giá thuật toán RL, thống kê đa hạt nhân, so sánh A*)
  - `docs/ACCEPTANCE_CRITERIA.md` (Bộ tiêu chí nghiệm thu định lượng MVP)
- **Tiêu chí hoàn thành:** Bản kế hoạch thẩm định chất lượng toàn diện, đảm bảo sản phẩm có thể kiểm chứng bằng thực nghiệm khoa học.

---

## 3. DANH MỤC 11 HỢP ĐỒNG KỸ THUẬT VÀ CÁC BÊN LIÊN QUAN

| Hợp đồng Kỹ thuật (Technical Contract) | Agent Phụ trách chính | Các Agent Đồng thuận / Tiêu thụ |
| :--- | :--- | :--- |
| **1. Observation Space Contract** | Agent 2 | Agent 1, Agent 3, Agent 4 |
| **2. Action Space Contract** | Agent 2 | Agent 1, Agent 3, Agent 4, Agent 5 |
| **3. Reward Function Contract** | Agent 1 | Agent 2, Agent 3, Agent 6 |
| **4. Environment API Contract** | Agent 2 | Agent 1, Agent 3, Agent 6 |
| **5. Training Pipeline Contract** | Agent 3 | Agent 1, Agent 4, Agent 6 |
| **6. Model Artifact Contract** | Agent 3 | Agent 4, Agent 0 |
| **7. Backend REST API Contract** | Agent 4 | Agent 5, Agent 0 |
| **8. Database Schema Contract** | Agent 4 | Agent 0, Agent 6 |
| **9. Frontend Data Contract (WebSocket)** | Agent 4 | Agent 5, Agent 2 |
| **10. Evaluation Metrics Contract** | Agent 1 | Agent 3, Agent 6, Agent 0 |
| **11. Docker Service Contract** | Agent 4 | Agent 0, Agent 6 |
