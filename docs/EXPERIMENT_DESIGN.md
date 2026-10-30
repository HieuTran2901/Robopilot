# ROBOPILOT — SCIENTIFIC EXPERIMENT DESIGN & BENCHMARKING PROTOCOL
# KẾ HOẠCH THỰC NGHIỆM KHOA HỌC, QUY TRÌNH ĐỐI CHUẨN ĐA HẠT NHÂN VÀ TỐI ƯU SIÊU THAM SỐ

> **Cơ quan phụ trách:** Tab 4 (@tab_4) — ML/RL Engineer & Training Architect  
> **Thẩm định:** Tab 7 (@tab_7) — QA Auditor | **Phê duyệt:** Tab 1 (@tab_1) — Orchestrator  
> **Đồng thuận:** Tab 2 (@tab_2) — RL Researcher | Tab 3 (@tab_3) — Simulation Designer  
> **Trạng thái:** DRAFT / PHASE 1 (Sprint 1) | **Ngày ban hành:** 2026-10-30  

---

## 1. NGUYÊN TẮC KHOA HỌC VÀ CAM KẾT TRUNG THỰC DỮ LIỆU (SCIENTIFIC INTEGRITY PROTOCOL)

Nhằm tuân thủ tuyệt đối Hiến chương Trí tuệ Nhân tạo (`GEMINI.md`) của dự án RoboPilot, Tab 4 thiết lập giao thức nghiên cứu thực nghiệm với các cam kết bất biến:
1. **Không ngụy tạo số liệu (Zero Fake Data Tolerance):** Tuyệt đối cấm tạo dữ liệu đồ thị hội tụ giả lập hoặc tự gán kết quả thực nghiệm. Toàn bộ đồ thị và bảng số liệu phải được trích xuất trực tiếp từ nhật ký thực nghiệm (execution log runs).
2. **Quy chuẩn Đa hạt nhân (Multi-Seed Evaluation Protocol):** Bất kỳ báo cáo nào về thuật toán RL đều bắt buộc phải chạy qua tối thiểu **5 hạt nhân ngẫu nhiên độc lập (seeds)**. Không chấp nhận việc chọn lọc một hạt nhân may mắn (cherry-picking).
3. **Thống kê Khoa học:** Mọi đại lượng đo lường đều phải trình bày dưới dạng:
   $$\bar{X} \pm \sigma \quad (\text{Trung bình} \pm \text{Độ lệch chuẩn})$$
   kèm khoảng tin cậy $95\%$ Confidence Interval ($95\%\text{ CI}$).

---

## 2. MA TRẬN ĐỐI CHUẨN THUẬT TOÁN (ALGORITHM BENCHMARK MATRIX)

Để đánh giá toàn diện năng lực của mô hình Dueling Double DQN (D3QN), hệ thống thiết lập 5 tác tử đối chuẩn (benchmarking baselines):

| Tác tử (Agent) | Không gian Quan sát | Cơ chế ra quyết định | Vai trò đối chuẩn khoa học |
| :--- | :---: | :--- | :--- |
| **1. Random Walk** | Bất kỳ | Chọn ngẫu nhiên đều $a \sim \mathcal{U}\{0, 3\}$ | **Cận dưới tuyệt đối (Lower Bound):** Chứng minh bài toán không thể giải quyết bằng sự may rủi. |
| **2. A\* Pathfinding** | Toàn cục (Bản đồ ma trận) | Tìm đường ngắn nhất trên đồ thị tĩnh | **Cận trên lý thuyết (Oracle/Upper Bound):** Đánh giá độ tối ưu đường đi của AI so với đường đi ngắn nhất hoàn hảo. |
| **3. Tabular Q-Learning** | Tọa độ $(x_r, y_r)$ $\mathbb{R}^4$ | Bảng tra cứu rời rạc $Q(s, a)$ | Đánh giá năng lực của RL truyền thống và chứng minh điểm hạn chế khi sang bản đồ mới. |
| **4. Vanilla DQN** | Cảm biến $\mathbb{R}^7$ | Mạng MLP 2 lớp ẩn (không Dueling, không Double) | Đánh giá sự cần thiết của các cải tiến kiến trúc Dueling và Double DQN. |
| **5. Dueling Double DQN** | Cảm biến $\mathbb{R}^7$ | Mạng D3QN + Huber Loss + Polyak Averaging | **Tác tử hạt nhân chính thức của RoboPilot V1**. |

---

## 3. BỘ 4 CHỈ SỐ ĐO LƯỜNG CỐT LÕI (CORE EVALUATION METRICS)

Hệ thống đánh giá hiệu năng dựa trên 4 chỉ số định lượng:

### 3.1. Tỷ lệ Hoàn thành Nhiệm vụ (Success Rate - $SR$)
Tỷ lệ phần trăm các episodes mà robot điều hướng tới trạm sạc/đích thành công trước khi chạm ngưỡng bước tối đa ($MaxSteps$):
$$SR = \frac{1}{M} \sum_{i=1}^M \mathbb{I}(\text{reached\_goal}_i) \times 100\%$$
- **Mục tiêu nghiệm thu:** $SR \ge 95\%$ trên bản đồ Huấn luyện, $SR \ge 85\%$ trên bản đồ Đánh giá chưa từng thấy.

### 3.2. Hiệu suất Chiều dài Quỹ đạo (Path Length Optimality Ratio - $PLR$)
So sánh số bước di chuyển thực tế của robot với đường đi ngắn nhất lý thuyết tính toán bởi thuật toán $A^*$:
$$PLR = \frac{\text{Length}_{\text{Agent}}}{\text{Length}_{A^*}}$$
- $PLR = 1.0$: Đường đi đạt độ tối ưu tuyệt đối.
- $PLR \le 1.15$: Đường đi nằm trong giới hạn cho phép của MVP kho vận (không thừa quá 15% số bước).

### 3.3. Tần suất Va chạm (Collision Rate - $CR$)
Số lần robot va phải kệ hàng hoặc tường bao trung bình trong một episode:
$$CR = \frac{1}{M} \sum_{i=1}^M \text{collisions}_i$$
- **Mục tiêu an toàn:** $CR \le 0.1$ va chạm/episode khi mô hình đã hội tụ.

### 3.4. Phần thưởng Tích lũy Trung bình (Mean Cumulative Return - $\bar{R}$)
Tổng phần thưởng nhận được trong suốt một episode:
$$\bar{R} = \frac{1}{M} \sum_{i=1}^M \sum_{t=0}^{T_i} r_t$$
- Được vẽ kèm dải mờ biểu diễn độ lệch chuẩn $\pm 1\sigma$ trên đồ thị TensorBoard.

---

## 4. BỘ 5 RANDOM SEEDS CHUẨN HÓA VÀ GIAO THỨC ĐÁNH GIÁ (5-SEED PROTOCOL)

Toàn bộ các thí nghiệm kiểm chứng phải sử dụng danh sách 5 seeds cố định:
$$\mathcal{S}_{\text{eval}} = \{42, 1337, 2026, 9999, 777\}$$

### Quy trình Đánh giá Độc lập (Evaluation Loop)
1. Trong quá trình huấn luyện, mỗi $50$ episodes, tạm dừng cập nhật gradient.
2. Thiết lập chế độ suy luận tất định: $\epsilon = 0.0$ (hoàn toàn theo chính sách tham lam).
3. Cho tác tử chạy $10$ episodes đánh giá trên từng seed $\in \mathcal{S}_{\text{eval}}$ (tổng cộng 50 episodes kiểm định).
4. Ghi nhận trung bình và phương sai của $SR, PLR, CR, \bar{R}$.
5. Chuyển lại chế độ huấn luyện và tiếp tục.

---

## 5. THỰC NGHIỆM TRÊN 3 BẢN ĐỒ KHO CHUẨN CỦA TAB 3

Các thử nghiệm được tiến hành trên 3 bản đồ kho vận đã chốt trong hợp đồng với Tab 3 (`maps/benchmark_*.json`):

```
+----------------------------------------------------------------------------------------------------+
|                                    MA TRẬN KIỂM THỬ BẢN ĐỒ                                         |
+--------------------------+-----------------------+------------------------+------------------------+
| Thuộc tính               | 1. Easy Map (10x10)   | 2. Medium Map (15x15)  | 3. Hard Map (20x20)    |
+--------------------------+-----------------------+------------------------+------------------------+
| Kích thước               | 10 x 10 ô lưới        | 15 x 15 ô lưới         | 20 x 20 ô lưới         |
| Tỷ lệ vật cản            | 10% (Kệ thưa)         | 20% (Kệ song song)     | 30% (Hành lang zíc zắc)|
| Ngõ cụt (Dead-ends)      | Không có              | Ít (1 - 2 ngõ)         | Nhiều (Bẫy ngõ cụt)    |
| Giới hạn bước (MaxSteps) | 100 bước              | 200 bước               | 400 bước               |
| Mục tiêu kiểm chứng      | Kiểm chứng học cơ bản | Khả năng né chướng ngại| Khả năng thoát ngõ cụt |
+--------------------------+-----------------------+------------------------+------------------------+
```

---

## 6. KHÔNG GIAN TÌM KIẾM SIÊU THAM SỐ (HYPERPARAMETER SEARCH SPACE)

Quá trình tinh chỉnh siêu tham số áp dụng phương pháp Bayesian Optimization (thông qua thư viện Optuna) với không gian tìm kiếm sau:

| Siêu tham số | Ký hiệu | Miền tìm kiếm | Giá trị đề xuất (Baseline) | Cơ sở lựa chọn |
| :--- | :---: | :---: | :---: | :--- |
| **Learning Rate** | $\alpha$ | $[10^{-4}, 3 \times 10^{-3}]$ (Log scale) | $1.0 \times 10^{-3}$ | Tránh bước cập nhật quá lớn gây sụp đổ biểu diễn Q-network. |
| **Discount Factor** | $\gamma$ | $[0.95, 0.999]$ | $0.99$ | Khớp tuyệt đối với công thức thế năng PBRS của Tab 2. |
| **Target Update Polyak** | $\tau$ | $[0.001, 0.05]$ | $0.005$ | Giữ mục tiêu ổn định, không giật bậc thang. |
| **Replay Capacity** | $N$ | $[20000, 100000]$ | $50000$ | Đủ lớn để phân phối mẫu IID, vừa vặn bộ nhớ RAM hệ thống. |
| **Batch Size** | $B$ | $\{32, 64, 128\}$ | $64$ | Tối ưu thông lượng tính toán trên cả CPU và GPU Colab. |
| **Decay Steps** | $T_{\text{decay}}$ | $[15000, 40000]$ | $25000$ | Bảo đảm thời gian khám phá đủ rộng các ngóc ngách bản đồ. |

---

## 7. CẤU TRÚC GHI NHẬT KÝ THỰC NGHIỆM (EXPERIMENT LOGGING PROTOCOL)

Hệ thống huấn luyện xuất nhật ký dưới 2 định dạng bổ trợ nhau:

### 7.1. Định dạng Tệp cục bộ nhẹ: `train_metrics.jsonl`
Mỗi dòng là một JSON object độc lập, không phụ thuộc máy chủ web:
```json
{
  "timestamp": "2026-10-30T15:30:00Z",
  "episode": 100,
  "total_steps": 1420,
  "epsilon": 0.943,
  "episode_reward": 84.5,
  "steps_in_episode": 18,
  "goal_reached": true,
  "collision_count": 0,
  "loss_mean": 0.0421,
  "td_error_mean": 0.183
}
```

### 7.2. Định dạng Trực quan hóa: TensorBoard SummaryWriter
Ghi nhật ký đồ thị vào thư mục `runs/<experiment_id>/` với các thẻ (tags):
- `Rollout/CumulativeReward`
- `Rollout/EpisodeLength`
- `Rollout/SuccessRate_Rolling100`
- `Train/HuberLoss`
- `Train/Epsilon`
- `Train/QValueMean`

---

## 8. TIÊU CHUẨN NGHIỆM THU VÀ DỪNG SỚM (CONVERGENCE & EARLY STOPPING CRITERIA)

### 8.1. Điều kiện Hội tụ Thành công (Success Convergence Criteria)
Quá trình huấn luyện được công nhận là hội tụ khi thỏa mãn đồng thời:
1. **Rolling Success Rate:** Trung bình trượt qua 100 episodes đạt $\ge 95\%$.
2. **Stable Return:** Phương sai phần thưởng trung bình qua 100 episodes cuối $\sigma \le 5.0$.
3. **No Collision Streak:** 50 episodes liên tiếp không xảy ra va chạm trên bản đồ huấn luyện.

### 8.2. Điều kiện Dừng sớm do Thất bại (Early Stopping Safeguards)
Huấn luyện tự động ngắt để tiết kiệm chi phí tính toán GPU nếu:
1. **Bùng nổ Gradient (Gradient Explosion):** $\mathcal{L}_{\text{Huber}} > 100.0$ trong 10 batches liên tiếp.
2. **Bế tắc Không học (Stagnation):** Sau $500$ episodes mà Rolling Success Rate vẫn bằng $0\%$.
