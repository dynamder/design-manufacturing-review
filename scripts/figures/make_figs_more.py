"""补充两张示意图：杠杆类比（行星轮系）与三点图解法（模拟卷 Q4 答案）。"""
import os
import sys

import numpy as np

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("MPLCONFIGDIR", os.path.join(_ROOT, ".cache", "mplconfig"))
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

sys.stdout.reconfigure(encoding="utf-8")
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 160

OUT = os.path.join(_ROOT, "assets", "figs")
os.makedirs(OUT, exist_ok=True)


def lever():
    S, P, R = 20.0, 30.0, 80.0
    ws, wr = 100.0, 0.0
    wc = ws * S / (R + S)
    xs = [0.0, S, R + S]          # sun, carrier, ring
    ys = [ws, wc, wr]
    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    ax.axhline(0, color="#8a99a8", lw=2.0)
    # 速度向量
    for x, y, lab, col in ((xs[0], ys[0], "太阳轮 $\\omega_s$", "#b03a2e"),
                           (xs[1], ys[1], "系杆 $\\omega_c$", "#1f618d"),
                           (xs[2], ys[2], "齿圈 $\\omega_r=0$", "#1e8449")):
        ax.annotate("", xy=(x, y), xytext=(x, 0),
                    arrowprops=dict(arrowstyle="-|>", lw=2.0, color=col))
        ax.plot([x], [0], "o", color="#2f4b66", ms=6, zorder=4)
        ax.text(x, -8, lab, ha="center", va="top", fontsize=9.5, color=col)
    # 顶点连线（杠杆）
    ax.plot([xs[0], xs[2]], [ys[0], ys[2]], "--", color="#7f8c8d", lw=1.2)
    ax.plot([xs[1]], [ys[1]], "o", color="#b03a2e", ms=6, zorder=5)
    ax.annotate("$\\omega_c=\\dfrac{S}{R+S}\\omega_s$", xy=(xs[1], ys[1]),
                xytext=(52, 70), fontsize=10,
                arrowprops=dict(arrowstyle="->", lw=0.9, color="#5b6675"))
    ax.set_xlabel("到太阳轮中心的距离（力臂）", fontsize=10)
    ax.set_ylabel("角速度", fontsize=10)
    ax.set_title("行星轮系的杠杆类比：三个节点在同一条直线上（2 个自由度）", fontsize=11)
    ax.set_xlim(-12, R + S + 12)
    ax.set_ylim(-22, 112)
    ax.grid(alpha=0.25, ls=":")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig6_lever.png"), bbox_inches="tight")
    plt.close(fig)


def circum(pts):
    pts = np.array(pts, dtype=float)
    A = np.array([[2 * (p[0] - pts[0][0]), 2 * (p[1] - pts[0][1])] for p in pts[1:]])
    b = np.array([p[0] ** 2 + p[1] ** 2 - (pts[0][0] ** 2 + pts[0][1] ** 2) for p in pts[1:]])
    return np.linalg.solve(A, b)


def pb3():
    A = [(0, 0), (40, 15), (70, 45)]
    B = [(100, 0), (120, 30), (160, 55)]
    A0, B0 = circum(A), circum(B)
    fig, ax = plt.subplots(figsize=(7.2, 5.6))

    for pts, c, col, name in ((A, A0, "#1f618d", "A"), (B, B0, "#b03a2e", "B")):
        r = np.hypot(pts[0][0] - c[0], pts[0][1] - c[1])
        ax.add_patch(Circle(c, r, fill=False, ls="--", lw=1.0, color=col, alpha=0.65))
        for k, p in enumerate(pts, 1):
            ax.plot(*p, "o", color=col, ms=5, zorder=5)
            ax.text(p[0] + 2.2, p[1] + 1.4, f"${name}_{k}$", fontsize=9, color=col)
        ax.plot(*c, "s", color=col, ms=7, zorder=6)
        ax.text(c[0] + 2.5, c[1] + 2.0, f"${name}_0$", fontsize=10, color=col)
        # 两条中垂线
        for p, q in ((pts[0], pts[1]), (pts[0], pts[2])):
            mid = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
            d = np.array([q[0] - p[0], q[1] - p[1]], dtype=float)
            d /= np.linalg.norm(d)
            n = np.array([-d[1], d[0]])
            ax.plot([mid[0] - 55 * n[0], mid[0] + 55 * n[0]],
                    [mid[1] - 55 * n[1], mid[1] + 55 * n[1]],
                    "-", color=col, lw=0.8, alpha=0.5)

    # 位置 1 的机构
    ax.plot([A0[0], A[0][0]], [A0[1], A[0][1]], "-", color="#1f618d", lw=2.2)
    ax.plot([B0[0], B[0][0]], [B0[1], B[0][1]], "-", color="#b03a2e", lw=2.2)
    ax.plot([A[0][0], B[0][0]], [A[0][1], B[0][1]], "-", color="#2f4b66", lw=2.6)

    ax.set_aspect("equal")
    ax.set_xlim(-45, 215)
    ax.set_ylim(-65, 130)
    ax.grid(alpha=0.25, ls=":")
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("y (mm)")
    ax.set_title("三个位置：两条中垂线交于固定铰，$A_0=(-14.5,\\ 99.5)$，$B_0=(190.9,\\ -38.9)$", fontsize=10.5)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig7_pb3.png"), bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    lever()
    pb3()
    print("ok")
