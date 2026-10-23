"""生成 L4/L5 补充插图：fig4 齿轮受力与 Kv 曲线，fig5 应力-应变折线。"""
import os
import numpy as np

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("MPLCONFIGDIR", os.path.join(_ROOT, ".cache", "mplconfig"))
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Polygon

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 160

OUT = os.path.join(_ROOT, "courses", "dm1", "src", "assets", "figs")
os.makedirs(OUT, exist_ok=True)


def fig_gear_force():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))

    # ---------- (a) 齿面受力分解 ----------
    phi = np.radians(20)
    # 简化齿廓（梯形）
    tooth = Polygon(
        [[-0.9, 0], [-0.55, 1.6], [0.55, 1.6], [0.9, 0]],
        closed=True, facecolor="#dfe9f3", edgecolor="#2f4b66", lw=1.4, zorder=2,
    )
    ax1.add_patch(tooth)
    ax1.axhline(0, color="#8a99a8", lw=1.0, ls="--", zorder=1)
    ax1.text(-1.55, -0.18, "节线", fontsize=9, color="#5b6675")

    P = np.array([0.40, 1.15])          # 啮合点（右齿面）
    # 法向力 Wn 沿啮合线，与切向成 phi 角
    Wn = 1.75
    dirN = np.array([np.cos(phi), -np.sin(phi)])
    endN = P + Wn * dirN
    ax1.annotate("", xy=endN, xytext=P,
                 arrowprops=dict(arrowstyle="-|>", lw=2.0, color="#b03a2e"))
    ax1.text(*(endN + np.array([0.05, -0.28])), "$W_n$", fontsize=13, color="#b03a2e")

    endT = P + np.array([Wn * np.cos(phi), 0])
    ax1.annotate("", xy=endT, xytext=P,
                 arrowprops=dict(arrowstyle="-|>", lw=1.8, color="#1f618d"))
    ax1.text(*(endT + np.array([0.06, 0.10])), "$W_t$", fontsize=13, color="#1f618d")

    endR = P + np.array([0, -Wn * np.sin(phi)])
    ax1.annotate("", xy=endR, xytext=P,
                 arrowprops=dict(arrowstyle="-|>", lw=1.8, color="#1e8449"))
    ax1.text(*(endR + np.array([0.12, -0.12])), "$W_r$", fontsize=13, color="#1e8449")

    # 压力角标注（Wt 与 Wn 之间）
    r0 = 0.55
    arc = np.linspace(0, -phi, 30)
    ax1.plot(P[0] + r0 * np.cos(arc), P[1] + r0 * np.sin(arc), color="#7f8c8d", lw=1.1)
    ax1.text(P[0] + r0 * 1.02, P[1] - r0 * 0.55, r"$\phi=20^\circ$", fontsize=10, color="#5b6675")

    # 平行四边形式辅助线（虚线）
    ax1.plot([endT[0], endT[0]], [P[1], endR[1]], color="#95a5a6", lw=0.8, ls=":")
    ax1.plot([endR[0], endT[0]], [endR[1], endR[1]], color="#95a5a6", lw=0.8, ls=":")
    ax1.plot([P[0], P[0] + 2.1], [P[1], P[1]], color="#95a5a6", lw=0.9, ls=":")

    ax1.set_xlim(-1.4, 3.0)
    ax1.set_ylim(-0.9, 2.1)
    ax1.set_aspect("equal")
    ax1.axis("off")
    ax1.set_title("(a) 法向力分解：$W_r=W_t\\tan\\phi$，$W_n=W_t/\\cos\\phi$", fontsize=11)

    # ---------- (b) Kv - V ----------
    V = np.linspace(0, 25, 400)
    curves = [
        ((3.05 + V) / 3.05, "铸铁、铸造齿形", "#95a5a6", "-"),
        ((6.1 + V) / 6.1, "切削/铣齿", "#1f618d", "-"),
        ((3.56 + np.sqrt(V)) / 3.56, "滚齿/插齿", "#b03a2e", "-"),
        (np.sqrt((5.56 + np.sqrt(V)) / 5.56), "剃齿/磨齿", "#1e8449", "--"),
    ]
    for y, lab, c, ls in curves:
        ax2.plot(V, y, color=c, lw=1.9, ls=ls, label=lab)
    ax2.set_xlabel("节线速度 $V$ (m/s)", fontsize=10)
    ax2.set_ylabel("速度系数 $K_v$", fontsize=10)
    ax2.set_title("(b) SI 单位下的 $K_v$（$V$ 用 m/s）", fontsize=11)
    ax2.grid(alpha=0.3, ls=":")
    ax2.legend(fontsize=8.5, loc="upper left")
    ax2.set_xlim(0, 25)
    ax2.set_ylim(1.0, 2.6)

    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig4_gearforce.png"), bbox_inches="tight")
    plt.close(fig)


def fig_stress_strain():
    fig, ax = plt.subplots(figsize=(6.6, 4.4))
    # 折线：原点 -> 屈服 -> 抗拉 -> 断裂
    pts = [(0.0, 0.0), (2.0, 50.0), (5.0, 60.0), (5.0, 45.0)]
    xs, ys = zip(*pts)
    ax.plot(xs, ys, "-o", color="#1f618d", lw=2.0, ms=5, zorder=3)

    ax.annotate("屈服 $(\\varepsilon_y=2\\%,\\ \\sigma_y=50\\ \\mathrm{MPa})$",
                xy=(2.0, 50.0), xytext=(2.15, 24),
                arrowprops=dict(arrowstyle="->", lw=0.9, color="#5b6675"), fontsize=9)
    ax.annotate("抗拉 $(\\varepsilon_u=5\\%,\\ \\sigma_u=60\\ \\mathrm{MPa})$",
                xy=(5.0, 60.0), xytext=(2.45, 68),
                arrowprops=dict(arrowstyle="->", lw=0.9, color="#5b6675"), fontsize=9)
    ax.annotate("断裂 $\\sigma_f=45\\ \\mathrm{MPa}$",
                xy=(5.0, 45.0), xytext=(3.45, 38),
                arrowprops=dict(arrowstyle="->", lw=0.9, color="#5b6675"), fontsize=9)

    # 斜率标注
    ax.plot([0, 2.0], [0, 50.0], color="#b03a2e", lw=0.8, ls=":")
    ax.text(0.25, 34, "$E=\\sigma_y/\\varepsilon_y$\n$=2500\\ \\mathrm{MPa}$",
            fontsize=9, color="#b03a2e")

    ax.set_xlabel("工程应变 $\\varepsilon$ (%)", fontsize=10)
    ax.set_ylabel("工程应力 $\\sigma$ (MPa)", fontsize=10)
    ax.set_title("PLA 的工程应力–应变折线（2023 期末 Q7 画法）", fontsize=11)
    ax.grid(alpha=0.3, ls=":")
    ax.set_xlim(-0.3, 6.2)
    ax.set_ylim(0, 75)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig5_stressstrain.png"), bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    fig_gear_force()
    fig_stress_strain()
    print("ok")
