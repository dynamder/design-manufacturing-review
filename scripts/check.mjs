#!/usr/bin/env node
/**
 * 自检：确认站点离线可用、引用完整。
 *
 *   npm run check
 *
 * 检查项：
 *   1. 章节文件编号连续，且都有 H1 标题
 *   2. Markdown 中的图片引用都存在，且没有指向外网的资源
 *   3. 构建产物 index.html 存在，且不引用任何外网资源
 *   4. 本地 MathJax 已就位
 *   5. 报告未被引用的图片（警告）
 *   6. 提示 index.html 是否比源文件旧（警告）
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '..');
const CONTENT = path.join(ROOT, 'src', 'content');
const OUT = path.join(ROOT, 'index.html');

const errors = [];
const warnings = [];
const fail = (msg) => errors.push(msg);
const warn = (msg) => warnings.push(msg);

function walk(dir) {
  const out = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...walk(full));
    else out.push(full);
  }
  return out;
}

/* 1. 章节文件 */
const chapters = fs.readdirSync(CONTENT)
  .filter((f) => /^\d{2}_.+\.md$/.test(f))
  .sort((a, b) => a.localeCompare(b, 'zh-CN'));

if (!chapters.length) fail('src/content 下没有 NN_*.md 章节文件');
chapters.forEach((file, index) => {
  const num = Number(file.slice(0, 2));
  if (num !== index) fail(`章节编号不连续：${file} 期望前缀 ${String(index).padStart(2, '0')}_`);
  const text = fs.readFileSync(path.join(CONTENT, file), 'utf8');
  if (!/^#\s+\S/m.test(text)) fail(`${file} 缺少 H1 标题`);
});

/* 2. Markdown 图片引用 */
const used = new Set();
let imageCount = 0;
for (const file of chapters) {
  const text = fs.readFileSync(path.join(CONTENT, file), 'utf8');
  for (const match of text.matchAll(/!\[[^\]]*\]\(([^)\s]+)\)/g)) {
    const ref = match[1];
    imageCount++;
    if (/^[a-z]+:/i.test(ref)) {
      fail(`${file} 引用了外网图片（离线会失效）：${ref}`);
      continue;
    }
    const abs = path.join(ROOT, ref.split('#')[0]);
    if (!fs.existsSync(abs)) fail(`${file} 图片不存在：${ref}`);
    used.add(path.relative(path.join(ROOT, 'assets'), abs).split(path.sep).join('/'));
  }
}

/* 3. 构建产物 */
let html = '';
if (!fs.existsSync(OUT)) {
  fail('index.html 不存在，请先运行 npm run build');
} else {
  html = fs.readFileSync(OUT, 'utf8');
  const external = [...html.matchAll(/<(?:script|img|link|iframe|source)\b[^>]*\b(?:src|href)="(https?:\/\/[^"]+)"/gi)];
  for (const m of external) fail(`index.html 引用了外网资源（离线会失效）：${m[1]}`);
  if (!/id="ch-1"/.test(html)) fail('index.html 里没有找到章节内容，构建可能不完整');
  if (!html.includes('vendor/mathjax/tex-svg.js')) fail('index.html 没有引用本地 MathJax');
}

/* 4. 本地 MathJax */
const mathjax = path.join(ROOT, 'vendor', 'mathjax', 'tex-svg.js');
if (!fs.existsSync(mathjax)) {
  fail('缺少 vendor/mathjax/tex-svg.js');
} else if (fs.statSync(mathjax).size < 100_000) {
  fail('vendor/mathjax/tex-svg.js 文件过小，下载可能不完整');
}

/* 5. 未使用的图片 */
const assetsDir = path.join(ROOT, 'assets', 'figs');
if (fs.existsSync(assetsDir)) {
  for (const abs of walk(assetsDir)) {
    const rel = path.relative(path.join(ROOT, 'assets'), abs).split(path.sep).join('/');
    if (!used.has(rel)) warn(`图片未被任何章节引用：assets/${rel}`);
  }
}

/* 6. 构建产物是否过期 */
if (fs.existsSync(OUT)) {
  const newest = walk(path.join(ROOT, 'src'))
    .map((f) => fs.statSync(f).mtimeMs)
    .reduce((a, b) => Math.max(a, b), 0);
  if (fs.statSync(OUT).mtimeMs < newest) {
    warn('index.html 比 src/ 中的源文件旧，可能没有重新构建（npm run build）');
  }
}

/* 输出 */
console.log(`检查了 ${chapters.length} 个章节文件、${imageCount} 处图片引用。`);
for (const w of warnings) console.log('警告: ' + w);
for (const e of errors) console.error('错误: ' + e);

if (errors.length) {
  console.error(`\n✗ 检查未通过：${errors.length} 个错误，${warnings.length} 个警告`);
  process.exit(1);
}
console.log(`\n✓ 检查通过${warnings.length ? `（${warnings.length} 个警告）` : ''}，页面可以离线独立运行。`);
