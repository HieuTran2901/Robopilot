# ROBOPILOT — QUALITY ASSURANCE & VERIFICATION TEST PLAN
# KẾ HOẠCH KIỂM ĐỊNH ĐỘC LẬP VÀ BÀI TEST ĐỐI KHÁNG (PHASE 1 - 4 AUDIT)

> **Cơ quan phụ trách:** Tab 7 (@tab_7) — QA & Research Validation Specialist  
> **Giám sát:** Tab 1 (@tab_1) — Orchestrator | **Đối tượng kiểm thử:** Tab 2, Tab 3, Tab 4, Tab 5, Tab 6  
> **Trạng thái:** ACTIVE / PHASE 1 (Sprint 1) | **Ngày cập nhật:** 2026-10-30  

---

## 1. MỤC TIÊU VÀ NGUYÊN TẮC KIỂM ĐỊNH (ZERO-TOLERANCE AUDIT)

Với vị thế là cơ quan kiểm định độc lập tuân thủ nghiêm ngặt tôn chỉ **"Zero-Tolerance to Corner Cutting"** và chuẩn mực khoa học [GEMINI.md](../GEMINI.md), Tab 7 thiết lập kế hoạch kiểm định toàn diện xuyên suốt 4 giai đoạn phát triển:

1. **Tuyệt đối khách quan & thực chứng:** Mọi kết luận kỹ thuật phải dựa trên kiểm chứng toán học, duyệt mã tĩnh hoặc kết quả chạy kiểm thử tự động; cấm suy diễn chủ quan hoặc làm tròn số liệu.
2. **Quyền phủ quyết (VETO Power):** Nếu phát hiện bất kỳ dấu hiệu Reward Hacking, rò rỉ bộ nhớ, sai lệch hợp đồng hoặc vi phạm an toàn va chạm, Tab 7 có toàn quyền tạm dừng (Block) quy trình chuyển pha cho đến khi lỗi được khắc phục triệt để.
3. **Bao phủ đa tầng (Multi-tier Verification):** Kiểm thử đơn vị (Unit Tests), Kiểm thử đối kháng (Adversarial Tests), Kiểm thử tải & độ trễ (Performance/Stress Tests), và Kiểm thử tích hợp đầu-cuối (E2E Integration Tests).

---

## 2. MA TRẬN KỊCH BẢN KIỂM THỬ GIAI ĐOẠN 1 (PHASE 1: ENVIRONMENT & REWARD)

```
+-----------------------------------------------------------------------------------+
|                            PHASE 1 TEST ARCHITECTURE                              |
+-----------------------------------------------------------------------------------+
|  [Group 1: Gymnasium Standard]   TC-ENV-01 -> TC-ENV-04 (Check Env, Bounds, Seed) |
|  [Group 2: Collision Invariant]  TC-COL-01 -> TC-COL-03 (Boundary, Shelves, Fuzz) |
|  [Group 3: Anti-Reward Hacking]  TC-RWD-01 -> TC-RWD-04 (Oscillation, Stalling)   |
|  [Group 4: Map Reachability]     TC-MAP-01 -> TC-MAP-03 (BFS Solvability Verification)
+-----------------------------------------------------------------------------------+
```

### Nhóm 1: Kiểm thử Chuẩn mực Gymnasium (Gym Compliance Tests)

| Mã Test | Tên kiểm thử | Phương pháp thực thi | Tiêu chí Đạt (Pass Criteria) | Trọng số |
| :---: | :--- | :--- | :--- | :---: |
| **TC-ENV-01** | `test_check_env` | Chạy `gymnasium.utils.env_checker.check_env(env)` | Không có ngoại lệ hoặc Warning nào phát sinh. | Critical |
| **TC-ENV-02** | `test_seed_reproducibility` | Gọi `reset(seed=42)` 2 lần trên 2 instance độc lập | Vector quan sát ban đầu và trạng thái ngẫu nhiên khớp $100\%$ từng bit float. | Critical |
| **TC-ENV-03** | `test_observation_bounds` | Cho robot thực hiện 1,000 bước đi ngẫu nhiên | Mọi phần tử $o_i$ luôn nằm nghiêm ngặt trong đoạn $[-1.0, 1.0]$. | High |
| **TC-ENV-04** | `test_truncation_limit` | Chạy robot cố tình không về đích cho đến hết giờ | Episode dừng chính xác tại bước thứ $\text{MaxSteps}$, `truncated == True`, `terminated == False`. | High |

---

### Nhóm 2: Kiểm thử Bất biến Va chạm (Collision Invariant Tests)

| Mã Test | Tên kiểm thử | Phương pháp thực thi | Tiêu chí Đạt (Pass Criteria) | Trọng số |
| :---: | :--- | :--- | :--- | :---: |
| **TC-COL-01** | `test_boundary_collision` | Đặt robot tại $(0, 0)$, thực hiện hành động `UP` và `LEFT` | Robot giữ nguyên tọa độ $(0, 0)$, cờ `is_collision == True`. | Critical |
| **TC-COL-02** | `test_shelf_collision` | Đặt robot cạnh kệ hàng, ra lệnh đi vào ô kệ hàng | Robot giữ nguyên tọa độ, không đi xuyên tường, nhận phạt $-10.0$ và trừ thêm $-1.0\%$ pin. | Critical |
| **TC-COL-03** | `test_zero_slip_fuzzing` | Chạy 10,000 hành động ngẫu nhiên trên bản đồ Hard | Tọa độ robot không bao giờ rơi vào ô có giá trị $\text{Grid}[y][x] == 1$. | Critical |

---

### Nhóm 3: Kiểm thử Đối kháng Chống Reward Hacking (Anti-Reward Hacking Tests)

| Mã Test | Tên kiểm thử | Phương pháp thực thi | Tiêu chí Đạt (Pass Criteria) | Trọng số |
| :---: | :--- | :--- | :--- | :---: |
| **TC-RWD-01** | `test_oscillation_penalty` | Bắt ép robot đi qua lại giữa 2 ô liên tục trong 100 bước: $s_0 \to s_1 \to s_0 \to \dots$ | **Tổng phần thưởng tích lũy bắt buộc phải âm sâu** ($\sum r_t < -45.0$). Tuyệt đối cấm sinh lãi điểm thưởng! | Blocker |
| **TC-RWD-02** | `test_stalling_penalty` | Cho robot đứng yên va chạm liên tục vào tường 50 bước | Phần thưởng tích lũy tụt giảm dốc đứng ($50 \times (-10.5) = -525.0$). | Blocker |
| **TC-RWD-03** | `test_shortest_path_reward`| So sánh đường đi tối ưu (A*) với đường đi vòng vèo | Đường đi tối ưu nhận tổng reward cao hơn hẳn đường đi vòng vèo ($\ge 15\%$ chênh lệch). | Blocker |
| **TC-RWD-04** | `test_battery_depletion` | Chạy robot tới khi pin $= 0\%$ mà chưa đến đích | Episode kết thúc (`terminated = True`), chịu phạt chết máy $-50.0$. | High |

---

### Nhóm 4: Kiểm định Tính Giải Được Bản Đồ (Map Reachability Verification)

> **LƯU Ý THẨM ĐỊNH (AUDIT FINDING AF-01):** Bản đồ Easy 10x10 có 2 dãy tường cản tại cột $x=3$ và $x=6$. Do đó, khoảng cách ngắn nhất thực tế là **16 bước** (không phải 14 bước như khoảng cách Manhattan thuần túy). Tiêu chí kiểm thử được cập nhật chuẩn xác theo thực tế BFS.

| Mã Test | Tên kiểm thử | Phương pháp thực thi | Tiêu chí Đạt (Pass Criteria) | Trọng số |
| :---: | :--- | :--- | :--- | :---: |
| **TC-MAP-01** | `test_easy_10x10_reachability` | Chạy BFS trên `benchmark_easy_10x10.json` | Tồn tại đường đi từ Start đến Goal; độ dài BFS ngắn nhất chính xác bằng **$16$ bước**. | Critical |
| **TC-MAP-02** | `test_medium_15x15_reachability`| Chạy BFS trên `benchmark_medium_15x15.json`| Tồn tại đường đi; độ dài BFS ngắn nhất chính xác bằng **$24$ bước**. | Critical |
| **TC-MAP-03** | `test_hard_20x20_reachability` | Chạy BFS trên `benchmark_hard_20x20.json` | Tồn tại đường đi; độ dài BFS ngắn nhất chính xác bằng **$36$ bước**. | Critical |

---

## 3. KỊCH BẢN KIỂM THỬ CÁC GIAI ĐOẠN TIẾP THEO (PHASE 2 - 4 PREVIEW)

### 3.1. Phase 2: ML/RL Training Pipeline Verification
- **TC-TRN-01 (Reproducibility):** Huấn luyện 2 runs với cùng 1 seed $\to$ Loss và Reward curve phải trùng nhau với dung sai $\epsilon < 10^{-6}$.
- **TC-TRN-02 (Multi-seed Consistency):** Chạy tối thiểu 5 random seeds (seeds: 42, 101, 2024, 777, 9999); hệ số biến thiên $\text{CV} = \frac{\sigma}{\mu} \le 15\%$.
- **TC-TRN-03 (Model Artifact Integrity):** Nạp file `model_best.pth` và kiểm tra metadata JSON chứa đầy đủ cấu hình hyperparameter, commit hash và metrics.

### 3.2. Phase 3: Backend & API Performance Verification
- **TC-API-01 (Inference Latency):** Endpoint `/api/v1/simulate/step` xử lý 1 action inference trong thời gian $\le 5\text{ ms}$ (p95).
- **TC-WS-01 (WebSocket Stream Rate):** Stream telemetry đạt $30\text{ FPS} \pm 2\text{ FPS}$ liên tục trong 10 phút không rò rỉ bộ nhớ (leak $< 5\text{ MB}$).
- **TC-DB-01 (Schema Integrity):** Toàn bộ Foreign Keys và Unique constraints trong PostgreSQL hoạt động chuẩn xác; không có dữ liệu mồ côi.

### 3.3. Phase 4: Frontend UI & E2E Verification
- **TC-UI-01 (Canvas Render FPS):** Render Canvas 2D đạt tối thiểu $55 - 60\text{ FPS}$ trên Chrome và Firefox.
- **TC-UI-02 (Dynamic Obstacle Injection):** Thêm vật cản trực tiếp trên Canvas $\to$ Backend cập nhật ma trận trong vòng $\le 50\text{ ms}$.

---

## 4. QUY TRÌNH KÝ DUYỆT CỔNG CHẤT LƯỢNG (QUALITY GATE SIGN-OFF)

Mỗi giai đoạn chỉ được bàn giao khi đáp ứng $100\%$ các tiêu chí cổng chất lượng:
1. Bộ test case tương ứng được hiện thực hóa đầy đủ bằng `pytest` trong thư mục `tests/`.
2. Tỉ lệ Pass đạt $100\%$ (Zero Failures, Zero Skips).
3. Độ bao phủ mã kiểm thử (Code Coverage) đạt $\ge 90\%$.
4. Báo cáo thẩm định độc lập từ Tab 7 được Tab 1 và Boss phê chuẩn.
