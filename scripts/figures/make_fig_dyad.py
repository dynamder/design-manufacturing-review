"""画标准二元组（dyad）的综合示意图：W、Z、δ、β、α 与精确点 P。"""
import os
import sys

import numpy as np

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("MPLCONFIGDIR", os.path.join(_ROOT, ".cache", "mplconfig"))
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Arc

sys.stdout.reconfigure(encoding="utf-8")
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 170

OUT = os.path.join(_ROOT, "assets", "figs")
os.makedirs(OUT, exist_ok=True)

A0 = np.array([0.0, 0.0])
W = 2.0 * np.exp(1j * np.deg2rad(32))
Z = 1.55 * np.exp(1j * np.deg2rad(78))
beta2 = np.deg2rad(42)
alpha2 = np.deg2rad(26)

A1 = np.array([W.real, W.imag])
P1 = A1 + np.array([Z.real, Z.imag])
A2 = np.array([(W * np.exp(1j * beta2)).real, (W * np.exp(1j * beta2)).imag])
Z2 = Z * np.exp(1j * alpha2)
P2 = A2 + np.array([Z2.real, Z2.imag])
delta = P2 - P1

fig, ax = plt.subplots(figsize=(7.6, 5.4))


def arrow(a, b, color, lw=2.4, ls="-", alpha=1.0):
    ax.annotate("", xy=b, xytext=a,
                arrowprops=dict(arrowstyle="-|>", lw=lw, color=color, ls=ls,
                                alpha=alpha, shrinkA=0, shrinkB=0))


arrow(A0, A1, "#1f618d")
arrow(A1, P1, "#b03a2e")
arrow(A0, A2, "#1f618d", lw=2.0, ls="--", alpha=0.5)
arrow(A2, P2, "#b03a2e", lw=2.0, ls="--", alpha=0.5)
arrow(P1, P2, "#1e8449", lw=1.9)

# β2
ax.add_patch(Arc(A0, 1.25, 1.25, theta1=np.degrees(np.angle(W)),
                 theta2=np.degrees(np.angle(W * np.exp(1j * beta2))), color="#1f618d", lw=1.6))
ax.text(A0[0] + 0.70, A0[1] + 0.14, r"$\beta_2$", fontsize=13, color="#1f618d")

# α2：在 A1 处画 Z 与 Z 转 α2 后的方向
ax.annotate("", xy=A1 + 0.8 * np.array([Z2.real, Z2.imag]), xytext=A1,
            arrowprops=dict(arrowstyle="-|>", lw=1.1, color="#b03a2e", ls=":", alpha=0.75))
ax.add_patch(Arc(A1, 1.05, 1.05, theta1=np.degrees(np.angle(Z)),
                 theta2=np.degrees(np.angle(Z2)), color="#7d3c98", lw=1.6))
ax.text(A1[0] + 0.42, A1[1] + 0.52, r"$\alpha_2$", fontsize=13, color="#7d3c98")

# δ2 标签（沿中线外移）
mid = 0.5 * (P1 + P2)
n = np.array([-delta[1], delta[0]])
n = n / np.linalg.norm(n) * 0.28
ax.text(mid[0] + n[0] - 0.35, mid[1] + n[1] + 0.12, r"$\delta_2=P_2-P_1$", fontsize=11, color="#1e8449")

for p, lab, dx, dy, fs in ((A0, r"$A_0$ 固定铰", -0.22, -0.36, 11.5),
                           (A1, r"$A_1$ 动铰", 0.10, -0.30, 11.5),
                           (A2, r"$A_2$", 0.12, 0.06, 11.5),
                           (P1, r"$P_1$ 精确点", 0.12, -0.30, 11.5),
                           (P2, r"$P_2$", 0.12, 0.10, 11.5)):
    ax.plot(*p, "o", color="#2f4b66", ms=7, zorder=6)
    ax.text(p[0] + dx, p[1] + dy, lab, fontsize=fs, zorder=7)

ax.text(*(A0 + 0.52 * (A1 - A0) + np.array([-0.62, 0.16])), r"$W$", fontsize=13, color="#1f618d")
ax.text(*(A1 + 0.52 * (P1 - A1) + np.array([0.12, 0.02])), r"$Z$", fontsize=13, color="#b03a2e")

ax.text(-0.35, 4.55,
        r"$P_1=W+Z$：连杆上同一材料点在位置 1 的坐标" "\n"
        r"$P_2=W\,e^{i\beta_2}+Z\,e^{i\alpha_2}$：位置 2" "\n"
        r"解出 $W,Z$ 后反求铰点：$A_1=P_1-Z$，$A_0=A_1-W$",
        fontsize=10.4, va="top", color="#2f4b66",
        bbox=dict(boxstyle="round,pad=0.45", fc="#f3f8fc", ec="#cfd8e1"))

ax.set_xlim(-0.9, 4.4)
ax.set_ylim(-0.8, 4.7)
ax.set_aspect("equal")
ax.axis("off")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig10_dyad.png"), bbox_inches="tight")
print("ok")
