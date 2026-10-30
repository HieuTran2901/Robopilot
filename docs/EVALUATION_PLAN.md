# ROBOPILOT — RL EVALUATION & BENCHMARKING PLAN
# PHƯƠNG PHÁP ĐÁNH GIÁ THUẬT TOÁN HỌC TĂNG CƯỜNG VÀ THỰC NGHIỆM ĐỐI CHUẨN

> **Cơ quan phụ trách:** Tab 7 (@tab_7) — QA & Research Validation Specialist  
> **Phối hợp:** Tab 2 (@tab_2) — RL Researcher & Tab 4 (@tab_4) — Training Architect  
> **Phê duyệt:** Tab 1 (@tab_1) — Project Orchestrator  
> **Trạng thái:** OFFICIAL / PHASE 1 (Sprint 1) | **Ngày ban hành:** 2026-10-30  

---

## 1. NGUYÊN TẮC THỰC NGHIỆM KHOA HỌC (SCIENTIFIC EVALUATION PROTOCOL)

Nhằm tuân thủ tuyệt đối quy tắc **Zero Tolerance đối với số liệu giả** theo [GEMINI.md](../GEMINI.md) và hướng dẫn nghiên cứu RL tiêu chuẩn (Henderson et al., 2018; Agarwal et al., 2021), toàn bộ quá trình đánh giá hiệu năng thuật toán trong RoboPilot bắt buộc tuân thủ:

1. **Giao thức Đa hạt giống (Multi-Seed Protocol):** Mỗi mô hình/cấu hình phải được huấn luyện và đánh giá trên tối thiểu **5 random seeds độc lập**:
   $$\mathcal{S}_{\text{eval}} = \{42, 101, 2024, 777, 9999\}$$
2. **Biểu diễn Thống kê Chuẩn:** Mọi chỉ số công bố bắt buộc trình bày dưới dạng:
   $$\bar{X} \pm \sigma \quad \text{hoặc} \quad 95\% \text{ Bootstrap Confidence Interval (CI)}$$
   Tuyệt đối cấm chỉ chọn seed có kết quả cao nhất để báo cáo.
3. **Phân định rõ Train vs Eval Environment:** Đánh giá trong chế độ khai thác thuần túy ($\epsilon = 0$, determinism mode), tách biệt khỏi quá trình thăm dò huấn luyện.

---

## 2. HỆ THỐNG THUẬT TOÁN ĐỐI CHUẨN (BENCHMARK BASELINES)

Để chứng minh giá trị thực tiễn và tính ưu việt của AI so với các phương pháp cổ điển, RoboPilot thiết lập 4 thuật toán đối chuẩn:

```
+-----------------------------------------------------------------------------------+
|                        BENCHMARK ALGORITHM MATRIX                                 |
+-----------------------------------------------------------------------------------+
| 1. Random Agent         -> Kiểm soát sàn đáy (Baseline floor, tỷ lệ thành công ~ 0%) |
| 2. Classic A* Search    -> Đường đi tối ưu lý thuyết (Optimal Ground Truth)       |
| 3. Tabular Q-Learning   -> Baseline học tăng cường cổ điển (Coordinate Mode)      |
| 4. PyTorch D3QN (Agent) -> Giải pháp cốt lõi V1 (Sensor Mode, Zero-shot transfer) |
+-----------------------------------------------------------------------------------+
```

### So sánh Đặc tính Kỹ thuật:

| Thuật toán | Loại thuật toán | Không gian quan sát | Khả năng né vật cản động | Khả năng tổng quát hóa |
| :--- | :--- | :---: | :---: | :---: |
| **Random Agent** | Ngẫu nhiên đều | Bất kỳ | Không có | Không |
| **A\* Search** | Quy hoạch đồ thị tĩnh | Toàn cảnh ma trận | Phải re-plan toàn bộ ($O(N \log N)$) | Phải biết trước bản đồ |
| **Q-Learning** | Model-free Tabular | Tọa độ $(x_r, y_r)$ | Kém, phụ thuộc vị trí ô | Không thể chạy map khác |
| **D3QN (Ours)** | Deep Reinforcement | 7 Cảm biến lân cận | Phản xạ tức thì $O(1)$ ($< 2\text{ ms}$) | Chạy tốt trên map chưa thấy |

---

## 3. CÁC CHỈ SỐ ĐÁNH GIÁ ĐỊNH LƯỢNG (QUANTITATIVE METRICS)

### 3.1. Tỉ lệ Thành công (Success Rate - SR)
Tỉ lệ phần trăm các episodes mà robot về tới ô `GOAL` trước khi cạn pin hoặc hết thời gian:
$$\text{SR} = \frac{N_{\text{success}}}{N_{\text{total}}} \times 100\%$$
- **Mục tiêu nghiệm thu:** Bản đồ Easy $\ge 95\%$, Medium $\ge 90\%$, Hard $\ge 85\%$.

### 3.2. Hệ số Hiệu suất Đường đi so với A* (Path Efficiency Ratio - PER)
Đánh giá mức độ tiệm cận đường đi ngắn nhất lý thuyết của A*:
$$\text{PER} = \frac{L_{\text{A*}}}{L_{\text{RL}}}$$
- $\text{PER} = 1.0$: Robot đi theo đúng đường đi ngắn nhất hoàn hảo.
- $\text{PER} < 0.8$: Robot đi vòng vèo, chưa tối ưu hành động.
- **Mục tiêu nghiệm thu:** $\text{PER} \ge 0.88$ (trung bình trên các runs thành công).

### 3.3. Tỉ lệ Va chạm (Collision Rate - CR)
Tỉ lệ các bước di chuyển mà robot va phải kệ hàng hoặc biên:
$$\text{CR} = \frac{\sum_{t=1}^{T} \mathbb{I}(\text{collision}_t)}{T} \times 100\%$$
- **Mục tiêu nghiệm thu:** $\text{CR} \le 2.0\%$ trong chế độ đánh giá.

### 3.4. Điểm Đánh giá Tổng quát hóa Không cần Học lại (Zero-shot Generalization Score)
Đánh giá mô hình đã huấn luyện trên `benchmark_easy` và `benchmark_medium`, sau đó nạp trực tiếp vào `benchmark_hard` hoặc bản đồ ngẫu nhiên chưa từng thấy:
$$\text{GenScore} = \frac{\text{SR}_{\text{unseen}}}{\text{SR}_{\text{training}}}$$
- **Mục tiêu:** $\text{GenScore} \ge 0.75$.

---

## 4. QUY TRÌNH THỰC HIỆN KIỂM ĐỊNH (EXECUTION PROTOCOL)

```
[ Huấn luyện trên 5 Seeds ] ──> [ Lưu Checkpoints & Metadata ]
                                                │
                                                v
[ Kiểm thử Độc lập (Tab 7) ] <── [ Trích xuất Weights Tốt nhất ]
         │
         ├── 1. Chạy 100 Episodes / Seed / Bản đồ (Tổng cộng 1,500 episodes)
         ├── 2. Đo đạc độ trễ inference (Latency Benchmark)
         ├── 3. Kiểm định đối kháng chống Reward Hacking
         └── 4. Tính toán p-value (Wilcoxon Signed-Rank Test)
                 │
                 v
[ Xuất Báo cáo Nghiệm thu docs/BENCHMARK_REPORT.md ]
```

---

## 5. KIỂM ĐỊNH Ý NGHĨA THỐNG KÊ (STATISTICAL SIGNIFICANCE TESTING)

Khi so sánh D3QN với Q-Learning hoặc A*:
1. Không chỉ so sánh giá trị trung bình đơn thuần.
2. Áp dụng kiểm định phi tham số **Wilcoxon Signed-Rank Test** (hoặc Paired Student's t-test nếu thỏa mãn phân phối chuẩn Shapiro-Wilk) trên từng cặp episodes cùng cấu hình khởi đầu:
   $$H_0: \mu_{\text{D3QN}} = \mu_{\text{Q-Learning}} \quad \text{vs} \quad H_1: \mu_{\text{D3QN}} > \mu_{\text{Q-Learning}}$$
3. Kết luận ưu việt chỉ được Tab 7 công nhận khi:
   $$p\text{-value} < 0.01$$

---

## 6. ĐỊNH DẠNG DỮ LIỆU ĐẦU RA BẮT BUỘC (EVALUATION ARTIFACT FORMAT)

Toàn bộ kết quả thí nghiệm phải được xuất ra định dạng JSON và CSV phục vụ Dashboard Frontend (Tab 6) và QA Audit:

```json
{
  "experiment_id": "EXP_20261030_D3QN_BENCHMARK",
  "algorithm": "D3QN",
  "seeds": [42, 101, 2024, 777, 9999],
  "episodes_per_seed": 100,
  "results_by_map": {
    "benchmark_easy_10x10": {
      "success_rate_mean": 98.4,
      "success_rate_std": 1.2,
      "path_efficiency_ratio_mean": 0.94,
      "collision_rate_mean": 0.4,
      "mean_steps_optimal_bfs": 16,
      "mean_steps_rl": 17.02
    }
  },
  "verified_by": "Tab 7 · QA Auditor",
  "audit_status": "PASSED"
}
```
