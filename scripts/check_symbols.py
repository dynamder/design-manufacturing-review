"""检查复习资料里是否还有“旧符号 / 一字母多义”的残留。

用法（在项目根目录）：
    python scripts/check_symbols.py [目录]

默认检查 src/content/；退出码 0 表示干净，1 表示有可疑残留（逐条打印 文件:行号 + 上下文）。
规则来自 00_使用说明.md 的符号约定；新增规则直接在 RULES 里加。
"""
import glob
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

# (旧写法, 应该改成, 说明)
RULES = [
    (r"}{R}", "}{R_a}", "电机电阻应为 R_a"),
    (r"\gamma_{\min}", r"\mu_{\min}", "传动角统一用 μ"),
    (r"[\gamma]", r"[\mu]", "许用传动角统一用 μ"),
    (r"i_{sc}", "u_{sc}", "传动比用 u"),
    (r"i_{rc}", "u_{rc}", "传动比用 u"),
    (r"i_{sr}", "u_{sr}", "传动比用 u"),
    (r"$N\eta", r"$u\eta", "传动比用 u"),
    (r"$N\propto", r"$z\propto", "齿数用 z"),
    (r"N_{\text{driven}}", r"z_{\text{driven}}", "齿数用 z"),
    (r"K_1", "k_1", "Freudenstein 系数用小写 k"),
    (r"K_2", "k_2", "Freudenstein 系数用小写 k"),
    (r"K_3", "k_3", "Freudenstein 系数用小写 k"),
    (r"$F\,Y", r"$b_f\,Y", "齿宽用 b_f"),
    (r"$F\,m", r"$b_f\,m", "齿宽用 b_f"),
    (r"$F=1.5", r"$b_f=1.5", "齿宽用 b_f"),
    (r"$r_1=\frac{d_P", r"$\rho_1=\frac{d_p", "曲率半径用 ρ"),
    (r"$s+l", r"$\ell_{\min}+\ell_{\max}", "Grashof 长度用 ℓ"),
    (r"$p+q", r"$\ell_p+\ell_q", "Grashof 长度用 ℓ"),
    (r"\omega_sS", r"\omega_s z_s", "行星齿数用 z_s"),
    (r"\omega_rR", r"\omega_r z_r", "行星齿数用 z_r"),
    (r"=N\eta", "=u\\eta", "传动比用 u"),
    (r"\frac{\omega_m}{N}", "\\frac{\\omega_m}{u}", "传动比用 u"),
    (r"T_o=N", "T_o=u", "传动比用 u"),
]

# 这些行是“对照表/命名规则”，允许出现旧写法
SKIP_MARKERS = ["课件写法", "国内教材写法", "不是 $", "（不是", "课件里", "记 $C_p$", "Shigley 记", "$K_1,K_2,K_3$"]


def main(root):
    files = sorted(glob.glob(os.path.join(root, "0[0-9]_*.md")))
    if not files:
        print("没有找到 0x_*.md，检查路径:", root)
        return 1
    bad = 0
    for path in files:
        text = open(path, encoding="utf-8").read()
        for lineno, line in enumerate(text.split("\n"), 1):
            if any(m in line for m in SKIP_MARKERS):
                continue
            for old, new, why in RULES:
                if old in line:
                    bad += 1
                    print(f"{os.path.basename(path)}:{lineno}: {why}")
                    print(f"    发现 {old!r} -> 建议 {new!r}")
                    print(f"    {line.strip()[:120]}")
    print(f"\n检查完成：{'发现 %d 处可疑残留' % bad if bad else '没有发现残留'}")
    return 1 if bad else 0


if __name__ == "__main__":
    default_root = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "content"
    )
    root = sys.argv[1] if len(sys.argv) > 1 else default_root
    sys.exit(main(root))
