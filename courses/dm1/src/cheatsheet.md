# 公式速查卡（按 L1–L5 排列，考前 30 分钟看这一份）

> 符号与正文一致：传动比 $u$、齿数 $z$、径节 $P_d$、周节 $p_c$、齿宽 $b_f$、中心距 $a_w$、顶隙 $h_c$、安全系数 $n_s$、弹性系数 $Z_E$、曲率半径 $\rho_1,\rho_2$、传动角 $\mu$、压力角 $\phi$。

> 建议打印成一页 A4 正反面。带 ★ 的是"闭眼也要写出来"的式子。

---

## L1 机构与四杆基础

| 项目 | 公式 |
| --- | --- |
| ★ 自由度 | $M=3(L-1)-2J_1-J_2$ |
| 总自由度 / 总约束 | $3(L-1)$ / $2J_1+J_2$ |
| 传动角 | $\mu=\angle BCD$（取锐角）；$F$ 为连杆力，$F_t=F\sin\mu$，$F_r=F\cos\mu$ |
| 许用传动角 | $30^\circ\le\mu\le150^\circ$，工程 $[\mu]\ge40^\circ$ |
| ★ Grashof | $\ell_{\min}+\ell_{\max}<\ell_p+\ell_q$；$=$ 变向点；$>$ 非 Grashof |
| 类型 | 最短杆为连架杆→曲柄摇杆；为机架→双曲柄；为连杆→双摇杆 |
| 机械效益 | $MA=F_{out}/F_{in}=v_{in}/v_{out}$ |

---

## L2 四杆分析与综合

| 项目 | 公式 |
| --- | --- |
| ★ 闭环方程 | $a e^{i\theta}+b e^{i\psi}=d+c e^{i\varphi}$ |
| 位置（几何法） | $BD^2=a^2+d^2-2ad\cos\theta$，$\cos\angle CBD=\dfrac{b^2+BD^2-c^2}{2bBD}$ |
| 位置（代数） | $\lambda_1\cos\varphi+\lambda_2\sin\varphi+\lambda_3=0$ |
| 系数 | $\lambda_1=2c(d-a\cos\theta)$，$\lambda_2=-2ac\sin\theta$，$\lambda_3=d^2+c^2+a^2-b^2-2ad\cos\theta$ |
| 解 | $t=\tan\dfrac{\varphi}{2}=\dfrac{-\lambda_2\pm\sqrt{\lambda_1^2+\lambda_2^2-\lambda_3^2}}{\lambda_3-\lambda_1}$，$\varphi=2\arctan t$ |
| ★ 速度 | $\omega_3=-\dfrac{a\omega_2\sin(\varphi-\theta)}{b\sin(\varphi-\psi)}$，$\omega_4=-\dfrac{a\omega_2\sin(\psi-\theta)}{c\sin(\varphi-\psi)}$ |
| 瞬心 | $\dfrac{\omega_3}{\omega_2}=\dfrac{P_{12}P_{23}}{P_{13}P_{23}}$ |
| ★ 二元组方程 | $W\left(e^{i\beta_j}-1\right)+Z\left(e^{i\alpha_j}-1\right)=\delta_j$ |
| 铰点还原 | $A_1=PP_1-Z$，$A_0=A_1-W$ |
| Freudenstein | $k_1\cos\varphi-k_2\cos\theta+k_3=\cos(\varphi-\theta)$ |
| 系数 | $k_1=\dfrac{d}{a}$，$k_2=\dfrac{d}{c}$，$k_3=\dfrac{d^2+c^2+a^2-b^2}{2ac}$ |
| 反解 | $d=k_1a$，$c=d/k_2$，$b=\sqrt{a^2+c^2+d^2-2ack_3}$ |

---

## L3 电机与传动

| 项目 | 公式 |
| --- | --- |
| ★ 电机三式 | $E=K_b\omega$，$T=K_TI$，$V_s=E+IR$ |
| ★ 机械特性 | $T_m=\dfrac{V_sK_T}{R_a}-\dfrac{K_TK_b}{R_a}\omega=T_s\left(1-\dfrac{\omega}{\omega_0}\right)$ |
| 堵转 / 空载 | $T_s=\dfrac{V_sK_T}{R_a}$，$\omega_0=\dfrac{V_s}{K_b}$，$I_s=\dfrac{V_s}{R_a}$ |
| 斜率 | $-\dfrac{K_TK_b}{R_a}$（与电压无关） |
| 功率 / 效率 | $P=T\omega$，$\eta=\dfrac{P_{out}}{P_{in}}=\dfrac{\omega}{\omega_0}$（理想） |
| 最大功率点 | $\omega=\omega_0/2$，$T=T_s/2$，$P_{\max}=V_s^2/(4R)$ |
| ★ 传动比 | $u=\dfrac{\omega_m}{\omega_o}=\dfrac{r_o}{r_m}$（运动学，恒成立）；$T_o=u\eta T_m$，仅 $\eta=1$ 时 $T_o/T_m=u$ |
| 转速换算 | $\omega=\dfrac{2\pi n}{60}$，$T(\text{N·m})=9550\dfrac{P(\text{kW})}{n(\text{rpm})}$ |
| ★ 齿轮参数 | $d=mz$，$p_c=\pi m$，$P_d=z/d$，$m[\text{mm}]=25.4/P_d$，$d_b=d\cos\phi$ |
| 齿顶 / 齿根 | $d_a=d+2m$，$d_f=d-2.5m$ |
| ★ 中心距 | $a_w=\dfrac{m(z_1+z_2)}{2}$ |
| 重合度 | $\varepsilon=\dfrac{\sqrt{r_{a1}^2-r_{b1}^2}+\sqrt{r_{a2}^2-r_{b2}^2}-C\sin\phi}{\pi m\cos\phi}$ |
| 根切 | $z_{\min}=\dfrac{2h_a^*}{\sin^2\phi}\approx17$ |
| ★ 轮系 | $\dfrac{\omega_{in}}{\omega_{out}}=\dfrac{\prod z_{\text{driven}}}{\prod z_{\text{driving}}}$ |
| 外/内啮合 | 外：$\omega_b=-\omega_aN_a/N_b$；内：取正 |
| ★ 行星 | $\omega_s z_s+\omega_r z_r=\omega_c(z_r+z_s)$，$z_r=2z_p+z_s$ |
| 行星杠杆 | $\omega_c=\dfrac{z_s}{z_r+z_s}\omega_s+\dfrac{z_r}{z_r+z_s}\omega_r$ |
| 齿圈固定 | $u_{sc}=1+\dfrac{z_r}{z_s}$ |
| 太阳轮固定 | $u_{rc}=1+\dfrac{z_s}{z_r}$ |
| 系杆固定 | $u_{sr}=-\dfrac{z_r}{z_s}$ |
| 谐波 | $u_h=\dfrac{z_f}{z_g-z_f}=\dfrac{z_f}{2}$（刚轮固定，反向） |

---

## L4 设计流程、材料、齿轮几何

| 项目 | 要点 |
| --- | --- |
| 设计流程 | 需求→调研→概念→筛选→详细设计→分析→样机→定型 |
| 选材指标 | 强度、刚度、密度、硬度、韧性、耐蚀、热膨胀、可加工性、成本 |
| 材料族 | 金属 / 陶瓷玻璃 / 高分子 / 复合材料 |
| 强度 vs 刚度 | $\sigma\le[\sigma]$（怕断） vs $\delta\le[\delta]$（怕变形，$E$ 决定） |
| 应力–应变 | $E=\sigma_y/\varepsilon_y$；$\sigma_y,\sigma_u,\sigma_f,\varepsilon_y,\varepsilon_u$ |
| 标准齿比例 | $h_a=m$，$h_f=1.25m$，$h_c=0.25m$，$h=2.25m$ |
| 模数换算 | $m[\text{mm}]=25.4/P$ |
| 齿宽经验 | $b_f=(6\text{–}12)m$ |
| 传动比分配 | 每级 $<10$，$u=\prod u_k$ |

---

## L5 齿轮受力与强度

| 项目 | 公式 |
| --- | --- |
| ★ 分力 | $W_r=W_t\tan\phi$，$W_n=W_t/\cos\phi$ |
| 马力–转矩 | $HP=\dfrac{T\cdot RPM}{63025}$ |
| 节线速度 | $V=\dfrac{\pi dn}{60}$（m/s，$d$ 用 m） |
| ★ 传递载荷（US） | $W_t=33000\dfrac{H}{V}$（hp，ft/min，lbf） |
| ★ 传递载荷（SI） | $W_t=\dfrac{60000H}{\pi dn}$（kW，mm，rpm → **kN**） |
| ★ 弯曲（US） | $\sigma=\dfrac{K_vW_tP}{FY}$ |
| ★ 弯曲（SI） | $\sigma=\dfrac{K_vW_t}{FmY}$ |
| $K_v$（US） | 铸造 $\dfrac{600+V}{600}$；铣齿 $\dfrac{1200+V}{1200}$；滚齿 $\dfrac{50+\sqrt V}{50}$；磨齿 $\sqrt{\dfrac{78+\sqrt V}{78}}$ |
| $K_v$（SI） | $3.05$；$6.1$；$3.56$；$5.56$（形式同上，$V$ 用 m/s） |
| ★ 曲率半径 | $\rho_1=\dfrac{d_p\sin\phi}{2}$，$\rho_2=\dfrac{d_g\sin\phi}{2}$ |
| ★ 弹性系数 | $Z_E=\left[\dfrac{1}{\pi\left(\dfrac{1-\nu_p^2}{E_p}+\dfrac{1-\nu_g^2}{E_g}\right)}\right]^{1/2}$ |
| ★ 接触应力 | $\sigma_C=-C_p\left[\dfrac{K_vW_t}{F\cos\phi}\left(\dfrac{1}{r_1}+\dfrac{1}{r_2}\right)\right]^{1/2}$ |
| 接触安全系数 | $n_s=\left(\dfrac{S_C}{\sigma_C}\right)^2$ |
| 弯曲安全系数 | $n_s=\dfrac{\sigma_{\text{allow}}}{\sigma}$ |
| 铸铁 $S_C$ | $S_C\approx0.32H_B$ kpsi |

---

## 常用数值与常数

| 量 | 值 |
| --- | --- |
| $\sin20^\circ$ / $\cos20^\circ$ / $\tan20^\circ$ | 0.3420 / 0.9397 / 0.3640 |
| $\operatorname{inv}20^\circ$ | 0.01490 |
| $2\pi/60$ | 0.10472 |
| $60/(2\pi)$ | 9.5493 |
| 1 hp | 746 W = 33000 ft·lbf/min |
| 1 in | 25.4 mm |
| 1 Mpsi | 6.895 GPa |
| 1 kpsi | 6.895 MPa |

---

## 中英术语对照（英文卷必备）

| 中文 | English | 中文 | English |
| --- | --- | --- | --- |
| 机构 | mechanism | 运动简图 | kinematic diagram |
| 构件 / 运动副 | link / joint | 自由度 | degree of freedom (mobility) |
| 机架 | ground link / frame | 连杆 | coupler |
| 曲柄 / 摇杆 | crank / rocker | 滑块 | slider |
| 传动角 | transmission angle | 压力角 | pressure angle |
| 死点 / 变向点 | toggle / change point | 反演 | inversion |
| 圆点 / 圆心点 | circle point / center point | 精确点 | precision point |
| 刚体导引 | motion generation | 轨迹生成 | path generation |
| 函数生成 | function generation | 二元组 | dyad |
| 渐开线 | involute | 基圆 | base circle |
| 分度圆 | pitch circle | 模数 / 径节 | module / diametral pitch |
| 周节 | circular pitch | 齿顶高 / 齿根高 | addendum / dedendum |
| 顶隙 | clearance | 重合度 | contact ratio |
| 根切 | undercut | 轮系 | gear train |
| 行星轮 / 太阳轮 | planet / sun gear | 内齿圈 | ring gear |
| 系杆 | carrier | 谐波减速器 | harmonic drive |
| 柔轮 / 刚轮 | flexspline / circular spline | 波发生器 | wave generator |
| 轮齿折断 | tooth breakage | 点蚀 | pitting |
| 胶合 / 磨损 | scoring / wear | 疲劳 | fatigue |
| 传递载荷 | transmitted load | 节线速度 | pitch-line velocity |
| 齿宽 | face width | 齿形系数 | Lewis form factor |
| 带 / 链 | belt / chain | 滚子链 | roller chain |
| 正应力 / 切应力 | normal / shear stress | 屈服 / 抗拉 | yield / ultimate |

---

## 考场时间分配（100 分钟）

| 题型 | 时间 |
| --- | --- |
| 自由度 + 类型判断 | 12 分钟 |
| 四杆位置/速度 + 传动角 | 18 分钟 |
| 电机工作点 + 传动比 | 18 分钟 |
| 齿轮几何 + 轮系/行星 | 18 分钟 |
| 齿轮受力/弯曲/接触 | 18 分钟 |
| 材料/设计流程简答 | 8 分钟 |
| 检查与补公式 | 8 分钟 |

> 写计算题永远按"**已知 → 公式 → 代入 → 结果 → 单位**"五步；单位错是最常见的丢分点。
