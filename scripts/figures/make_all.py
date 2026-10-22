"""按顺序重新生成全部插图。

用法（在项目根目录）：
    python scripts/figures/make_all.py

依赖：numpy、matplotlib；字体使用系统里的 Microsoft YaHei / SimHei（缺失时退回 DejaVu Sans）。
输出：assets/figs/*.png
"""
import os
import runpy
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# 顺序即图的编号；单个脚本也可以单独运行
SCRIPTS = [
    "make_figs.py",           # fig1–fig3
    "make_figs_extra.py",     # fig4–fig5
    "make_figs_more.py",      # fig6–fig7
    "make_fig_cam.py",        # fig8
    "make_fig_angles.py",     # fig9
    "make_fig_dyad.py",       # fig10
    "make_fig_branches.py",   # fig11
    "make_fig_loadlines.py",  # fig12
]


def main():
    try:
        import matplotlib  # noqa: F401
    except ImportError:
        print("缺少 matplotlib，请先安装：pip install matplotlib numpy", file=sys.stderr)
        return 1

    for name in SCRIPTS:
        path = os.path.join(HERE, name)
        print(f"==> {name}")
        runpy.run_path(path, run_name="__main__")
    print(f"\n完成：图片已写入 {os.path.join(os.path.dirname(os.path.dirname(HERE)), 'assets', 'figs')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
