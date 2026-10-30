# ROBOPILOT — ARCHITECTURE DECISION LOG (ADR)
# NHẬT KÝ QUYẾT ĐỊNH KIẾN TRÚC VÀ THIẾT KẾ HỆ THỐNG

Tài liệu này ghi lại toàn bộ các quyết định kiến trúc quan trọng của dự án RoboPilot. Mỗi quyết định được quản lý trạng thái nghiêm ngặt:
- `PROPOSED`: Đang đề xuất, chờ Chủ dự án (USER) hoặc Nhóm xem xét phê duyệt.
- `APPROVED`: Đã được phê duyệt chính thức làm căn cứ triển khai.
- `REJECTED`: Đã bị từ chối kèm lý do cụ thể.
- `BLOCKED`: Đang bị nghẽn do thiếu thông tin hoặc phụ thuộc điều kiện khác.

---

## BẢNG TỔNG HỢP CÁC QUYẾT ĐỊNH

| Mã ADR | Tiêu đề quyết định | Trạng thái | Ngày tạo | Người đề xuất |
| :--- | :--- | :--- | :--- | :--- |
| **ADR-001** | Phạm vi môi trường mô phỏng V1 là 2D Discrete Grid World | `APPROVED` | 2026-10-29 | Agent 0 (Master Brief) |
| **ADR-002** | Bộ thuật toán cốt lõi: Random, A*, Q-Learning, PyTorch DQN | `APPROVED` | 2026-10-29 | Agent 0 (Master Brief) |
| **ADR-003** | Tách rời hoàn toàn Training Subsystem và Serving/Inference Subsystem | `APPROVED` | 2026-10-29 | Agent 0 (Master Brief) |
| **ADR-004** | Thiết kế không gian quan sát (Observation Space) dạng Hybrid | `PROPOSED` | 2026-10-29 | Agent 0 |
| **ADR-005** | Thiết kế hàm thưởng (Reward Function) với Potential-based Shaping | `PROPOSED` | 2026-10-29 | Agent 0 |
| **ADR-006** | Công nghệ render Simulation Arena sử dụng HTML5 Canvas 2D | `APPROVED` | 2026-10-29 | Agent 0 |
| **ADR-007** | Cơ chế đồng bộ mô phỏng: WebSocket Stream kết hợp REST API | `PROPOSED` | 2026-10-29 | Agent 0 |
| **ADR-008** | Chiến lược lưu trữ tách biệt: PostgreSQL cho Metadata & Filesystem cho Trọng số | `APPROVED` | 2026-10-29 | Agent 0 |
| **ADR-009** | Cơ chế cơ sở dữ liệu linh hoạt: PostgreSQL cho Docker, SQLite Fallback cho Local Dev | `PROPOSED` | 2026-10-29 | Agent 0 |
| **ADR-010** | Chuẩn hóa cấu trúc đóng gói Model Artifact Package (`.pt` + `metadata.json`) | `PROPOSED` | 2026-10-29 | Agent 0 |

---

## CHI TIẾT CÁC QUYẾT ĐỊNH (ADR DETAILS)

### ADR-001: Phạm vi môi trường mô phỏng V1 là 2D Discrete Grid World
- **Trạng thái:** `APPROVED`
- **Bối cảnh:** Cần xây dựng nền tảng thử nghiệm thuật toán RL cho robot nhà kho tự hành. Các mô phỏng 3D hoặc vật lý liên tục ban đầu tiềm ẩn rủi ro quá tải kỹ thuật.
- **Quyết định:** Giới hạn V1 ở môi trường lưới ô vuông 2 chiều (Grid World), hành động rời rạc (4 hướng di chuyển: Up, Down, Left, Right). Chướng ngại vật tĩnh (kệ hàng).
- **Hệ quả:** Đơn giản hóa bài toán toán học, đảm bảo thuật toán Q-Learning và DQN hội tụ ổn định, giảm tải cho máy tính người học. Mở rộng sang continuous kinematics ở V2.

---

### ADR-002: Bộ thuật toán cốt lõi cho V1 (Random, A*, Q-Learning, PyTorch DQN)
- **Trạng thái:** `APPROVED`
- **Bối cảnh:** Cần so sánh công bằng giữa phương pháp tìm đường cổ điển và học tăng cường.
- **Quyết định:**
  1. `Random Policy`: Đo sàn hiệu năng tối thiểu.
  2. `A* Search`: Thuật toán tìm đường ngắn nhất tối ưu làm mốc đối chuẩn trần (Ground Truth Benchmark).
  3. `Tabular Q-Learning`: Minh họa học tăng cường cổ điển dựa trên bảng giá trị Q, hội tụ nhanh trên bản đồ nhỏ.
  4. `Deep Q-Network (DQN)` tự phát triển bằng PyTorch: Sử dụng mạng nơ-ron xấp xỉ Q-function, Target Network, Replay Buffer.
- **Hệ quả:** Cung cấp bức tranh toàn diện và khách quan về năng lực của RL so với phương pháp cổ điển.

---

### ADR-003: Tách rời hoàn toàn Training Subsystem và Serving/Inference Subsystem
- **Trạng thái:** `APPROVED`
- **Bối cảnh:** Việc chạy huấn luyện mô hình sâu (DQN) bên trong tiến trình web server hoặc container Docker nhẹ có thể gây treo server, tràn RAM hoặc quá tải CPU.
- **Quyết định:** 
  - Khâu Training diễn ra độc lập: chạy qua script Python CLI hoặc Google Colab GPU notebook. Kết quả huấn luyện được xuất thành tệp model artifact.
  - Ứng dụng Web (Backend + Frontend) chỉ thực thi nạp model artifact (Model Loading) và chạy suy luận (Inference Mode).
- **Hệ quả:** Hệ thống web nhẹ, phản hồi nhanh, ổn định và không đòi hỏi cấu hình máy chủ web phải có GPU đắt đỏ.

---

### ADR-004: Thiết kế không gian quan sát (Observation Space) dạng Hybrid
- **Trạng thái:** `PROPOSED` (Cần USER phê duyệt)
- **Bối cảnh:** Nếu chỉ dùng tọa độ tuyệt đối $(x, y)$, robot chỉ có thể ghi nhớ bản đồ đó (memorization) và sẽ thất bại hoàn toàn nếu đưa sang bản đồ mới (kém tổng quát). Nếu chỉ dùng sensor cục bộ, robot dễ rơi vào bẫy ngõ cụt khi không biết phương hướng đích.
- **Quyết định đề xuất:** Hỗ trợ 2 chế độ:
  1. *Coordinate Mode (cho Tabular Q-Learning):* `[robot_x, robot_y, goal_x, goal_y]`.
  2. *Sensor-Direction Vector Mode (cho DQN Generalization):* Vector gồm khoảng cách tới vật cản gần nhất ở 4 hướng $[d_{\text{up}}, d_{\text{down}}, d_{\text{left}}, d_{\text{right}}]$ kết hợp vector hướng tương đối tới đích $[\Delta x, \Delta y]$ và khoảng cách Manhattan.
- **Hệ quả:** DQN có thể học được chính sách phản xạ điều hướng tổng quát, có khả năng zero-shot trên bản đồ mới chưa từng học.

---

### ADR-005: Thiết kế hàm thưởng (Reward Function) với Potential-based Shaping
- **Trạng thái:** `PROPOSED` (Cần USER phê duyệt)
- **Bối cảnh:** Brief đưa ra giả định ban đầu (+100 đích, -100 va chạm, +1 tiến gần đích, -0.1 bước đi). Giả định "+1 khi tiến gần đích" nếu không cẩn thận sẽ dẫn đến **Reward Cycling (Reward Hacking)**: robot đi tới rồi lùi lại liên tục để farm điểm thưởng mà không cần đến đích.
- **Quyết định đề xuất:**
  - Phần thưởng đến đích: $+100.0$ (`terminated=True`).
  - Phạt va chạm vật cản / biên: $-10.0$ (hoặc $-20.0$, robot giữ nguyên vị trí để học tránh).
  - Phạt bước đi (Step Penalty): $-0.5$ (ép robot tìm đường ngắn nhất).
  - Thưởng định hướng (Potential-based Reward Shaping theo Ng et al., 1999):
    $$R_{\text{shaping}} = \gamma \Phi(s_{t+1}) - \Phi(s_t)$$
    với $\Phi(s) = - \text{ManhattanDistance}(s_{\text{robot}}, s_{\text{goal}})$. 
    *Được chứng minh toán học bảo toàn chính sách tối ưu, triệt tiêu hoàn toàn reward hacking.*
- **Hệ quả:** Robot học nhanh hơn trong không gian thưa, không bị lặp vô tận.

---

### ADR-006: Công nghệ render Simulation Arena sử dụng HTML5 Canvas 2D
- **Trạng thái:** `APPROVED`
- **Bối cảnh:** Cần vẽ bản đồ kho hàng 2D có robot di chuyển mượt mà, hỗ trợ trajectory trail và collision indicators.
- **Quyết định:** Sử dụng native HTML5 Canvas 2D API kết hợp React ref. Không sử dụng DOM nodes (div) vì chậm khi lưới lớn; không sử dụng Three.js/WebGL vì quá phức tạp so với yêu cầu 2D grid của V1.
- **Hệ quả:** Hiệu năng đạt 60 FPS ổn định, dung lượng bundle frontend cực nhẹ, dễ tùy biến màu sắc và animation.

---

### ADR-007: Cơ chế đồng bộ mô phỏng: WebSocket Stream kết hợp REST API
- **Trạng thái:** `PROPOSED` (Cần USER phê duyệt)
- **Bối cảnh:** Khi người dùng nhấn "Play", robot cần bước liên tục trên màn hình theo tốc độ điều chỉnh được (ví dụ 10 bước/giây). Polling HTTP GET liên tục sẽ gây độ trễ và quá tải kết nối.
- **Quyết định đề xuất:**
  - Dùng **WebSocket** (`/ws/simulation/{session_id}`): truyền phát các tick di chuyển thời gian thực từ Backend về Frontend khi ở chế độ Continuous Run.
  - Dùng **REST API**: cho các tác vụ CRUD (quản lý bản đồ, cấu hình, lấy danh sách model, xem lịch sử benchmark, step từng bước đơn lẻ).
- **Hệ quả:** Trải nghiệm người dùng mượt mà, phản hồi tức thì với nút Pause/Reset.

---

### ADR-008: Chiến lược lưu trữ tách biệt: PostgreSQL cho Metadata & Filesystem cho Trọng số
- **Trạng thái:** `APPROVED`
- **Bối cảnh:** Lưu trữ tệp nhị phân trọng số (PyTorch `.pt` nặng vài MB đến hàng chục MB) trực tiếp dưới dạng BLOB trong cơ sở dữ liệu quan hệ làm phình dung lượng DB và giảm hiệu năng truy vấn.
- **Quyết định:**
  - PostgreSQL chỉ lưu metadata: đường dẫn tệp (`file_path`), thuật toán, siêu tham số, chỉ số đánh giá, thời gian tạo.
  - Tệp trọng số mô hình (`.pt`, `.pkl`) được lưu trữ tại thư mục quy định (`/models/`), được mount qua Docker volume.
- **Hệ quả:** Tối ưu hóa hiệu năng cơ sở dữ liệu, việc sao lưu hoặc di chuyển model giữa các môi trường diễn ra độc lập và nhanh chóng.

---

### ADR-009: Cơ chế cơ sở dữ liệu linh hoạt: PostgreSQL cho Docker, SQLite Fallback cho Local Dev
- **Trạng thái:** `PROPOSED` (Cần USER phê duyệt)
- **Bối cảnh:** Người học hoặc lập trình viên khi thử nghiệm nhanh trên máy cá nhân có thể chưa cài sẵn PostgreSQL hoặc không muốn bật Docker ngay lập tức.
- **Quyết định đề xuất:** Backend sử dụng SQLAlchemy ORM với cấu hình biến môi trường `DATABASE_URL`. Khi chạy Docker Compose mặc định trỏ tới PostgreSQL. Khi chạy kiểm thử cục bộ không có Docker, có thể tự động fallback sang SQLite (`robopilot.db`).
- **Hệ quả:** Nâng cao tối đa tính tiện dụng và khả năng tương thích môi trường cho người dùng.

---

### ADR-010: Chuẩn hóa cấu trúc đóng gói Model Artifact Package (`.pt` + `metadata.json`)
- **Trạng thái:** `PROPOSED` (Cần USER phê duyệt)
- **Bối cảnh:** Nếu chỉ lưu `torch.save(model.state_dict(), 'model.pt')`, Backend khi nạp lại sẽ không biết kích thước input/output, số hidden layers, hay tham số chuẩn hóa observation, dẫn tới lỗi nạp mô hình.
- **Quyết định đề xuất:** Chuẩn hóa cấu trúc thư mục hoặc file nén của Model Artifact:
  - `model.pt` hoặc `q_table.pkl`: Trọng số mạng hoặc bảng Q.
  - `metadata.json`: Chứa schema đầy đủ:
    ```json
    {
      "model_id": "dqn_warehouse_v1_seed42",
      "algorithm": "DQN",
      "framework": "PyTorch",
      "observation_mode": "proximity_raycast",
      "observation_dim": 7,
      "action_dim": 4,
      "network_architecture": {
        "hidden_layers": [128, 128],
        "activation": "ReLU"
      },
      "hyperparameters": {
        "learning_rate": 0.0005,
        "gamma": 0.99,
        "epsilon_min": 0.05
      },
      "metrics": {
        "success_rate": 0.96,
        "avg_steps": 18.4,
        "collision_rate": 0.02
      }
    }
    ```
- **Hệ quả:** Backend tự động khởi tạo đúng kiến trúc mô hình và xác thực tính tương thích trước khi nạp vào bộ nhớ.
