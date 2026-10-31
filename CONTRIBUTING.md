# 贡献指南

这个站由课程维护者共同维护。你可以只写一门课，也可以只修一个错。

## 只改内容（最常见）

1. 找到课程目录：`courses/<slug>/src/`。
2. 改对应的 `.md`。目录顺序在 `src/SUMMARY.md` 里。
3. 本地验证：

   ```bash
   npm run build
   npm run serve      # http://127.0.0.1:5173/
   ```

4. 提交 PR。只改 Markdown 时不需要动 `site/`。

写作约定：

- 图片放 `src/assets/figs/`，Markdown 里写 `![说明](assets/figs/xxx.png)`
- 公式用 `$...$` 和 `$$...$$`
- 标题层级：文件里一个 `#` 一级标题；`##` 是节
- 打印友好：不要依赖颜色传达信息

## 开一门新课

1. 建 `courses/<slug>/`，写 `meta.json`：

   ```json
   {
     "slug": "mechanics",
     "title": "理论力学",
     "code": "ME-102",
     "summary": "静力学 · 运动学 · 动力学",
     "tags": ["静力学", "运动学"],
     "status": "active",
     "order": 2,
     "maintainers": ["@your-handle"],
     "updated": "2025-10-24"
   }
   ```

   | 字段 | 说明 |
   | --- | --- |
   | `slug` | URL 和目录名，稳定、短、英文 |
   | `status` | `active` 已发布；`planned` 只占位，显示“待认领”（是否构建看书里有没有 `SUMMARY.md`） |
   | `order` | 左栏顺序，小的在前 |
   | `maintainers` | GitHub handle 列表，显示在课程页脚 |
   | `updated` | 门面显示的“更新”日期，手动维护 |

2. 建 `book.toml`。复制 `courses/dm1/book.toml`，改：

   ```toml
   [book]
   title = "课程名"
   authors = ["你的名字"]
   language = "zh-CN"
   src = "src"
   ```

3. 建 `src/SUMMARY.md`。Part 标题决定门面里的内容类型：

   ```md
   # Summary

   # 开始
   - [使用说明](intro.md)

   # 讲义
   - [第 1 讲](ch01.md)

   # 速查
   - [公式表](cheatsheet.md)

   # 真题
   - [往年卷](exam.md)
   ```

   `开始 / 讲义 / 速查 / 真题 / 附录` 会映射成门面的标签和筛选。

4. 复制 `courses/dm1/theme/`（返回胶囊 + 主题），或者暂时不放；没有主题也能构建。

5. `npm run build`，确认左栏出现新课程、右栏能点进章节。

## 改门面

门面在 `site/src/`：

| 文件 | 职责 |
| --- | --- |
| `catalog.gleam` | 入口、init/update、URL、副作用 |
| `data.gleam` | 目录类型与解码 |
| `types.gleam` | Model / Message / Item / Action |
| `results.gleam` | 命令面板的匹配、排序、动作列表 |
| `view.gleam` | 全部 HTML |
| `ffi.gleam` / `ffi_ffi.mjs` | 浏览器边界（URL、剪贴板、焦点） |

改完：

```bash
cd site && gleam build && cd ..
```

视觉在 `site/public/styles.css`。配色/密度改动请先看 `docs/design.md` 里的取舍。

## 几条硬规则

- **门面不渲染正文。** 正文永远由 mdbook 负责。
- **不写本地存储。** 不加 `localStorage`、cookie、进度上报；状态只进 URL。
- **不铺快捷键。** 新动作放进命令面板，不新增全局组合键。
- **不改 mdbook 的 `index.hbs`。** 用 `additional-css` / `additional-js` 做增量，
  否则 mdbook 升级会断。
- **课程 slug 一旦发布就不要改。** 改了就加 301/重定向表。

## PR 检查清单

- [ ] `npm run build` 通过
- [ ] 新图片在 `src/assets/` 里，没有外链图床
- [ ] 公式在断网下能渲染（用了仓库自带的 MathJax）
- [ ] 新课程在门面左栏、面板、手机视图里都能到达
- [ ] 没有新增 `localStorage` / cookie
- [ ] 打印预览可用（Ctrl+P）
