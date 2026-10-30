# ROBOPILOT — QUANTITATIVE ACCEPTANCE CRITERIA (MVP)
# BỘ TIÊU CHÍ NGHIỆM THU ĐỊNH LƯỢNG SẢN PHẨM VÀ BẢO ĐẢM CHẤT LƯỢNG

> **Cơ quan ban hành:** Tab 7 (@tab_7) — QA & Research Validation Specialist  
> **Cơ quan giám sát:** Tab 1 (@tab_1) — Project Orchestrator  
> **Thẩm quyền:** Toàn quyền VETO (Bác bỏ nghiệm thu) nếu vi phạm chỉ tiêu chất lượng  
> **Trạng thái:** OFFICIAL DRAFT / MVP RELEASE 1.0 | **Ngày ban hành:** 2026-10-30  

---

## 1. NGUYÊN TẮC NGHIỆM THU ĐỊNH LƯỢNG (QUANTITATIVE FRAMEWORK)

Mọi đánh giá nghiệm thu sản phẩm RoboPilot MVP 1.0 phải dựa trên các con số định lượng có thể đo đạc và tái lập tự động, tuyệt đối không chấp nhận đánh giá cảm tính.

Các nguyên tắc cốt lõi:
1. **Không khoan nhượng về an toàn (Zero Collision Tolerance):** Trong chế độ suy luận triển khai thực tế (Evaluation / Inference), robot tuyệt đối không được gây tai nạn với kệ hàng hoặc vật cản tĩnh.
2. **Trung thực về dữ liệu (Statistical Truthfulness):** Kết quả RL phải được kiểm thử qua tối thiểu $5$ random seeds khác nhau; kết quả công bố là $\text{Mean} \pm \text{Std}$. Cấm chọn lọc hạt giống đơn lẻ (cherry-picking).
3. **Hiệu năng thời gian thực (Real-time Latency):** Phản hồi suy luận và stream đồ họa phải đáp ứng ngưỡng tương tác người dùng 60 FPS mà không giật lag.
4. **Chuẩn mực kỹ thuật nghiêm ngặt:** $100\%$ type hinting, tuân thủ `mypy --strict` và TypeScript `strict: true`.

---

## 2. BẢNG TIÊU CHÍ NGHIỆM THU ĐỊNH LƯỢNG THEO PHÂN HỆ

### 2.1. Phân hệ 1: Mô hình Học tăng cường (RL / Algorithm Benchmarks)

| Hạng mục nghiệm thu | Chỉ số đo lường | Ngưỡng đạt chuẩn (Target Threshold) | Phương thức đo đạc | Độ ưu tiên |
| :--- | :--- | :---: | :--- | :---: |
| **Tỉ lệ đến đích thành công** | $\text{Success Rate (SR)}$ | $\ge 95.0\%$ trên bản đồ Easy<br>$\ge 90.0\%$ trên bản đồ Medium<br>$\ge 85.0\%$ trên bản đồ Hard | Chạy 100 episodes độc lập trên mỗi bản đồ | Blocker |
| **Tỉ lệ va chạm khi suy luận** | $\text{Collision Rate (CR)}$ | $\le 2.0\%$ tổng số bước di chuyển | Ghi nhận trong 100 test episodes | Blocker |
| **Hiệu suất đường đi so với A***| $\text{Path Efficiency Ratio (PER)} = \frac{L_{\text{A*}}}{L_{\text{RL}}}$ | $\ge 88.0\%$ | So sánh số bước đi thực tế với thuật toán A* tối ưu | High |
| **Độ ổn định đa hạt giống** | Coefficient of Variation ($\text{CV} = \sigma / \mu$) | $\le 15.0\%$ | Đánh giá trên 5 random seeds khác nhau | High |
| **Triệt tiêu Reward Hacking** | Chu trình lặp 2 ô ($s_0 \leftrightarrow s_1$) | Reward tích lũy $\sum r_t < 0$ với mọi chu trình lặp | Chạy test suite `TC-RWD-01` | Blocker |
| **Độ trễ suy luận mô hình** | Inference Latency (D3QN) | $\le 5.0\text{ ms}$ / step (CPU)<br>$\le 1.5\text{ ms}$ / step (GPU) | Đo đạc qua 1,000 forward passes | Medium |

---

### 2.2. Phân hệ 2: Môi trường Mô phỏng (Gymnasium Environment)

| Hạng mục nghiệm thu | Chỉ số đo lường | Ngưỡng đạt chuẩn (Target Threshold) | Phương thức đo đạc | Độ ưu tiên |
| :--- | :--- | :---: | :--- | :---: |
| **Gymnasium Compliance** | `check_env()` status | $0$ Error, $0$ Warning | Chạy `gymnasium.utils.env_checker` | Blocker |
| **Độ phức tạp kiểm tra va chạm**| Time Complexity | $O(1)$ Matrix lookup | Phân tích thuật toán & đo benchmark microsecond | High |
| **Tính tái lập của Seed** | Deterministic Seed Match | $100\%$ bit-exact match | Chạy 2 môi trường cùng seed và chuỗi action | Blocker |
| **Giới hạn bước (Truncation)**| Max Steps Invariant | Dừng chính xác tại $2.5 \times (W+H)$ | Chạy test suite `TC-ENV-04` | High |
| **Tính giải được của bản đồ**| Reachability Solvability | $100\%$ các bản đồ có đường đi hợp lệ (BFS check) | Chạy BFS xác thực trước khi nạp | Blocker |

---

### 2.3. Phân hệ 3: Backend & MLOps Infrastructure

| Hạng mục nghiệm thu | Chỉ số đo lường | Ngưỡng đạt chuẩn (Target Threshold) | Phương thức đo đạc | Độ ưu tiên |
| :--- | :--- | :---: | :--- | :---: |
| **REST API Latency** | Step Simulation API Latency | p95 $\le 10\text{ ms}$, p99 $\le 20\text{ ms}$ | Benchmark bằng Locust với 50 concurrent requests | High |
| **WebSocket Telemetry Stream** | Streaming Frame Rate | $30\text{ FPS} \pm 2\text{ FPS}$ | Đo đạc qua client listener trong 5 phút liên tục | High |
| **Dynamic Model Loader** | Model Switch Time | $\le 500\text{ ms}$ khi đổi checkpoint | Chuyển đổi giữa 3 weights khác nhau | Medium |
| **Docker Compose Startup** | One-command cold start | Khởi động toàn bộ cụm trong $\le 45\text{ s}$ | Chạy `docker compose up -d` từ trạng thái sạch | High |
| **Rò rỉ bộ nhớ (Memory Leak)**| Long-running RAM Delta | Tăng trưởng $\le 10\text{ MB}$ sau 10,000 steps | Quan sát process memory qua `psutil` | High |

---

### 2.4. Phân hệ 4: Frontend & Canvas Simulation UI

| Hạng mục nghiệm thu | Chỉ số đo lường | Ngưỡng đạt chuẩn (Target Threshold) | Phương thức đo đạc | Độ ưu tiên |
| :--- | :--- | :---: | :--- | :---: |
| **Tốc độ khung hình Canvas** | Rendering Frame Rate | $55 - 60\text{ FPS}$ ổn định | Chrome DevTools Performance Monitor | High |
| **Độ trễ phản hồi tương tác** | Click-to-Action Response | $\le 16.6\text{ ms}$ (1 frame latency) | Bấm nút Step/Play đến khi robot dịch chuyển | Medium |
| **Độ trễ chèn vật cản động** | Dynamic Obstacle Latency | $\le 50\text{ ms}$ từ khi click đến khi grid đổi màu | Đo thời gian gửi và nhận WebSocket state | Medium |
| **Khả năng phục hồi kết nối**| WebSocket Auto-reconnect | Tự động kết nối lại trong $\le 2.0\text{ s}$ khi ngắt mạng | Giả lập rớt socket và quan sát trạng thái | High |

---

### 2.5. Phân hệ 5: Chuẩn mực Kỹ thuật & Độ bao phủ Kiểm thử (Code Standards)

| Hạng mục nghiệm thu | Chỉ số đo lường | Ngưỡng đạt chuẩn (Target Threshold) | Phương thức đo đạc | Độ ưu tiên |
| :--- | :--- | :---: | :--- | :---: |
| **Code Test Coverage** | Line Coverage | $\ge 90.0\%$ toàn bộ core modules | Chạy `pytest --cov=src tests/` | Blocker |
| **Python Static Typing** | Mypy Type Errors | $0$ errors (`mypy --strict src/`) | Kiểm tra mã nguồn tự động | Blocker |
| **PEP 8 Compliance** | Flake8 / Ruff Warnings | $0$ errors (`ruff check src/`) | Linting kiểm tra tĩnh | High |
| **TypeScript Strictness** | TypeScript Type Errors | $0$ errors (`tsc --noEmit`), cấm `any` | Compile-time check | Blocker |

---

## 3. QUY TRÌNH KÝ DUYỆT CỔNG NGHIỆM THU (QUALITY GATES MATRIX)

```
[ Phase 1: Environment & Reward ] ──(Gate 1)──> [ Phase 2: Training Pipeline ]
                                                      │
                                                   (Gate 2)
                                                      │
[ Phase 4: Frontend UI & Canvas ] <──(Gate 4)── [ Phase 3: Backend & MLOps ]
               │
           (Gate 5)
               │
               v
  [ CHÍNH THỨC PHÁT HÀNH MVP ]
```

### Điều kiện VETO của Tab 7 tại mỗi cổng:
- **Gate 1:** Nếu phát hiện sai lệch bất biến va chạm hoặc hàm thế năng PBRS không thỏa mãn $\sum r_t < 0$ cho chu trình lặp $\to$ **VETO**.
- **Gate 2:** Nếu mô hình RL chỉ được báo cáo trên 1 seed duy nhất hoặc không cung cấp độ lệch chuẩn $\to$ **VETO**.
- **Gate 3:** Nếu endpoint API vượt quá ngưỡng trễ $20\text{ ms}$ hoặc WebSocket rớt khung hình $\to$ **VETO**.
- **Gate 4:** Nếu Canvas render dưới $45\text{ FPS}$ hoặc mất đồng bộ vị trí robot $\to$ **VETO**.
- **Gate 5:** Nếu độ bao phủ test $< 90\%$ hoặc còn tồn tại lỗi type check $\to$ **VETO**.

---

## 4. BẢNG KÝ NHẬN CAM KẾT GIỮA CÁC TAB

| Tab | Vai trò | Cam kết chất lượng | Ký nhận |
| :---: | :--- | :--- | :---: |
| **Tab 1** | Project Orchestrator | Đảm bảo tính nhất quán hợp đồng và điều phối tiến độ | `APPROVED` |
| **Tab 2** | RL Researcher | Cam kết hàm thưởng triệt tiêu reward hacking, chứng minh toán học chuẩn | `COMMITTED` |
| **Tab 3** | Simulation Designer | Cam kết môi trường chuẩn Gymnasium, va chạm $O(1)$ an toàn tuyệt đối | `COMMITTED` |
| **Tab 4** | Training Architect | Cam kết pipeline huấn luyện tái lập, đánh giá $\ge 5$ seeds | `COMMITTED` |
| **Tab 5** | Backend MLOps | Cam kết API độ trễ thấp, WebSocket 30 FPS, Docker 1 lệnh | `COMMITTED` |
| **Tab 6** | Frontend Designer | Cam kết Canvas 60 FPS, không dùng `any`, UI chuẩn công nghiệp | `COMMITTED` |
| **Tab 7** | QA Auditor | Độc lập kiểm thử, nghiệm thu thực chứng, bảo vệ chuẩn mực chất lượng | `OFFICIAL AUDITOR` |
