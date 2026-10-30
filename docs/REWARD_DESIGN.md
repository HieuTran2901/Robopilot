# ROBOPILOT — REWARD FUNCTION DESIGN & MATHEMATICAL PROOFS
# THIẾT KẾ HÀM THƯỞNG VÀ CHỨNG MINH TOÁN HỌC CHỐNG HIỆN TƯỢNG REWARD HACKING

> **Cơ quan phụ trách:** Tab 2 (@tab_2) — Robotics & RL Research Specialist  
> **Thẩm định:** Tab 7 (@tab_7) — QA Auditor | **Phê duyệt:** Tab 1 (@tab_1) — Orchestrator  
> **Trạng thái:** DRAFT / PHASE 1 (Sprint 1) | **Ngày ban hành:** 2026-10-30  

---

## 1. BÀI TOÁN THIẾT KẾ PHẦN THƯỞNG: PHẦN THƯỞNG THƯA (SPARSE) vs DẦY (DENSE)

Trong học tăng cường cho xe tự hành (AMR), việc thiết kế hàm thưởng $\mathcal{R}(s, a, s')$ quyết định trực tiếp việc robot có học được hay không:
- **Nếu dùng Phần thưởng Thưa (Sparse Reward):** Robot chỉ nhận $+100$ khi đến đích, $0$ ở mọi bước khác.
  * *Hệ quả:* Không gian tìm kiếm quá rộng, robot đi ngẫu nhiên hàng triệu bước vẫn không thể chạm tới đích $\to$ Mạng nơ-ron không nhận được tín hiệu gradient để cập nhật.
- **Nếu dùng Phần thưởng Dầy ngây thơ (Naive Dense Shaping):** Cộng $+1$ mỗi khi robot tiến gần mục tiêu:
  $$r_{\text{naive}} = \text{dist}(s, g) - \text{dist}(s', g)$$
  * *Hệ quả (Reward Cycling / Reward Hacking):* Robot sẽ học cách đi tới rồi lùi lại liên tục giữa 2 ô liền kề để nhận điểm thưởng vô tận mà không bao giờ chịu đi về đích!

---

## 2. ĐỊNH LÝ SHAPING PHẦN THƯỞNG DỰA TRÊN THẾ NĂNG (POTENTIAL-BASED REWARD SHAPING - PBRS)

Để giải quyết triệt để nghịch lý trên, RoboPilot áp dụng định lý toán học nền tảng của **Ng, Harada & Russell (ICML 1999)**:

### Định lý (Bảo toàn Chính sách Tối ưu)
Cho một MDP nguyên bản $M = (\mathcal{S}, \mathcal{A}, \mathcal{P}, \mathcal{R}, \gamma)$. Xét một MDP biến đổi $M' = (\mathcal{S}, \mathcal{A}, \mathcal{P}, \mathcal{R}', \gamma)$ với hàm thưởng:
$$\mathcal{R}'(s, a, s') = \mathcal{R}(s, a, s') + F(s, s')$$

Hàm $F(s, s')$ bảo toàn toàn bộ chính sách tối ưu ($\pi^*_{M'} = \pi^*_M$) nếu và chỉ nếu $F$ có dạng hiệu thế năng chiết khấu:
$$F(s, s') = \gamma \Phi(s') - \Phi(s)$$
trong đó $\Phi: \mathcal{S} \to \mathbb{R}$ là một hàm thế năng thực bất kỳ xác định trên không gian trạng thái.

### Chứng minh Toán học (Proof of Invariance)
Xét phương trình Bellman trên MDP biến đổi $M'$:
$$Q^*_{M'}(s, a) = \mathcal{R}(s, a, s') + \gamma \Phi(s') - \Phi(s) + \gamma \sum_{s'} \mathcal{P}(s' \mid s, a) \max_{a'} Q^*_{M'}(s', a')$$

Đặt hàm phụ trợ:
$$\hat{Q}(s, a) = Q^*_{M'}(s, a) + \Phi(s)$$
Thay vào phương trình trên:
$$\hat{Q}(s, a) - \Phi(s) = \mathcal{R}(s, a, s') + \gamma \Phi(s') - \Phi(s) + \gamma \sum_{s'} \mathcal{P}(s' \mid s, a) \max_{a'} \left[ \hat{Q}(s', a') - \Phi(s') \right]$$

Triệt tiêu $-\Phi(s)$ ở hai vế:
$$\hat{Q}(s, a) = \mathcal{R}(s, a, s') + \gamma \sum_{s'} \mathcal{P}(s' \mid s, a) \max_{a'} \hat{Q}(s', a')$$

Phương trình này đồng nhất tuyệt đối với phương trình Bellman của MDP gốc $M$, suy ra:
$$\hat{Q}(s, a) = Q^*_M(s, a) \implies Q^*_{M'}(s, a) = Q^*_M(s, a) - \Phi(s)$$

Vì $\Phi(s)$ là hằng số đối với toán tử $\arg\max_a$:
$$\arg\max_{a \in \mathcal{A}} Q^*_{M'}(s, a) = \arg\max_{a \in \mathcal{A}} \left[ Q^*_M(s, a) - \Phi(s) \right] = \arg\max_{a \in \mathcal{A}} Q^*_M(s, a) = \pi^*(s)$$
$\blacksquare$ **Kết luận:** Hàm thế năng định hướng robot học cực nhanh nhưng **không bao giờ làm thay đổi đường đi tối ưu**!

---

## 3. THIẾT KẾ CỤ THỂ HÀM THƯỞNG CHO ROBOPILOT V1

### 3.1. Định nghĩa Hàm Thế năng ($\Phi$)
Trong môi trường lưới kho hàng 2D với 4 hướng di chuyển trực giao, hàm thế năng tối ưu nhất là **Khoảng cách Manhattan âm** chuẩn hóa:
$$\Phi(s) = - \frac{|x_r - x_g| + |y_r - y_g|}{W + H - 2}$$
- Tại đích ($s = s_{\text{goal}}$): Khoảng cách bằng $0 \implies \Phi(s_{\text{goal}}) = 0$ (Cực đại thế năng).
- Càng xa đích: Khoảng cách càng lớn $\implies \Phi(s) < 0$ (Thế năng càng thấp).

### 3.2. Cấu trúc Hàm thưởng Tổng thể ($r_t$)
Phần thưởng tức thời tại bước $t$ được tính bằng tổng:
$$r_t = R_{\text{env}}(s_t, a_t, s_{t+1}) + F(s_t, s_{t+1})$$

| Thành phần phần thưởng | Giá trị số trị | Điều kiện kích hoạt | Mục đích kỹ thuật |
| :--- | :---: | :--- | :--- |
| **Đến đích ($R_{\text{goal}}$)** | $+100.0$ | $s_{t+1} == s_{\text{goal}}$ (`terminated = True`) | Khích lệ mục tiêu tối thượng. |
| **Va chạm ($R_{\text{collision}}$)**| $-10.0$ | Robot đi vào tường / kệ hàng (Robot giữ nguyên vị trí) | Phạt nặng hành vi mất an toàn. |
| **Chi phí bước đi ($R_{\text{step}}$)**| $-0.5$ | Mỗi bước di chuyển hợp lệ | Ép robot chọn đường ngắn nhất, triệt tiêu động tác thừa. |
| **Hết thời gian ($R_{\text{timeout}}$)**| $-20.0$ | $\text{steps} \ge \text{MaxSteps}$ (`truncated = True`) | Phạt hành vi đi lạc, bế tắc. |
| **Shaping ($F(s_t, s_{t+1})$)** | $\gamma \Phi(s_{t+1}) - \Phi(s_t)$ | Mọi bước chuyển trạng thái | Hướng dẫn gradient dẫn đường không gây hacking. |

---

## 4. PHÂN TÍCH ĐỐI KHÁNG: CHỨNG MINH TRIỆT TIÊU HIỆN TƯỢNG ĐI LẶP VÒNG TRÒN

Xét trường hợp robot có hành vi "ăn gian" bằng cách dao động giữa 2 trạng thái kề nhau:
$$s_0 \xrightarrow{a_1} s_1 \xrightarrow{a_2} s_0$$

Giả sử bước $a_1$ đưa robot lại gần đích hơn ($\Phi(s_1) > \Phi(s_0)$).
- **Tại bước 1 ($s_0 \to s_1$):**
  $$r_1 = R_{\text{step}} + \gamma \Phi(s_1) - \Phi(s_0) = -0.5 + \gamma \Phi(s_1) - \Phi(s_0)$$
- **Tại bước 2 ($s_1 \to s_0$):**
  $$r_2 = R_{\text{step}} + \gamma \Phi(s_0) - \Phi(s_1) = -0.5 + \gamma \Phi(s_0) - \Phi(s_1)$$

Tổng phần thưởng sau chu trình 2 bước:
$$\Delta R = r_1 + r_2 = 2 \cdot R_{\text{step}} + (\gamma - 1)\Phi(s_1) + (\gamma - 1)\Phi(s_0)$$
Vì $\gamma = 0.99 < 1 \implies (\gamma - 1) = -0.01 < 0$, và $\Phi(s) \le 0 \implies (\gamma - 1)\Phi(s) \ge 0$:
$$\Delta R = -1.0 + 0.01 \cdot \left[ (-\Phi(s_1)) + (-\Phi(s_0)) \right]$$
Vì $\Phi(s)$ chuẩn hóa trong đoạn $[-1, 0]$ nên $(-\Phi(s)) \le 1$:
$$\Delta R \le -1.0 + 0.01 \cdot (1 + 1) = -0.98 < 0$$

$\implies$ **Kết luận khoa học:** Mỗi lần robot đi qua lại giữa 2 ô, nó bị **lỗ ròng ít nhất $-0.98$ điểm**. Mạng nơ-ron nhận tín hiệu phạt liên tục và sẽ dập tắt hoàn toàn hành vi dao động này chỉ sau vài chục episodes!

---

## 5. THÔNG SỐ ĐỀ XUẤT CHO TAB 3 VÀ TAB 4

```json
{
  "reward_config": {
    "goal_reward": 100.0,
    "collision_penalty": -10.0,
    "step_penalty": -0.5,
    "timeout_penalty": -20.0,
    "potential_scale": 1.0,
    "discount_gamma": 0.99,
    "max_steps_factor": 2.5
  }
}
```

*Tài liệu này được bàn giao chính thức cho **Tab 3 (@tab_3)** để tích hợp vào hàm `step()` của `WarehouseGridEnv` và cho **Tab 7 (@tab_7)** để thiết kế kịch bản test chống reward hacking.*
