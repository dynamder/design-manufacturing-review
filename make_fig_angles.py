"""画四杆机构的 θ、ψ、φ 三个角度定义图。"""
import os
import sys

import numpy as np

os.environ.setdefault("MPLCONFIGDIR", os.path.abspath(".mplconfig"))
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Circle

sys.stdout.reconfigure(encoding="utf-8")
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 170

OUT = "figs"
os.makedirs(OUT, exist_ok=True)

a, b, c, d = 50.0, 120.0, 100.0, 130.0
th = np.radians(60.0)
A = np.array([0.0, 0.0])
D = np.array([d, 0.0])
B = A + a * np.array([np.cos(th), np.sin(th)])
phi = np.radians(89.56)
C = D + c * np.array([np.cos(phi), np.sin(phi)])
psi = np.arctan2(C[1] - B[1], C[0] - B[0])

fig, ax = plt.subplots(figsize=(7.6, 4.9))
ax.plot([A[0], D[0]], [A[1], D[1]], "-", color="#8a99a8", lw=3, zorder=2)
ax.plot([A[0], B[0]], [A[1], B[1]], "-", color="#b03a2e", lw=4, zorder=3, solid_capstyle="round")
ax.plot([B[0], C[0]], [B[1], C[1]], "-", color="#1f618d", lw=4, zorder=3, solid_capstyle="round")
ax.plot([C[0], D[0]], [C[1], D[1]], "-", color="#1e8449", lw=4, zorder=3, solid_capstyle="round")
for p, lab, dx, dy in ((A, "$A$", -11, -14), (B, "$B$", 4, 6), (C, "$C$", 2, 8), (D, "$D$", -14, -14)):
    ax.plot(*p, "o", color="#2f4b66", ms=7, zorder=6)
    ax.text(p[0] + dx, p[1] + dy, lab, fontsize=13, zorder=7)

# 参考方向（+x 虚线）
for p in (A, B, D):
    ax.plot([p[0], p[0] + (46 if p is not A else 40)], [p[1], p[1]],
            ls=":", color="#95a5a6", lw=1.2, zorder=1)

# θ
ax.add_patch(Arc(A, 56, 56, theta1=0, theta2=60, color="#b03a2e", lw=1.8))
ax.text(A[0] + 33, A[1] + 9, r"$\theta$", fontsize=14, color="#b03a2e")

# ψ
ax.add_patch(Arc(B, 62, 62, theta1=0, theta2=np.degrees(psi), color="#1f618d", lw=1.8))
ax.text(B[0] + 34, B[1] - 3, r"$\psi$", fontsize=14, color="#1f618d")

# φ（从 D 的 +x 方向量到 DC）
ax.add_patch(Arc(D, 58, 58, theta1=0, theta2=89.56, color="#1e8449", lw=1.8))
ax.text(D[0] + 13, D[1] + 27, r"$\varphi$", fontsize=14, color="#1e8449")

# 传动角 mu（在 C 处，CB 与 CD 的夹角）
v1 = (B - C) / np.linalg.norm(B - C)
v2 = (D - C) / np.linalg.norm(D - C)
ang1 = np.degrees(np.arctan2(v1[1], v1[0]))
ang2 = np.degrees(np.arctan2(v2[1], v2[0]))
ax.add_patch(Arc(C, 46, 46, theta1=min(ang1, ang2), theta2=max(ang1, ang2), color="#7d3c98", lw=1.8))
ax.text(C[0] - 30, C[1] - 26, r"$\mu$ 传动角", fontsize=12, color="#7d3c98")

ax.text(6, 118,
        r"$\theta$：输入杆 $AB$ 的方位角" "\n"
        r"$\psi$：连杆 $BC$（$B\to C$）的方位角" "\n"
        r"$\varphi$：输出杆 $DC$（$D\to C$）的方位角" "\n"
        r"都从 $+x$ 方向起、逆时针为正（虚线即 $+x$）" "\n" r"$\operatorname{atan2}$ 结果取 $(-180^\circ,180^\circ]$",
        fontsize=10.2, va="top", color="#2f4b66",
        bbox=dict(boxstyle="round,pad=0.45", fc="#f3f8fc", ec="#cfd8e1"))

ax.set_xlim(-28, 178)
ax.set_ylim(-34, 132)
ax.set_aspect("equal")
ax.axis("off")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig9_angles.png"), bbox_inches="tight")
print("psi=%.2f phi=%.2f mu=%.2f" % (np.degrees(psi), 89.56, abs(89.56 - np.degrees(psi))))
