"""画四杆机构的两条装配支路（同一 θ 下的两个 C 解）。"""
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
plt.rcParams["figure.dpi"] = 170

OUT = os.path.join(_ROOT, "courses", "dm1", "src", "assets", "figs")
os.makedirs(OUT, exist_ok=True)

a, b, c, d = 50.0, 120.0, 100.0, 130.0
th = np.radians(60.0)
A = np.array([0.0, 0.0])
D = np.array([d, 0.0])
B = A + a * np.array([np.cos(th), np.sin(th)])

# 两个解：C 为圆(B,b) 与圆(D,c) 的交点
# 用两圆交点公式
r1, r2 = b, c
dv = D - B
dist = np.linalg.norm(dv)
ex = dv / dist
# 交点沿 B->D 的投影
aa = (r1**2 - r2**2 + dist**2) / (2 * dist)
hh = np.sqrt(max(r1**2 - aa**2, 0.0))
mid = B + aa * ex
perp = np.array([-ex[1], ex[0]])
C1 = mid + hh * perp
C2 = mid - hh * perp

fig, ax = plt.subplots(figsize=(7.6, 6.0))

# 两个圆
ax.add_patch(Circle(B, b, fill=False, ls="--", lw=1.0, color="#7f8c8d", alpha=0.8))
ax.add_patch(Circle(D, c, fill=False, ls="--", lw=1.0, color="#7f8c8d", alpha=0.8))

# 机架与曲柄
ax.plot([A[0], D[0]], [A[1], D[1]], "-", color="#5b6675", lw=3.2, zorder=2)
ax.plot([A[0], B[0]], [A[1], B[1]], "-", color="#b03a2e", lw=4, zorder=3, solid_capstyle="round")

# 支路 1（σ=+1）：蓝
ax.plot([B[0], C1[0]], [B[1], C1[1]], "-", color="#1f618d", lw=3.4, zorder=3)
ax.plot([C1[0], D[0]], [C1[1], D[1]], "-", color="#1e8449", lw=3.4, zorder=3)
# 支路 2（σ=-1）：橙
ax.plot([B[0], C2[0]], [B[1], C2[1]], "--", color="#1f618d", lw=2.6, zorder=3, alpha=0.75)
ax.plot([C2[0], D[0]], [C2[1], D[1]], "--", color="#1e8449", lw=2.6, zorder=3, alpha=0.75)

# BD 连线
ax.plot([B[0], D[0]], [B[1], D[1]], ":", color="#7d3c98", lw=1.6, zorder=1)
ax.text(*(0.5 * (B + D) + np.array([-6, 6])), r"$BD$", fontsize=12, color="#7d3c98")

for p, lab, dx, dy, col in ((A, "$A$", -12, -14, "#2f4b66"), (B, "$B$", -4, 10, "#2f4b66"),
                            (D, "$D$", -34, -30, "#2f4b66"),
                            (C1, "$C_1$（支路 $\\sigma=+1$）", 10, 14, "#1f618d"),
                            (C2, "$C_2$（支路 $\\sigma=-1$）", 6, -18, "#c15f00")):
    ax.plot(*p, "o", color=col, ms=7, zorder=6)
    ax.text(p[0] + dx, p[1] + dy, lab, fontsize=11.5, color=col, zorder=7)

ax.text(-40, 128,
        r"$|BC|=b$、$|DC|=c$ 两个约束 $\Rightarrow$ $C$ 是两个圆的交点" "\n"
        r"两个解就是两条装配支路；$\sigma=\operatorname{sign}[(D-B)\times(C-B)]$",
        fontsize=10.2, va="top", color="#2f4b66",
        bbox=dict(boxstyle="round,pad=0.45", fc="#f3f8fc", ec="#cfd8e1"))

ax.set_xlim(-45, 165)
ax.set_ylim(-105, 140)
ax.set_aspect("equal")
ax.axis("off")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig11_branches.png"), bbox_inches="tight")

for name, C in (("C1", C1), ("C2", C2)):
    u = D - B
    v = C - B
    cross = u[0] * v[1] - u[1] * v[0]
    psi = np.degrees(np.arctan2(v[1], v[0]))
    beta = np.degrees(np.arctan2(u[1], u[0]))
    print(name, np.round(C, 2), "sigma=", np.sign(cross), "psi=%.2f beta=%.2f" % (psi, beta))
