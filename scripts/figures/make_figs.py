
import os, json, math
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("MPLCONFIGDIR", os.path.join(_ROOT, ".cache", "mplconfig"))
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 160

OUT = os.path.join(_ROOT, "assets", "figs")
os.makedirs(OUT, exist_ok=True)

# ================= 四杆机构 =================
a, b, c, d = 50.0, 120.0, 100.0, 130.0

def solve_phi(th):
    A1 = 2*c*(d - a*math.cos(th))
    B1 = -2*a*c*math.sin(th)
    C1 = d*d + c*c + a*a - b*b - 2*d*a*math.cos(th)
    Dv = -C1
    disc = A1*A1 + B1*B1 - Dv*Dv
    if disc < 0: return None
    cands = []
    for sgn in (+1, -1):
        tt = (B1 + sgn*math.sqrt(disc)) / (A1 + Dv)
        pp = 2*math.atan(tt)
        Cc = np.array([d + c*math.cos(pp), c*math.sin(pp)])
        cands.append((pp, Cc[1], Cc))
    best = max(cands, key=lambda z: z[1])
    return best[0], best[2]

th = math.radians(60)
phi, C = solve_phi(th)
B = np.array([a*math.cos(th), a*math.sin(th)])
A = np.array([0.0, 0.0]); D = np.array([d, 0.0])

def angle_at(P, Q, R):
    v1 = Q - P; v2 = R - P
    cv = np.dot(v1, v2)/np.linalg.norm(v1)/np.linalg.norm(v2)
    return math.degrees(math.acos(max(-1, min(1, cv))))

gamma60 = angle_at(C, B, D); gamma60 = min(gamma60, 180-gamma60)
ths = np.linspace(0, 2*math.pi, 721)
gammas = []
for t_ in ths:
    res = solve_phi(t_)
    if res is None:
        gammas.append(np.nan); continue
    pp, CC = res
    g = angle_at(CC, np.array([a*math.cos(t_), a*math.sin(t_)]), D)
    gammas.append(min(g, 180-g))
gammas = np.array(gammas)
imin = np.nanargmin(gammas); gmin = gammas[imin]

def tri_angle_A(AC):
    return math.degrees(math.acos(max(-1, min(1, (d*d + AC*AC - c*c)/(2*d*AC)))))
theta_pp = abs(tri_angle_A(b - a) - tri_angle_A(b + a))
K = (180 + theta_pp)/(180 - theta_pp)

w2 = 10.0
vB = w2*np.array([-a*math.sin(th), a*math.cos(th)])
rCB = C - B; rCD = C - D
M = np.column_stack([np.array([-rCB[1], rCB[0]]), -np.array([-rCD[1], rCD[0]])])
w3, w4 = np.linalg.solve(M, -vB)
vC = w4*np.array([-rCD[1], rCD[0]])

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.8))
ax1.set_aspect("equal")
tt = np.linspace(0, 2*math.pi, 400)
ax1.plot(a*np.cos(tt), a*np.sin(tt), ls=":", lw=0.8, color="0.75")
ax1.plot(d + c*np.cos(tt), c*np.sin(tt), ls=":", lw=0.8, color="0.75")
for P, Q, col in [(A, B, "#1565c0"), (B, C, "#c62828"), (C, D, "#2e7d32")]:
    ax1.plot([P[0], Q[0]], [P[1], Q[1]], lw=4.5, color=col, solid_capstyle="round")
ax1.plot([A[0], D[0]], [A[1], D[1]], lw=3, color="0.35")
for P, name, off in [(A, "A", (-16, -18)), (B, "B", (-6, 12)), (C, "C", (10, 12)), (D, "D", (-6, -22))]:
    ax1.plot(*P, "o", ms=8, mfc="white", mec="0.2", mew=1.6, zorder=5)
    ax1.annotate(name, P+np.array(off), fontsize=13, fontweight="bold")
v1 = (B-C)/np.linalg.norm(B-C); v2 = (D-C)/np.linalg.norm(D-C)
ang1_ = math.atan2(v1[1], v1[0]); ang2_ = math.atan2(v2[1], v2[0])
lo, hi = sorted([ang1_, ang2_])
if hi - lo > math.pi: lo, hi = hi, lo + 2*math.pi
arc = np.linspace(lo, hi, 60)
ax1.plot(C[0]+34*np.cos(arc), C[1]+34*np.sin(arc), color="#6a1b9a", lw=2)
mid = (lo+hi)/2
ax1.annotate(f"μ={gamma60:.1f}°", (C[0]+52*math.cos(mid), C[1]+52*math.sin(mid)),
             color="#6a1b9a", fontsize=11, ha="center")
ax1.text(-88, -42, "虚线：B、C 点的运动圆", fontsize=8, color="0.5")
ax1.set_xlim(-95, 205); ax1.set_ylim(-55, 195)
ax1.set_title(f"曲柄摇杆机构（θ=60°，φ={math.degrees(phi):.1f}°）", fontsize=11)
ax1.axis("off")

ax2.plot(np.degrees(ths), gammas, color="#1565c0", lw=2)
ax2.axhline(40, color="#c62828", ls="--", lw=1)
ax2.text(4, 41.5, "许用传动角 [μ]≈40°", color="#c62828", fontsize=9)
ax2.plot(math.degrees(ths[imin]), gmin, "o", color="#c62828", ms=6)
ax2.annotate(f"μ_min={gmin:.1f}°", (math.degrees(ths[imin]), gmin), xytext=(26, 28),
             textcoords="offset points", fontsize=9, color="#c62828",
             arrowprops=dict(arrowstyle="->", color="#c62828", lw=0.8))
ax2.set_xlabel("曲柄转角 θ (°)"); ax2.set_ylabel("传动角 μ (°)")
ax2.set_xlim(0, 360); ax2.set_ylim(35, 95)
ax2.grid(alpha=0.3)
ax2.set_title("传动角随曲柄转角变化：共线位置附近最小", fontsize=11)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig1_fourbar.png"), bbox_inches="tight")
plt.close(fig)

# ================= 电机 =================
V, R = 24.0, 1.0
ke = V/(8000*2*math.pi/60)
w0 = V/ke; Ts = ke*V/R
w = np.linspace(0, w0, 400)
T = Ts*(1 - w/w0)
kf = 2.5e-6
fig, ax = plt.subplots(figsize=(8.2, 4.6))
ax.plot(w, T, color="#1565c0", lw=2.5)
ax.plot(w, np.full_like(w, 0.30), color="#2e7d32", lw=2)
ax.plot(w, kf*w**2, color="#c62828", lw=2)
w1 = w0*(1-0.30/Ts)
aa, bb, cc = kf, Ts/w0, -Ts
w2 = (-bb + math.sqrt(bb*bb - 4*aa*cc))/(2*aa)
ax.plot(w1, 0.30, "o", ms=9, color="#2e7d32", zorder=5, mfc="white", mew=2)
ax.plot(w2, kf*w2**2, "o", ms=9, color="#c62828", zorder=5, mfc="white", mew=2)
ax.annotate(f"工作点 1\n{w1*60/(2*math.pi):.0f} rpm", (w1, 0.30), xytext=(18, 34),
            textcoords="offset points", fontsize=9, color="#2e7d32",
            arrowprops=dict(arrowstyle="->", color="#2e7d32", lw=0.8))
ax.annotate(f"工作点 2\n{w2*60/(2*math.pi):.0f} rpm", (w2, kf*w2**2), xytext=(-78, 26),
            textcoords="offset points", fontsize=9, color="#c62828",
            arrowprops=dict(arrowstyle="->", color="#c62828", lw=0.8))
ax.annotate("堵转点 (0, T_s)", (0, Ts), xytext=(52, Ts*1.02), fontsize=9, color="#1565c0",
            arrowprops=dict(arrowstyle="->", color="#1565c0", lw=0.8))
ax.text(w0*0.70, 0.035, "空载点 (ω0, 0)", fontsize=9, color="#1565c0")
ax.plot([], [], color="#1565c0", lw=2.5, label="电机 T-ω 线")
ax.plot([], [], color="#2e7d32", lw=2, label="恒转矩负载")
ax.plot([], [], color="#c62828", lw=2, label="风机负载 T=kω²")
ax.legend(fontsize=9, loc="lower right", framealpha=0.95)
ax.set_xlabel(r"转速 $\omega$ (rad/s)"); ax.set_ylabel("转矩 T (N·m)")
ax.set_xlim(0, 880); ax.set_ylim(0, 0.76)
ax.grid(alpha=0.3)
ax.set_title("工作点 = 电机特性曲线与负载特性曲线的交点", fontsize=11)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig2_motor.png"), bbox_inches="tight")
plt.close(fig)

# ================= 齿轮 =================
def teeth_circle(ax, R, n, inward=False, color="0.3", lw=1.0, h=4):
    for k in range(n):
        t = 2*math.pi*k/n
        r1, r2 = (R, R-h) if inward else (R, R+h)
        ax.plot([r1*math.cos(t), r2*math.cos(t)], [r1*math.sin(t), r2*math.sin(t)], color=color, lw=lw)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5.2))
ax1.set_aspect("equal"); ax1.axis("off")
Rs, Rp, Rr = 40, 30, 100
teeth_circle(ax1, Rr, 50, inward=True)
teeth_circle(ax1, Rs, 20)
ax1.add_patch(Circle((0,0), Rr, fill=False, color="0.4", lw=1))
ax1.add_patch(Circle((0,0), Rs, fill=False, color="0.4", lw=1))
for k in range(3):
    t = 2*math.pi*k/3 + math.pi/6
    cx, cy = (Rs+Rp)*math.cos(t), (Rs+Rp)*math.sin(t)
    ax1.add_patch(Circle((cx, cy), Rp, fill=False, color="0.4", lw=1))
    teeth_circle(ax1, Rp, 15, color="0.55", lw=0.7)
    ax1.plot([0, cx], [0, cy], color="#1565c0", lw=2)
ax1.add_patch(Circle((0,0), 13, fc="#e3f0ff", ec="#1565c0", lw=1.2, zorder=6))
ax1.text(0, 0, "H", ha="center", va="center", fontsize=11, fontweight="bold", color="#1565c0", zorder=7)
ax1.text(0, 27, "1", ha="center", va="center", fontsize=11, fontweight="bold", zorder=7)
ax1.text((Rs+Rp)*math.cos(math.pi/6), (Rs+Rp)*math.sin(math.pi/6), "2", ha="center", va="center",
         fontsize=11, fontweight="bold", color="0.25")
ax1.text(0, Rr-12, "3", ha="center", fontsize=12, fontweight="bold")
ax1.set_xlim(-120, 120); ax1.set_ylim(-120, 135)
ax1.set_title("2K-H 行星轮系：1 太阳轮  2 行星轮  3 内齿圈  H 系杆", fontsize=10)

ax2.set_aspect("equal"); ax2.axis("off")
Rg = 100
ell_a, ell_b = 100, 78
ax2.add_patch(Circle((0,0), Rg, fill=False, color="0.35", lw=1.2))
teeth_circle(ax2, Rg, 60, inward=True)
tt = np.linspace(0, 2*math.pi, 600)
ex, ey = ell_a*np.cos(tt), ell_b*np.sin(tt)
ax2.plot(ex, ey, color="#2e7d32", lw=1.5)
for k in range(60):
    t = 2*math.pi*k/60
    x, y = ell_a*math.cos(t), ell_b*math.sin(t)
    nx, ny = x/ell_a**2, y/ell_b**2
    nl = math.hypot(nx, ny)
    ax2.plot([x, x+4*nx/nl], [y, y+4*ny/nl], color="#2e7d32", lw=0.9)
ax2.add_patch(Ellipse((0,0), 2*ell_a*0.94, 2*ell_b*0.91, fill=False, color="#c62828", lw=2))
ax2.text(0, 0, "3", ha="center", va="center", fontsize=12, fontweight="bold", color="#c62828")
ax2.text(-62, 34, "2", fontsize=11, fontweight="bold", color="#2e7d32")
ax2.text(0, Rg+12, "1", ha="center", fontsize=12, fontweight="bold")
ax2.set_xlim(-125, 125); ax2.set_ylim(-120, 128)
ax2.set_title("谐波齿轮：1 刚轮（内齿）  2 柔轮（外齿）  3 波发生器", fontsize=10)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig3_gears.png"), bbox_inches="tight")
plt.close(fig)

# ================= 例題数值 =================
m, z1, z2, alpha = 3.0, 20, 40, math.radians(20)
d1, d2 = m*z1, m*z2
da1, da2 = d1+2*m, d2+2*m
df1, df2 = d1-2.5*m, d2-2.5*m
db1, db2 = d1*math.cos(alpha), d2*math.cos(alpha)
aa_ = (d1+d2)/2
aa1 = math.acos(db1/da1); aa2 = math.acos(db2/da2)
eps = (z1*(math.tan(aa1)-math.tan(alpha)) + z2*(math.tan(aa2)-math.tan(alpha)))/(2*math.pi)

a2,b2,c2,d2_ = 40.0,100.0,80.0,110.0
def phi_from_theta(th):
    A1 = 2*c2*(d2_ - a2*math.cos(th)); B1 = -2*a2*c2*math.sin(th)
    C1 = d2_*d2_ + c2*c2 + a2*a2 - b2*b2 - 2*d2_*a2*math.cos(th)
    Dv = -C1; disc = A1*A1+B1*B1-Dv*Dv
    sols = []
    for s in (1,-1):
        t = (B1 + s*math.sqrt(disc))/(A1+Dv); p = 2*math.atan(t)
        Cc = np.array([d2_+c2*math.cos(p), c2*math.sin(p)])
        sols.append((p, Cc[1]))
    return math.degrees(max(sols, key=lambda x: x[1])[0])
rows = [(t, phi_from_theta(math.radians(t))) for t in (30, 60, 90)]
M = []; rhs = []
for tdeg, pdeg in rows:
    t = math.radians(tdeg); p = math.radians(pdeg)
    M.append([math.cos(p), -math.cos(t), 1.0]); rhs.append(math.cos(p-t))
K1,K2,K3 = np.linalg.solve(np.array(M), np.array(rhs))
adopt = 40.0
dd = K1*adopt; cc = dd/K2; bb = math.sqrt(adopt*adopt + cc*cc + dd*dd - 2*adopt*cc*K3)

out = {
  "fourbar": {"phi": math.degrees(phi), "gamma": gamma60, "gamma_min": gmin,
              "theta_pp": theta_pp, "K": K, "w3": w3, "w4": w4,
              "vC": vC.tolist(), "vB": vB.tolist()},
  "motor": {"ke": ke, "w0": w0, "n0": w0*60/(2*math.pi), "Ts": Ts, "w1": w1, "w2": w2,
            "n1": w1*60/(2*math.pi), "n2": w2*60/(2*math.pi), "T2": kf*w2**2},
  "gear": {"d1": d1, "d2": d2, "da1": da1, "da2": da2, "df1": df1, "df2": df2,
           "db1": db1, "db2": db2, "a": aa_, "eps": eps, "alpha_a1": math.degrees(aa1),
           "alpha_a2": math.degrees(aa2)},
  "freudenstein": {"rows": rows, "K1": K1, "K2": K2, "K3": K3, "b": bb, "c": cc, "d": dd}
}
print(json.dumps(out, ensure_ascii=False, indent=1))
