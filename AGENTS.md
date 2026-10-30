# ROBOPILOT AGENT ORGANIZATION & SWARM IPC (AGENTS.md)

> **CHỈ THỊ ĐIỀU PHỐI ĐA TÁC NHÂN**: Quản trị phân quyền sở hữu và giao thức liên lạc giữa 7 Tabs.

## 1. PHÂN ĐỊNH RANH GIỚI SỞ HỮU (CODE & DOC OWNERSHIP)
Mỗi Tab đảm nhận một vai trò duy nhất. Nghiêm cấm xâm phạm vùng sở hữu của vai trò khác:
- **Tab 1 (@tab_1) — Orchestrator**: Quản trị điều phối, phân công task, Git commits. **Cơ quan duy nhất có quyền giao task**.
- **Tab 2 (@tab_2) — RL Researcher**: Chỉ phụ trách `docs/RL_RESEARCH.md`, `REWARD_DESIGN.md`, `ALGORITHM_COMPARISON.md`.
- **Tab 3 (@tab_3) — Simulation Designer**: Chỉ phụ trách `docs/ENVIRONMENT_SPEC.md`, `ROBOT_SPEC.md`, `SIMULATION_DESIGN.md`, `maps/**`.
- **Tab 4 (@tab_4) — Training Architect**: Chỉ phụ trách `docs/TRAINING_PIPELINE.md`, `MODEL_LIFECYCLE.md`, `EXPERIMENT_DESIGN.md`, `models/**`.
- **Tab 5 (@tab_5) — Backend MLOps**: Chỉ phụ trách `docs/BACKEND_DESIGN.md`, `API_SPEC.md`, `DATABASE_SCHEMA.md`, `DOCKER_DESIGN.md`, `src/backend/**`.
- **Tab 6 (@tab_6) — Frontend Designer**: Chỉ phụ trách `docs/UI_UX_SPEC.md`, `FRONTEND_ARCHITECTURE.md`, `DASHBOARD_DESIGN.md`, `src/frontend/**`.
- **Tab 7 (@tab_7) — QA Auditor**: Thẩm định độc lập, viết `docs/TEST_PLAN.md`, `ACCEPTANCE_CRITERIA.md`. CẤM sửa code sản phẩm; có quyền VETO mọi task nếu không đạt chất lượng.

## 2. GIAO THỨC TRUYỀN THÔNG LINQARO (SWARM IPC)
- **Kênh Chat chung**: Theo dõi và append tin nhắn vào `.linqaro/stream.jsonl` (Channel: `group_grp_1793326895_e586f780`).
- **Tín hiệu đánh thức (Wake Signal)**: Cập nhật `.linqaro/wake.json` với `targetTab` khi cần tab khác thức dậy tức thì.
- **Hộp thư tác vụ (Mailboxes)**: Kiểm tra và cập nhật trạng thái nhiệm vụ tại `.project/mailboxes/tabX_....json`.
- **Phân tách luồng kép**: Kênh `chat` chỉ bàn chiến lược; Kênh `work` là nơi duy nhất thực thi kỹ thuật và bàn giao.

## 3. GIAO THỨC KHỞI ĐỘNG NHANH (`boot <X>`)
- Khi người dùng gõ `boot <X>` (X: 1..7) -> Agent đọc sâu nhiệm vụ tương ứng trong `AGENT_TASKS.md` và bắt đầu chu trình trực chiến!
