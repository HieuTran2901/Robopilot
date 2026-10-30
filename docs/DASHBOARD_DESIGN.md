# ROBOPILOT — ANALYTICS DASHBOARD & BENCHMARK DESIGN
# THIẾT KẾ PHÂN HỆ BIỂU ĐỒ KHOA HỌC & BẢNG ĐỐI CHUẨN THUẬT TOÁN

> **Cơ quan phụ trách:** Tab 6 (@tab_6) — Frontend & UX/UI Designer  
> **Thẩm định:** Tab 7 (@tab_7) — QA Auditor | **Phê duyệt:** Tab 1 (@tab_1) — Orchestrator  
> **Trạng thái:** PROPOSED / PHASE 1 (Sprint 1) | **Ngày ban hành:** 2026-10-30  

---

## 1. MỤC TIÊU & CHUẨN MỰC TRỰC QUAN HÓA KHOA HỌC (ANALYTICS OBJECTIVES)

Phân hệ Dashboard của RoboPilot không chỉ đơn thuần là các đồ thị minh họa, mà đóng vai trò là **Công cụ Thẩm định Khoa học (Empirical Verification Suite)** cho Kỹ sư AI/ML:
1. **Minh bạch hóa Quá trình Học tập của RL:** Giúp phát hiện tức thì hiện tượng Reward Hacking, chính sách rơi vào cực tiểu cục bộ (Local Minima) hoặc suy thoái chính sách (Policy Degradation).
2. **Tuân thủ Chuẩn mực Đa Hạt Nhân (Multi-Seed Validation):** Mọi biểu đồ đánh giá tổng kết bắt buộc thể hiện dải trung bình và độ lệch chuẩn ($\text{Mean} \pm \text{Std}$) trên tối thiểu 3 đến 5 hạt giống ngẫu nhiên (Seeds), tuyệt đối không dùng 1 seed thuận lợi để báo cáo.
3. **Đối chuẩn Trực diện với Baseline Tối ưu:** Mọi kết quả của agent RL (Q-Learning, D3QN) luôn được đặt cạnh thuật toán quy hoạch đường đi tối ưu hình học A\* (Oracle Optimal Path).

---

## 2. BỐ CỤC KHÔNG GIAN PHÂN HỆ DASHBOARD (DASHBOARD GRID LAYOUT)

```
+----------------------------------------------------------------------------------------------------+
|  📊 TRAINING & BENCHMARK ANALYTICS COCKPIT                                                         |
|  Filter: [Map: benchmark_hard ▼] [Seeds: All (3 seeds) ▼] [Smoothing: Window 20 ▼] [Export CSV]   |
+------------------------------------------------------------------+---------------------------------+
|  CHART 1: EPISODE REWARD & MOVING AVERAGE                        |  CHART 2: CONVERGENCE RATES     |
|  Reward                                                          |  Rate (%)                       |
|   100 |                           .--- Raw Reward                |  100% |              .-- Success|
|    50 |                 .--------'    -- Rolling MA (N=20)       |   50% |       .-----'           |
|     0 |        .-------'                                         |   20% |-------.                 |
|   -50 |_______'_________________________________________         |    0% |        '--.--- Collision|
|       0       200      400      600      800    1000 Episode     |       0    200   400  600  800  |
+------------------------------------------------------------------+---------------------------------+
|  CHART 3: STEP EFFICIENCY vs A* ORACLE (E = S_A* / S_Agent)      |  CHART 4: Q-VALUE DYNAMICS      |
|  Ratio E                                                         |  Q-Value Bar (Current State s)  |
|   1.0 |                           .--- Ideal Target (E=1.0)      |  UP   [███░░░░░░░] 2.1          |
|   0.8 |                 .--------'                               |  DOWN [█████████░] 6.8 [BEST]   |
|   0.6 |        .-------'                                         |  LEFT [█░░░░░░░░░] 0.5          |
|   0.4 |_______'                                                  |  RIGHT[████░░░░░░] 3.2          |
|       0       200      400      600      800    1000 Episode     |  Advantage V(s)=4.2, A*(s)=2.6  |
+------------------------------------------------------------------+---------------------------------+
|  CHART 5: MULTI-SEED REPRODUCIBILITY ENVELOPE (Mean ± Std)                                         |
|  Reward                                                                                            |
|   100 |                                    .------------------ Shaded Area: Mean ± 1.0 Std Dev     |
|    50 |                          .--------' (Seed 42, 101, 2024)                                   |
|     0 |                 .-------'           Solid Line: Mean Reward                                |
|   -50 |________________'                                                                           |
|       0       200      400      600      800    1000 1200 1400 1600 1800 2000 Episodes           |
+----------------------------------------------------------------------------------------------------+
|  COMPONENT 6: SCIENTIFIC BENCHMARK COMPARISON MATRIX                                               |
|  +--------------------+--------------+--------------+---------------+--------------+-------------+ |
|  | Algorithm          | Success Rate | Col. Rate    | Avg Steps     | Mean Reward  | Latency (ms)| |
|  +--------------------+--------------+--------------+---------------+--------------+-------------+ |
|  | A* (Oracle Path)   | 100.0% ± 0.0 |  0.0% ± 0.0  | 18.00 ± 0.00  | +82.0 ± 0.0  | 0.45 ± 0.05 | |
|  | Tabular Q-Learning |  86.5% ± 3.2 |  8.2% ± 1.5  | 23.40 ± 2.10  | +54.2 ± 4.8  | 0.02 ± 0.01 | |
|  | PyTorch D3QN       |  96.8% ± 1.4 |  1.4% ± 0.6  | 19.20 ± 0.85  | +78.6 ± 2.1  | 1.15 ± 0.12 | |
|  +--------------------+--------------+--------------+---------------+--------------+-------------+ |
```

---

## 3. THIẾT KẾ ĐẶC TẢ TỪNG BIỂU ĐỒ (DETAILED CHART SPECIFICATIONS)

### 3.1. Biểu đồ 1: Episode Reward & Moving Average (Hội tụ Phần thưởng)
- **Mục tiêu khoa học:** Theo dõi xu hướng tích lũy phần thưởng $G_t = \sum_{\tau=0}^T \gamma^\tau r_\tau$ qua các episode, kiểm chứng tính ổn định của hàm thưởng PBRS.
- **Loại biểu đồ:** Double Line Chart (Recharts `<LineChart>`).
- **Đường nét hiển thị:**
  * `raw_reward`: Nét mảnh màu lam nhạt `#38BDF8`, độ mờ `opacity=0.3` (biểu diễn độ dao động thô của exploration).
  * `rolling_ma`: Nét dày $2.5\text{px}$ màu Cyan sáng `#06B6D4`, tính toán qua cửa sổ trượt $N = 20$:
    $$\bar{R}_k = \frac{1}{N} \sum_{i=k-N+1}^k R_i$$
- **Cảnh báo bất thường (Heuristic Detection):** Nếu $\bar{R}_k$ sụt giảm đột ngột quá $30\%$ sau khi đã đạt trạng thái ổn định, hiển thị dấu chấm cảnh báo đỏ (Policy Collapse Warning).

### 3.2. Biểu đồ 2: Tỷ lệ Thành công vs Va chạm (Success Rate & Collision Rate)
- **Mục tiêu khoa học:** Đánh giá độ an toàn trong vận hành kho hàng (Zero Collision Target).
- **Loại biểu đồ:** Dual Area Chart chồng mờ (Recharts `<AreaChart>`).
- **Chỉ số đo đạc:**
  * `success_rate`: Diện tích màu xanh lục `#10B981` (Tỷ lệ về đích hợp lệ trong 50 episodes gần nhất).
  * `collision_rate`: Diện tích màu đỏ rực `#EF4444` (Tỷ lệ đâm vào kệ hàng hoặc tường trong 50 episodes gần nhất).
- **Tiêu chuẩn nghiệm thu MVP:** Tỷ lệ thành công phải vượt $\ge 95\%$, tỷ lệ va chạm duy trì $\le 2\%$.

### 3.3. Biểu đồ 3: Hiệu suất Bước đi so với Baseline A\* (Step Efficiency Metric)
- **Mục tiêu khoa học:** So sánh độ dài đường đi thực tế của AI Agent với độ dài đường đi ngắn nhất tìm được bởi thuật toán A\* trên cùng bản đồ.
- **Công thức Hiệu suất Hình học:**
  $$E(k) = \frac{L_{A^*}}{L_{\text{agent}}(k)} \in [0.0, 1.0]$$
  * $E = 1.0$: Agent đạt quỹ đạo tối ưu tuyệt đối tương đương A\*.
  * $E < 0.6$: Agent đi lòng vòng, có dấu hiệu lặp chu kỳ hoặc khám phá kém hiệu quả.
- **Loại biểu đồ:** `<LineChart>` với đường kẻ ngang tham chiếu (ReferenceLine) tại mốc lý tưởng $E = 1.0$ (màu vàng kim `#F59E0B`).

### 3.4. Biểu đồ 4: Phân phối Động lực Q-Value (Real-Time Action Q-Values)
- **Mục tiêu khoa học:** Giải thích quyết định tức thời của nơ-ron (Explainable AI / Policy Introspection) tại vị trí ô lưới hiện tại.
- **Loại biểu đồ:** Horizontal Bar Chart (Recharts `<BarChart layout="vertical">`).
- **Dữ liệu hiển thị:** 4 thanh tương ứng 4 actions $[Q(s, \text{UP}), Q(s, \text{DOWN}), Q(s, \text{LEFT}), Q(s, \text{RIGHT})]$.
- **Màu sắc động:**
  * Thanh cao nhất mang màu xanh ngọc lục bảo `#10B981` (Hành động Greedy được chọn).
  * Các thanh còn lại mang màu xám xanh `#4B5563`.
  * Nếu chênh lệch giữa Q lớn nhất và Q nhỏ nhất $< 0.1$, hiển thị nhãn "Uncertain Decision" (Trạng thái phân vân).

### 3.5. Biểu đồ 5: Dải Dao động Đa Hạt Nhân (Multi-Seed Scientific Envelope)
- **Mục tiêu khoa học:** Loại trừ tính may rủi trong khởi tạo trọng số mạng nơ-ron và vị trí sinh ngẫu nhiên.
- **Loại biểu đồ:** Shaded Area Range Chart (Recharts `<AreaChart>`).
- **Thuật toán dựng dải bao:**
  * Chạy huấn luyện qua $M$ seeds độc lập ($S = \{42, 101, 2024\}$).
  * Tại mỗi mốc episode $t$, tính giá trị trung bình $\mu(t)$ và độ lệch chuẩn $\sigma(t)$:
    $$\mu(t) = \frac{1}{M}\sum_{i=1}^M R_{i}(t), \quad \sigma(t) = \sqrt{\frac{1}{M-1}\sum_{i=1}^M (R_i(t) - \mu(t))^2}$$
  * Dải bao râm (Shaded Confidence Band): $[\mu(t) - \sigma(t), \mu(t) + \sigma(t)]$, màu Cyan mờ `rgba(6, 182, 212, 0.2)`.
  * Đường trung tâm $\mu(t)$: Nét liền màu `#06B6D4`.

---

## 4. BẢNG ĐỐI CHUẨN THUẬT TOÁN KHOA HỌC (BENCHMARK COMPARISON MATRIX)

Bảng đối chuẩn tổng hợp được thiết kế theo chuẩn bài báo hội nghị quốc tế (IEEE/NeurIPS format):

### 4.1. Cấu trúc Cột và Định dạng Dữ liệu

| Cột Chỉ số (Metric) | Đơn vị | Tiêu chí đánh giá | Công thức hiển thị |
| :--- | :---: | :---: | :---: |
| **Thuật toán (Algorithm)** | Tên chuỗi | - | A\* vs Tabular Q vs D3QN |
| **Tỷ lệ Về đích (Success Rate)** | $\%$ | Càng cao càng tốt ($\ge 95\%$) | $\text{Mean} \pm \text{Std}$ |
| **Tỷ lệ Va chạm (Collision Rate)** | $\%$ | Càng thấp càng tốt ($\le 2\%$) | $\text{Mean} \pm \text{Std}$ |
| **Số bước đi Trung bình (Avg Steps)**| Bước | Càng gần A\* càng tốt | $\text{Mean} \pm \text{Std}$ |
| **Hệ số Hiệu năng (Efficiency $E$)**| Điểm $[0, 1]$| Càng gần 1.0 càng tốt | $L_{A^*} / L_{\text{Agent}}$ |
| **Thời gian Suy luận (Inference Latency)**| $\text{ms}$ / tick | Càng nhỏ càng tốt ($< 5\text{ms}$) | Đo bằng High-res Timer |
| **Dung lượng Mô hình (Memory Size)**| $\text{KB}$ | Nhẹ, dễ nhúng edge | Checkpoint file size |

### 4.2. Chức năng Tương tác của Bảng (Interactive Features)
1. **Sortable Columns:** Cho phép click vào tiêu đề cột để sắp xếp tăng dần / giảm dần theo từng chỉ số.
2. **Seed Breakdown Drawer:** Bấm vào dòng thuật toán sẽ trượt mở rộng bảng chi tiết kết quả của từng seed con.
3. **Data Exporter:**
   * Nút `Export CSV`: Xuất toàn bộ bảng ra file `robopilot_benchmark_report_<timestamp>.csv`.
   * Nút `Export JSON`: Xuất telemetry chi tiết cho các notebook phân tích chuyên sâu (Jupyter/Colab).

---

## 5. THIẾT KẾ COMPONENT RECHARTS MẪU (RECHARTS SPECIFICATION CODE)

```tsx
// src/frontend/components/benchmark/RewardConvergenceChart.tsx
import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend
} from 'recharts';

interface MultiSeedPoint {
  episode: number;
  meanReward: number;
  upperStd: number; // mean + std
  lowerStd: number; // mean - std
  rawReward?: number;
}

interface Props {
  data: MultiSeedPoint[];
  showConfidenceInterval?: boolean;
}

export const RewardConvergenceChart: React.FC<Props> = ({
  data,
  showConfidenceInterval = true
}) => {
  return (
    <div className="w-full h-72 bg-gray-900 border border-gray-800 rounded-lg p-3">
      <div className="flex justify-between items-center mb-2">
        <h4 className="text-xs font-semibold text-gray-200 uppercase tracking-wider">
          Episode Convergence Envelope (Mean ± 1σ)
        </h4>
        <span className="text-xs font-mono text-cyan-400">3 Seeds Average</span>
      </div>
      <ResponsiveContainer width="100%" height="88%">
        <ComposedChart data={data} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
          <XAxis
            dataKey="episode"
            stroke="#6B7280"
            fontSize={11}
            tickLine={false}
          />
          <YAxis
            stroke="#6B7280"
            fontSize={11}
            tickLine={false}
          />
          <Tooltip
            contentStyle={{ backgroundColor: '#111827', borderColor: '#374151' }}
            itemStyle={{ fontSize: '12px' }}
          />
          <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '4px' }} />
          {showConfidenceInterval && (
            <Area
              name="Std Envelope (±1σ)"
              dataKey="upperStd"
              stroke="none"
              fill="#06B6D4"
              fillOpacity={0.15}
            />
          )}
          <Line
            name="Mean Reward (μ)"
            type="monotone"
            dataKey="meanReward"
            stroke="#06B6D4"
            strokeWidth={2}
            dot={false}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};
```
