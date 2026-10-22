"""画一张凸轮-滚子摆杆的机构简图，用于解释自由度表的三种建模。"""
import os
import sys

import numpy as np

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("MPLCONFIGDIR", os.path.join(_ROOT, ".cache", "mplconfig"))
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon

sys.stdout.reconfigure(encoding="utf-8")
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 170

OUT = os.path.join(_ROOT, "assets", "figs")
os.makedirs(OUT, exist_ok=True)

O2 = np.array([1.45, 1.75])
O4 = np.array([4.05, 0.55])
TH = np.deg2rad(58.0)


def cam_r(t):
    return 0.78 + 0.16 * np.cos(t - 0.7)


r_contact = cam_r(TH)
R = 0.24
D = O2 + (r_contact + R) * np.array([np.cos(TH), np.sin(TH)])   # 滚子中心

fig, ax = plt.subplots(figsize=(6.8, 4.4))

# 地面
ax.plot([-0.4, 5.4], [0, 0], color="#7f8c8d", lw=2)
for x in np.arange(-0.4, 5.4, 0.22):
    ax.plot([x, x - 0.12], [0, -0.16], color="#7f8c8d", lw=0.8)

# 机架支柱（把两个铰支到地面上）
for piv in (O2, O4):
    ax.plot([piv[0], piv[0]], [0, piv[1]], color="#8a99a8", lw=6, solid_capstyle="butt", zorder=1)

# 凸轮
t = np.linspace(0, 2 * np.pi, 400)
prof = np.array([[O2[0] + cam_r(a) * np.cos(a), O2[1] + cam_r(a) * np.sin(a)] for a in t])
ax.add_patch(Polygon(prof, closed=True, facecolor="#dfe9f3", edgecolor="#1f618d", lw=1.8, zorder=2))
ax.plot(*O2, "o", color="#1f618d", ms=7, zorder=6)

# 摆杆
ax.plot([O4[0], D[0]], [O4[1], D[1]], "-", color="#2f4b66", lw=6, solid_capstyle="round", zorder=3)
ax.plot(*O4, "o", color="#2f4b66", ms=7, zorder=6)

# 滚子
ax.add_patch(Circle(D, R, facecolor="#f4d9c6", edgecolor="#b03a2e", lw=1.6, zorder=5))
ax.plot(*D, "o", color="#b03a2e", ms=4, zorder=7)

# 接触点
Pc = O2 + r_contact * np.array([np.cos(TH), np.sin(TH)])
ax.plot(*Pc, "o", color="#1e8449", ms=5, zorder=8)

# 标注
ax.annotate("1 机架（固定）", xy=(0.75, 0.0), xytext=(0.12, -0.66), fontsize=10,
            arrowprops=dict(arrowstyle="->", lw=0.9, color="#5b6675"))
ax.annotate("2 凸轮（主动，1 个输入）", xy=(O2[0] - 0.55, O2[1] - 0.55), xytext=(0.05, 2.95),
            fontsize=10, color="#1f618d",
            arrowprops=dict(arrowstyle="->", lw=0.9, color="#1f618d"))
ax.annotate("3 摆杆（从动）", xy=(3.05, 1.42), xytext=(3.15, 2.62), fontsize=10, color="#2f4b66",
            arrowprops=dict(arrowstyle="->", lw=0.9, color="#2f4b66"))
ax.annotate("4 滚子（可绕自身销轴自转）", xy=(D[0] + 0.16, D[1] + 0.18), xytext=(2.45, 3.35),
            fontsize=10, color="#b03a2e",
            arrowprops=dict(arrowstyle="->", lw=0.9, color="#b03a2e"))

ax.text(O2[0] - 0.05, O2[1] - 0.42, "$O_2$", fontsize=11, ha="right")
ax.text(O4[0] + 0.12, O4[1] - 0.26, "$O_4$", fontsize=11)
ax.text(D[0] + 0.30, D[1] + 0.02, "$C$", fontsize=11, color="#b03a2e")
ax.annotate("$D$（凸轮与滚子的接触点）", xy=(Pc[0] - 0.02, Pc[1] - 0.05), xytext=(0.02, 2.32),
            fontsize=9.5, color="#1e8449",
            arrowprops=dict(arrowstyle="->", lw=0.9, color="#1e8449"))

ax.text(0.05, 0.55,
        "$L=4$：机架 1、凸轮 2、摆杆 3、滚子 4\n"
        "转动副 $J_1$：$O_2,\\ O_4,\\ C$（3 个）\n"
        "接触 $D$：纯滚动按 $J_1$；允许滚+滑按 $J_2$",
        fontsize=9.8, va="top", color="#2f4b66",
        bbox=dict(boxstyle="round,pad=0.45", fc="#f3f8fc", ec="#cfd8e1"))

ax.set_xlim(-0.5, 5.5)
ax.set_ylim(-0.75, 3.7)
ax.set_aspect("equal")
ax.axis("off")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig8_cam_follower.png"), bbox_inches="tight")
print("ok")
