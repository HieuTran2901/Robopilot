# ROBOPILOT — QUALITY ASSURANCE & VERIFICATION TEST PLAN
# KẾ HOẠCH KIỂM ĐỊNH ĐỘC LẬP VÀ BÀI TEST ĐỐI KHÁNG (PHASE 1 AUDIT)

> **Cơ quan phụ trách:** Tab 7 (@tab_7) — QA & Research Validation Specialist  
> **Giám sát:** Tab 1 (@tab_1) — Orchestrator | **Đối tượng kiểm thử:** Tab 2 & Tab 3  
> **Trạng thái:** DRAFT / PHASE 1 (Sprint 1) | **Ngày ban hành:** 2026-10-30  

---

## 1. MỤC TIÊU VÀ PHẠM VI KIỂM ĐỊNH (AUDIT SCOPE)

Với tư cách là cơ quan kiểm định độc lập tuân thủ nguyên tắc **Zero-Tolerance to Corner Cutting** của [ENGINEERING_FRAMEWORK.md](../ENGINEERING_FRAMEWORK.md), Tab 7 thiết lập bộ kế hoạch kiểm thử tự động toàn diện cho Phase 1 nhằm đảm bảo:
1. Môi trường `WarehouseGridEnv` tuân thủ $100\%$ chuẩn Gymnasium.
2. Logic va chạm tuyệt đối an toàn ($O(1)$ Invariant).
3. Hàm thưởng triệt tiêu hoàn toàn nguy cơ Reward Hacking / Reward Cycling.
4. Toàn bộ 3 bản đồ benchmark đảm bảo tính giải được (Solvable).

---

## 2. MA TRẬN KỊCH BẢN KIỂM THỬ (TEST CASE SPECIFICATION)

### Nhóm 1: Kiểm thử Chuẩn mực Gymnasium (Gym Compliance Tests)

| Mã Test | Tên kiểm thử | Phương pháp thực thi | Tiêu chí Đạt (Pass Criteria) |
| :---: | :--- | :--- | :--- |
| **TC-ENV-01** | `test_check_env` | Chạy `gymnasium.utils.env_checker.check_env(env)` | Không có ngoại lệ hoặc Warning nào phát sinh. |
| **TC-ENV-02** | `test_seed_reproducibility` | Gọi `reset(seed=42)` 2 lần trên 2 instance khác nhau | Hai vector observation ban đầu trùng khớp $100\%$ từng bit float. |
| **TC-ENV-03** | `test_observation_bounds` | Cho robot thực hiện 1,000 bước đi ngẫu nhiên | Mọi phần tử $o_i$ luôn nằm nghiêm ngặt trong đoạn $[-1.0, 1.0]$. |
| **TC-ENV-04** | `test_truncation_limit` | Chạy robot không cho về đích đến khi hết giờ | Episode dừng chính xác tại bước thứ $\text{MaxSteps}$, `truncated == True`. |

---

### Nhóm 2: Kiểm thử Bất biến Va chạm (Collision Invariant Tests)

| Mã Test | Tên kiểm thử | Phương pháp thực thi | Tiêu chí Đạt (Pass Criteria) |
| :---: | :--- | :--- | :--- |
| **TC-COL-01** | `test_boundary_collision` | Đặt robot tại $(0, 0)$, thực hiện hành động `UP` và `LEFT` | Robot giữ nguyên tọa độ $(0, 0)$, cờ `is_collision == True`. |
| **TC-COL-02** | `test_shelf_collision` | Đặt robot cạnh kệ hàng, ra lệnh đi vào ô kệ hàng | Robot giữ nguyên tọa độ, không đi xuyên tường, nhận phạt $-10.0$. |
| **TC-COL-03** | `test_zero_slip_fuzzing` | Chạy 10,000 hành động ngẫu nhiên trên bản đồ Hard | Tọa độ robot không bao giờ rơi vào ô có giá trị $\text{Grid}[y][x] == 1$. |

---

### Nhóm 3: Kiểm thử Đối kháng Chống Reward Hacking (Anti-Hacking Adversarial Tests)

| Mã Test | Tên kiểm thử | Phương pháp thực thi | Tiêu chí Đạt (Pass Criteria) |
| :---: | :--- | :--- | :--- |
| **TC-RWD-01** | `test_oscillation_penalty` | Bắt ép robot đi qua lại giữa 2 ô liên tục trong 100 bước: $s_0 \to s_1 \to s_0 \to \dots$ | **Tổng phần thưởng tích lũy bắt buộc phải âm sâu** ($\sum r_t < -45.0$). Tuyệt đối cấm sinh lãi điểm thưởng! |
| **TC-RWD-02** | `test_stalling_penalty` | Cho robot đứng yên va chạm liên tục vào tường 50 bước | Phần thưởng tích lũy tụt giảm dốc đứng ($50 \times (-10.5) = -525.0$). |
| **TC-RWD-03** | `test_shortest_path_reward`| So sánh đường đi tối ưu (A*) với đường đi vòng vèo | Đường đi tối ưu nhận tổng reward cao hơn hẳn đường đi vòng vèo. |

---

### Nhóm 4: Kiểm định Tính Giải Được Bản Đồ (Map Reachability Verification)

| Mã Test | Tên kiểm thử | Phương pháp thực thi | Tiêu chí Đạt (Pass Criteria) |
| :---: | :--- | :--- | :--- |
| **TC-MAP-01** | `test_easy_10x10_reachability` | Chạy BFS trên `benchmark_easy_10x10.json` | Tồn tại đường đi từ Start đến Goal; độ dài BFS đúng bằng $14$ bước. |
| **TC-MAP-02** | `test_medium_15x15_reachability`| Chạy BFS trên `benchmark_medium_15x15.json`| Tồn tại đường đi; độ dài BFS đúng bằng $24$ bước. |
| **TC-MAP-03** | `test_hard_20x20_reachability` | Chạy BFS trên `benchmark_hard_20x20.json` | Tồn tại đường đi; độ dài BFS đúng bằng $36$ bước. |

---

## 3. QUY TRÌNH KÝ DUYỆT CỔNG CHẤT LƯỢNG (PHASE 1 SIGN-OFF CRITERIA)

Tab 7 sẽ chỉ cấp chứng nhận `SIGN-OFF` cho Phase 1 khi:
1. $100\%$ các kịch bản test trên được viết thành mã kiểm thử tự động tại `tests/test_environment.py`.
2. Chạy `pytest` đạt tỉ lệ $100\%$ Passed (không có xfail, không bỏ qua test).
3. Báo cáo Code Coverage đạt $\ge 90\%$.
4. Tab 1 và Boss phê duyệt tài liệu.

> **QUYỀN PHỦ QUYẾT (VETO POWER):** Nếu bất kỳ kiểm thử nào trong Nhóm 3 (Reward Hacking) bị thất bại, Tab 7 sẽ ngay lập tức kích hoạt cờ `BLOCKED` trong mailbox của Tab 2 và yêu cầu tính toán lại thế năng $\Phi(s)$!
