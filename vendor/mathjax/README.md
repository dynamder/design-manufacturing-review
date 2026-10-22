# MathJax（本地副本）

本目录存放从 npm 包 `mathjax` 复制过来的单文件构建产物，使复习网页在**断网、双击打开**时也能渲染公式。

- 版本：MathJax 3.2.2
- 文件：`tex-svg.js`（tex 输入 + SVG 输出，含常用扩展；页面通过 `window.MathJax` 配置）
- 来源：<https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-svg.js>
- 许可：Apache License 2.0，全文见同目录 `LICENSE`

升级步骤：

```bash
# 在项目根目录
curl -L -o vendor/mathjax/tex-svg.js https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-svg.js
curl -L -o vendor/mathjax/LICENSE      https://cdn.jsdelivr.net/npm/mathjax@3.2.2/LICENSE
npm run build
npm run check
```

`tex-svg.js` 是压缩后的构建产物，不需要阅读或修改；页面侧只需要在 `src/template.html` 里通过
`<script async src="vendor/mathjax/tex-svg.js"></script>` 引入。
