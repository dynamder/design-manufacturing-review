# 设计与制造 1 · L1–L5 复习网页

注意：这是个人自用的复习网页，并不准备长期维护。

把 `src/content/` 里的 Markdown 复习资料构建成一个**单页复习网站**。构建产物 `index.html`
不依赖服务器、不依赖外网：图片在 `assets/`，公式渲染器 MathJax 在 `vendor/`，双击即可阅读。

- 内容：L1 机构基础、L2 四杆分析与综合、L3 电机与传动、L4 设计流程/材料/齿轮几何、L5 齿轮受力与强度，附公式速查、模拟卷与答案。
- 特性：侧边目录、表格、代码块、SVG 公式、图片点击放大、打印/存 PDF 样式、移动端适配。

## 在线访问

- 网页：<https://dynamder.github.io/design-manufacturing-review/>
- 仓库：<https://github.com/dynamder/design-manufacturing-review>

GitHub Pages 直接托管 `main` 分支根目录（legacy 构建），`.nojekyll` 关闭 Jekyll。
推送到 `main` 后 GitHub 会自动重新发布，通常 1 分钟内生效。

## 快速开始

直接阅读：

```text
双击 index.html（Chrome / Edge / Firefox 均可，断网也能正常显示公式）
```

本地预览（可选，需要 Node.js ≥ 18）：

```bash
npm run serve          # http://127.0.0.1:5173/
```

修改内容后重新构建：

```bash
npm run build          # src/ -> index.html
npm run dev            # 构建 + 本地预览 + 监听 src/ 自动重建
```

构建、预览都只用 Node 内置模块，**没有 npm 依赖**，不需要 `npm install`。
如果环境里 `npm` 不可用，也可以直接运行 `node scripts/build.mjs`、`node scripts/serve.mjs`。

## 目录结构

```text
ai-生成复习资料/
├── index.html              # 构建产物：完整页面，可直接双击或分享
├── src/
│   ├── content/            # 章节源码（00–09，按文件名排序）
│   ├── styles/main.css     # 全部样式（构建时内联进 HTML）
│   ├── template.html       # 页面骨架（占位符 {{TITLE}}、{{TOC}} 等）
│   └── site.json           # 标题、副标题、页脚等站点信息
├── assets/
│   └── figs/               # 插图（fig*.png 为自绘，ppt/ 为课件截图）
├── vendor/
│   └── mathjax/            # 本地 MathJax 3.2.2（离线公式渲染）
├── scripts/
│   ├── build.mjs           # 构建脚本（Markdown -> HTML）
│   ├── dev.mjs             # 开发模式：监听 + 自动重建
│   ├── serve.mjs           # 零依赖静态服务器
│   ├── check.mjs           # 自检：图片引用、外网依赖、产物是否过期
│   ├── check_symbols.py    # 符号约定检查（旧符号残留）
│   └── figures/            # matplotlib 绘图脚本 + make_all.py
├── legacy/
│   └── 旧版_按主题/         # 旧版资料归档，不参与构建
├── package.json
├── .editorconfig
├── .gitignore
├── .gitattributes
└── README.md
```

## 写作约定

- **章节**：`src/content/NN_名称.md`，`NN` 从 `00` 连续编号；构建时按文件名排序，`#` 一级标题自动成为章节和目录项，`##` 二级标题进入目录。
- **图片**：放到 `assets/figs/`，Markdown 里写 `![说明](assets/figs/xxx.png)`；构建会检查图片是否存在。
- **公式**：行内 `$...$`，独立公式 `$$...$$`，由本地 MathJax 渲染。
- **支持语法**：标题、段落、粗体/斜体、行内代码、代码块、引用、有序/无序列表、表格、分隔线、图片、链接。
- **不支持**：原始 HTML、脚注、任务列表等（构建器是轻量实现，够用即可）。

新增一章：

```bash
# 1. 新建 src/content/10_新章节.md，以 # 标题 开头
# 2. 重新构建
npm run build
```

## 检查与维护

```bash
npm run check           # 检查图片引用、外网依赖、MathJax 是否就位、产物是否过期
npm run check:symbols   # 检查旧符号 / 一字母多义残留（需 Python）
npm run figs            # 重新生成自绘插图（需 numpy + matplotlib）
```

`npm run check` 通过即表示：页面引用的所有资源都在仓库内，**可以离线独立运行**。

## 发布 / 备份

整个目录就是一个可独立运行的站点。发布渠道：

- **GitHub Pages（当前使用）**：`main` 分支根目录，推送后自动发布到
  <https://dynamder.github.io/design-manufacturing-review/>；根目录的 `.nojekyll` 让 GitHub 原样托管静态文件。
- **离线分享**：压缩整个目录发给别人，对方解压后双击 `index.html`。
- **其他静态托管**：入口是根目录的 `index.html`。
- 如果只想带最小文件集，复制 `index.html` + `assets/` + `vendor/` 即可。

`index.html` 是生成文件，请不要直接编辑；改动请落在 `src/`，然后 `npm run build`。

## 版本管理

仓库已初始化 Git，`index.html` 与源文件一起纳入版本管理，因此克隆后无需构建即可阅读。
每次改完内容建议：

```bash
npm run check
npm run build
git add -A
git commit -m "更新 L3 复习内容"
git push
```

## 说明

- 内容依据课程官方课件 L1–L5 与 2023 期末卷整理；【课件】为原文，【补充】已单独标注。
- `legacy/旧版_按主题/` 是最早按主题拆分的版本，仅作归档，不参与构建。
- MathJax 为第三方组件（Apache-2.0），来源与升级方法见 `vendor/mathjax/README.md`。
