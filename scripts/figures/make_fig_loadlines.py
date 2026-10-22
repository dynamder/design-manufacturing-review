"""画负载线的四种典型形状，以及它们与电机特性线的交点。"""
import os
import sys

import numpy as np

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("MPLCONFIGDIR", os.path.join(_ROOT, ".cache", "mplconfig"))
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.stdout.reconfigure(encoding="utf-8")
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 170

OUT = os.path.join(_ROOT, "assets", "figs")
os.makedirs(OUT, exist_ok=True)

Ts, w0 = 0.688, 837.8          # 电机：堵转转矩、空载角速度（与 fig2 同一台）
w = np.linspace(1, 860, 800)
motor = Ts * (1 - w / w0)

loads = {
    "恒转矩 $T_L=T_0$（提升、传送带）": (np.full_like(w, 0.30), "#1e8449", "-"),
    "粘性摩擦 $T_L=T_0+k_v\\omega$（轴承、油膜）": (0.05 + 5.5e-4 * w, "#1f618d", "-"),
    "流体阻力 $T_L=c\\omega^2$（风机、泵）": (2.5e-6 * w**2, "#b03a2e", "-"),
    "恒功率 $T_L=P/\\omega$（卷绕、主轴）": (100.0 / w, "#c15f00", "--"),
}

fig, ax = plt.subplots(figsize=(8.0, 4.8))
ax.plot(w, motor, color="#0d3b66", lw=2.6, label="电机 $T_m=T_s(1-\\omega/\\omega_0)$")

for lab, (tl, col, ls) in loads.items():
    ax.plot(w, tl, color=col, lw=2.0, ls=ls, label=lab)
    d = motor - tl
    idx = np.where(np.diff(np.sign(d)) != 0)[0]
    for k in idx:
        ax.plot(w[k], tl[k], "o", color=col, ms=6, zorder=5)

ax.set_xlim(0, 860)
ax.set_ylim(0, 0.80)
ax.set_xlabel("角速度 $\\omega$ (rad/s)", fontsize=10)
ax.set_ylabel("转矩 $T$ (N·m)", fontsize=10)
ax.set_title("负载线的四种典型形状：交点就是工作点", fontsize=11.5)
ax.grid(alpha=0.25, ls=":")
ax.legend(fontsize=8.6, loc="upper right")
ax.text(30, 0.74, "电机特性线是固定的；\n负载线由负载本身决定", fontsize=9.5, color="#2f4b66",
        bbox=dict(boxstyle="round,pad=0.35", fc="#f3f8fc", ec="#cfd8e1"))
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig12_loadlines.png"), bbox_inches="tight")
print("ok")
