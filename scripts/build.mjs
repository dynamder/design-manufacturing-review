#!/usr/bin/env node
/**
 * 构建脚本：src/ -> index.html
 *
 * 内容来源：
 *   src/content/NN_*.md  章节目录（按文件名排序）
 *   src/styles/main.css  页面样式（内联进 HTML）
 *   src/template.html    页面骨架
 *   src/site.json        标题、副标题等站点信息
 *
 * 输出：项目根目录的 index.html（可直接双击打开，无需服务器）
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '..');
const SRC = path.join(ROOT, 'src');
const CONTENT = path.join(SRC, 'content');
const SITE_FILE = path.join(SRC, 'site.json');
const STYLE_FILE = path.join(SRC, 'styles', 'main.css');
const TEMPLATE_FILE = path.join(SRC, 'template.html');
const OUTPUT_FILE = path.join(ROOT, 'index.html');

/* ---------- Markdown 解析（轻量实现，覆盖本项目用到的语法） ---------- */

let mathStore = [];
let secGlobal = 0;

function esc(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function protectMath(text) {
  text = text.replace(/\$\$([\s\S]*?)\$\$/g, (m, g) => {
    mathStore.push({ d: 1, tex: g });
    return 'XQM' + (mathStore.length - 1) + 'XQ';
  });
  text = text.replace(/\$([^$\n]+?)\$/g, (m, g) => {
    mathStore.push({ d: 0, tex: g });
    return 'XQM' + (mathStore.length - 1) + 'XQ';
  });
  return text;
}

function mathHtml(n) {
  const o = mathStore[n];
  return o.d ? '$$' + esc(o.tex) + '$$' : '$' + esc(o.tex) + '$';
}

function inline(s) {
  let out = esc(s);
  // 行内代码先占位，避免被 * / ** 规则误伤
  const codes = [];
  out = out.replace(/`([^`]+)`/g, (m, c) => {
    codes.push(c);
    return 'XQC' + (codes.length - 1) + 'XQ';
  });
  out = out.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img alt="$1" src="$2">');
  out = out.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
  out = out.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  out = out.replace(/(^|[^*])\*([^*\n]+)\*/g, '$1<em>$2</em>');
  out = out.replace(/XQC(\d+)XQ/g, (m, n) => '<code>' + codes[+n] + '</code>');
  out = out.replace(/(^|\s)(https?:\/\/[^\s<]+)/g, (m, pre, url) => {
    return pre + '<a href="' + url + '" target="_blank" rel="noopener">' + url + '</a>';
  });
  out = out.replace(/XQM(\d+)XQ/g, (m, n) => mathHtml(+n));
  return out;
}

function plain(s) {
  return s.replace(/\$([^$]*)\$/g, '$1').replace(/\*\*/g, '').replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');
}

function splitRow(l) {
  return l.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map((x) => x.trim());
}

function renderTable(head, rows) {
  let h = '<div class="tablewrap"><table><thead><tr>';
  for (const c of head) h += '<th>' + inline(c) + '</th>';
  h += '</tr></thead><tbody>';
  for (const r of rows) {
    h += '<tr>';
    for (let k = 0; k < head.length; k++) h += '<td>' + inline(r[k] === undefined ? '' : r[k]) + '</td>';
    h += '</tr>';
  }
  return h + '</tbody></table></div>';
}

function isBlockStart(line) {
  return /^(#{1,6}\s|>\s?|\||```)/.test(line) || /^\s*([-*]|\d+\.)\s+/.test(line) || /^---+$/.test(line.trim());
}

function parse(md) {
  md = md.replace(/\r\n/g, '\n');
  md = protectMath(md);
  const lines = md.split('\n');
  const out = [];
  const headings = [];
  let i = 0;
  let open = false;

  while (i < lines.length) {
    const line = lines[i];
    if (!line.trim()) { i++; continue; }

    const m = line.match(/^(#{1,6})\s+(.*)$/);
    if (m) {
      const lv = m[1].length;
      const txt = m[2].trim();
      if (lv === 1) {
        if (open) out.push('</section>');
        secGlobal++;
        const id = 'ch-' + secGlobal;
        headings.push({ lv: 1, text: txt, id });
        out.push('<section class="chapter" id="' + id + '">');
        open = true;
        out.push('<h1>' + inline(txt) + '</h1>');
      } else {
        secGlobal++;
        const id = 'sec-' + secGlobal;
        if (lv <= 2) headings.push({ lv, text: txt, id });
        out.push('<h' + lv + ' id="' + id + '">' + inline(txt) + '</h' + lv + '>');
      }
      i++;
      continue;
    }

    if (/^---+$/.test(line.trim())) { out.push('<hr>'); i++; continue; }

    if (/^```/.test(line.trim())) {
      i++;
      const buf = [];
      while (i < lines.length && !/^```/.test(lines[i].trim())) { buf.push(lines[i]); i++; }
      i++;
      out.push('<pre class="code"><code>' + esc(buf.join('\n')) + '</code></pre>');
      continue;
    }

    if (/^>\s?/.test(line)) {
      const buf = [];
      while (i < lines.length && /^>/.test(lines[i])) {
        buf.push(lines[i].replace(/^>\s?/, ''));
        i++;
      }
      out.push('<blockquote>' + buf.map((x) => '<p>' + inline(x) + '</p>').join('') + '</blockquote>');
      continue;
    }

    if (/^\|/.test(line.trim())) {
      let j = i + 1;
      if (j < lines.length && /^\|[\s:|-]+\|$/.test(lines[j].trim())) {
        const head = splitRow(line);
        j++;
        const rows = [];
        while (j < lines.length && /^\|/.test(lines[j].trim())) { rows.push(splitRow(lines[j])); j++; }
        out.push(renderTable(head, rows));
        i = j;
        continue;
      }
    }

    if (/^\s*([-*]|\d+\.)\s+/.test(line)) {
      const ordered = /^\s*\d+\.\s+/.test(line);
      const items = [];
      while (i < lines.length && /^\s*([-*]|\d+\.)\s+/.test(lines[i]) && (/^\s*\d+\.\s+/.test(lines[i]) === ordered)) {
        items.push(lines[i].replace(/^\s*([-*]|\d+\.)\s+/, ''));
        i++;
      }
      const tag = ordered ? 'ol' : 'ul';
      out.push('<' + tag + '>' + items.map((x) => '<li>' + inline(x) + '</li>').join('') + '</' + tag + '>');
      continue;
    }

    const buf = [line];
    i++;
    while (i < lines.length && lines[i].trim() && !isBlockStart(lines[i])) { buf.push(lines[i]); i++; }
    const joined = buf.join(' ');
    const stripped = joined.replace(/XQM\d+XQ/g, '').trim();
    const tokens = [];
    joined.replace(/XQM(\d+)XQ/g, (m, n) => { tokens.push(+n); return m; });
    const allDisplay = tokens.length > 0 && tokens.every((n) => mathStore[n].d === 1);
    if (allDisplay && stripped === '') {
      for (const n of tokens) out.push('<div class="mathblock">' + mathHtml(n) + '</div>');
    } else {
      const lead = joined.match(/^((?:XQM\d+XQ)+)\s*/);
      const leadTokens = [];
      if (lead) { lead[1].replace(/XQM(\d+)XQ/g, (m, n) => { leadTokens.push(+n); return m; }); }
      if (lead && leadTokens.every((n) => mathStore[n].d === 1)) {
        lead[1].replace(/XQM(\d+)XQ/g, (m, n) => {
          out.push('<div class="mathblock">' + mathHtml(+n) + '</div>');
          return m;
        });
        const rest = joined.slice(lead[0].length);
        if (rest.trim()) out.push('<p>' + inline(rest) + '</p>');
      } else {
        out.push('<p>' + inline(joined) + '</p>');
      }
    }
  }

  if (open) out.push('</section>');
  return { html: out.join('\n'), headings };
}

/* ---------- 站点构建 ---------- */

function listChapters() {
  const files = fs.readdirSync(CONTENT)
    .filter((f) => /^\d{2}_.+\.md$/.test(f))
    .sort((a, b) => a.localeCompare(b, 'zh-CN'));
  if (!files.length) throw new Error('src/content 下没有找到 NN_*.md 章节文件');
  return files;
}

function renderToc(headings) {
  let toc = '<div class="navtitle">目录</div><nav aria-label="章节目录"><ul class="toc">';
  let openChap = false;
  for (const h of headings) {
    if (h.lv === 1) {
      if (openChap) toc += '</ul></li>';
      toc += '<li class="chap"><a href="#' + h.id + '">' + esc(plain(h.text)) + '</a><ul>';
      openChap = true;
    } else if (h.lv === 2) {
      toc += '<li><a href="#' + h.id + '">' + esc(plain(h.text)) + '</a></li>';
    }
  }
  if (openChap) toc += '</ul></li>';
  toc += '</ul></nav>';
  return toc;
}

function checkAssets(html) {
  const refs = [...html.matchAll(/(?:src|href)="((?:assets|vendor)\/[^"]+)"/g)].map((m) => m[1]);
  const missing = [...new Set(refs)].filter((rel) => !fs.existsSync(path.join(ROOT, rel)));
  if (missing.length) throw new Error('引用了不存在的资源：\n  ' + missing.join('\n  '));
}

export function build() {
  mathStore = [];
  secGlobal = 0;

  const site = JSON.parse(fs.readFileSync(SITE_FILE, 'utf8'));
  const css = fs.readFileSync(STYLE_FILE, 'utf8').trim();
  const template = fs.readFileSync(TEMPLATE_FILE, 'utf8');
  const chapters = listChapters();

  let body = '';
  let headings = [];
  for (const file of chapters) {
    const md = fs.readFileSync(path.join(CONTENT, file), 'utf8');
    const result = parse(md);
    body += result.html + '\n';
    headings = headings.concat(result.headings);
  }

  const values = {
    LANG: esc(site.lang || 'zh-CN'),
    TITLE: esc(site.title || ''),
    KICKER: esc(site.kicker || ''),
    HEADING: esc(site.heading || site.title || ''),
    SUBTITLE: esc(site.subtitle || ''),
    HINT: esc(site.hint || ''),
    FOOTER: esc(site.footer || ''),
    TOC: renderToc(headings),
    BODY: body,
    CSS: css,
  };

  const html = template.replace(/\{\{([A-Z_]+)\}\}/g, (m, key) => {
    if (!(key in values)) throw new Error('模板中有未知占位符：{{' + key + '}}');
    return values[key];
  });

  const leftover = html.match(/\{\{[A-Z_]+\}\}/);
  if (leftover) throw new Error('模板占位符未全部替换：' + leftover[0]);

  checkAssets(html);
  fs.writeFileSync(OUTPUT_FILE, html, 'utf8');

  console.log(
    '构建完成: index.html  ' + html.length + ' 字符 · ' +
    chapters.length + ' 个文件 · ' + headings.length + ' 个目录项 · ' +
    mathStore.length + ' 个公式'
  );
}

const isMain = process.argv[1] && pathToFileURL(process.argv[1]).href === import.meta.url;
if (isMain) {
  try {
    build();
  } catch (err) {
    console.error('构建失败:', err.message);
    process.exit(1);
  }
}
