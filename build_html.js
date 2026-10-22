const fs = require('fs');
const path = require('path');
const dir = __dirname;

const files = [
  '00_使用说明.md',
  '01_L1_机构与四杆基础.md',
  '02_L2_四杆分析与综合.md',
  '03_L3_电机与传动.md',
  '04_L4_设计流程材料与齿轮几何.md',
  '05_L5_齿轮受力与强度.md',
  '06_公式速查.md',
  '07_模拟卷.md',
  '08_模拟卷答案.md',
  '09_附录_带与链.md'
];

let mathStore = [];
let secGlobal = 0;

function esc(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function protectMath(text) {
  text = text.replace(/\$\$([\s\S]*?)\$\$/g, function (m, g) {
    mathStore.push({ d: 1, tex: g });
    return 'XQM' + (mathStore.length - 1) + 'XQ';
  });
  text = text.replace(/\$([^$\n]+?)\$/g, function (m, g) {
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
  out = out.replace(/`([^`]+)`/g, function (m, c) {
    codes.push(c);
    return 'XQC' + (codes.length - 1) + 'XQ';
  });
  out = out.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img alt="$1" src="$2">');
  out = out.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
  out = out.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  out = out.replace(/(^|[^*])\*([^*\n]+)\*/g, '$1<em>$2</em>');
  out = out.replace(/XQC(\d+)XQ/g, function (m, n) { return '<code>' + codes[+n] + '</code>'; });
  out = out.replace(/(^|\s)(https?:\/\/[^\s<]+)/g, function (m, pre, url) {
    return pre + '<a href="' + url + '" target="_blank" rel="noopener">' + url + '</a>';
  });
  out = out.replace(/XQM(\d+)XQ/g, function (m, n) { return mathHtml(+n); });
  return out;
}

function plain(s) {
  return s.replace(/\$([^$]*)\$/g, '$1').replace(/\*\*/g, '').replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');
}

function splitRow(l) {
  return l.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map(function (x) { return x.trim(); });
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
  let out = [];
  let i = 0, open = false;
  const headings = [];
  while (i < lines.length) {
    let line = lines[i];
    if (!line.trim()) { i++; continue; }

    let m = line.match(/^(#{1,6})\s+(.*)$/);
    if (m) {
      const lv = m[1].length, txt = m[2].trim();
      if (lv === 1) {
        if (open) out.push('</section>');
        secGlobal++;
        const id = 'ch-' + secGlobal;
        headings.push({ lv: 1, text: txt, id: id });
        out.push('<section class="chapter" id="' + id + '">');
        open = true;
        out.push('<h1>' + inline(txt) + '</h1>');
      } else {
        secGlobal++;
        const id = 'sec-' + secGlobal;
        if (lv <= 2) headings.push({ lv: lv, text: txt, id: id });
        out.push('<h' + lv + ' id="' + id + '">' + inline(txt) + '</h' + lv + '>');
      }
      i++; continue;
    }

    if (/^---+$/.test(line.trim())) { out.push('<hr>'); i++; continue; }

    if (/^```/.test(line.trim())) {
      i++;
      let buf = [];
      while (i < lines.length && !/^```/.test(lines[i].trim())) { buf.push(lines[i]); i++; }
      i++;
      out.push('<pre class="code"><code>' + esc(buf.join('\n')) + '</code></pre>');
      continue;
    }

    if (/^>\s?/.test(line)) {
      let buf = [];
      while (i < lines.length && /^>/.test(lines[i])) {
        buf.push(lines[i].replace(/^>\s?/, ''));
        i++;
      }
      out.push('<blockquote>' + buf.map(function (x) { return '<p>' + inline(x) + '</p>'; }).join('') + '</blockquote>');
      continue;
    }

    if (/^\|/.test(line.trim())) {
      let j = i + 1;
      if (j < lines.length && /^\|[\s:|-]+\|$/.test(lines[j].trim())) {
        const head = splitRow(line);
        j++;
        let rows = [];
        while (j < lines.length && /^\|/.test(lines[j].trim())) { rows.push(splitRow(lines[j])); j++; }
        out.push(renderTable(head, rows));
        i = j; continue;
      }
    }

    if (/^\s*([-*]|\d+\.)\s+/.test(line)) {
      const ordered = /^\s*\d+\.\s+/.test(line);
      let items = [];
      while (i < lines.length && /^\s*([-*]|\d+\.)\s+/.test(lines[i]) && (/^\s*\d+\.\s+/.test(lines[i]) === ordered)) {
        items.push(lines[i].replace(/^\s*([-*]|\d+\.)\s+/, ''));
        i++;
      }
      const tag = ordered ? 'ol' : 'ul';
      out.push('<' + tag + '>' + items.map(function (x) { return '<li>' + inline(x) + '</li>'; }).join('') + '</' + tag + '>');
      continue;
    }

    let buf = [line];
    i++;
    while (i < lines.length && lines[i].trim() && !isBlockStart(lines[i])) { buf.push(lines[i]); i++; }
    const joined = buf.join(' ');
    const stripped = joined.replace(/XQM\d+XQ/g, '').trim();
    const tokens = [];
    joined.replace(/XQM(\d+)XQ/g, function (m, n) { tokens.push(+n); return m; });
    const allDisplay = tokens.length > 0 && tokens.every(function (n) { return mathStore[n].d === 1; });
    if (allDisplay && stripped === '') {
      for (const n of tokens) out.push('<div class="mathblock">' + mathHtml(n) + '</div>');
    } else {
      const lead = joined.match(/^((?:XQM\d+XQ)+)\s*/);
      let leadTokens = [];
      if (lead) { lead[1].replace(/XQM(\d+)XQ/g, function (m, n) { leadTokens.push(+n); return m; }); }
      if (lead && leadTokens.every(function (n) { return mathStore[n].d === 1; })) {
        lead[1].replace(/XQM(\d+)XQ/g, function (m, n) {
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
  return { html: out.join('\n'), headings: headings };
}

// ---------- 读取与解析 ----------
let body = '';
let headings = [];
for (const f of files) {
  const md = fs.readFileSync(path.join(dir, f), 'utf8');
  const r = parse(md);
  body += r.html + '\n';
  headings = headings.concat(r.headings);
}

// ---------- 目录 ----------
let toc = '<div class="navtitle">目录</div><nav><ul class="toc">';
let openChap = false;
for (const h of headings) {
  if (h.lv === 1) {
    if (openChap) toc += '</ul></li>';
    toc += '<li class="chap"><a href="#' + h.id + '">' + plain(h.text) + '</a><ul>';
    openChap = true;
  } else if (h.lv === 2) {
    toc += '<li><a href="#' + h.id + '">' + plain(h.text) + '</a></li>';
  }
}
if (openChap) toc += '</ul></li>';
toc += '</ul></nav>';

// ---------- 样式 ----------
const css = [
  ':root{--ink:#20242b;--muted:#5b6675;--line:#dfe5ec;--accent:#0d3b66;--accent2:#14618f;--paper:#f4f1ea;--card:#ffffff;--soft:#f3f8fc;}',
  '*{box-sizing:border-box}',
  'html{scroll-behavior:smooth}',
  'body{margin:0;background:var(--paper);color:var(--ink);font-family:"Segoe UI","PingFang SC","Microsoft YaHei",system-ui,sans-serif;line-height:1.9;font-size:16px}',
  '.top{background:linear-gradient(135deg,#0b2f52 0%,#0d3b66 45%,#14618f 100%);color:#fff;padding:46px 0 34px}',
  '.top .wrap{max-width:1180px;margin:0 auto;padding:0 28px}',
  '.kicker{font-size:12px;letter-spacing:3px;color:#9fc6e8;margin-bottom:10px}',
  '.top h1{margin:0;font-size:34px;letter-spacing:2px;font-weight:700;border:none;padding:0}',
  '.top .sub{margin:10px 0 0;font-size:15px;color:#d6e6f3}',
  '.top .hint{margin:12px 0 0;font-size:13px;color:#a9c4da}',
  '.printbtn{display:inline-block;margin-top:16px;padding:7px 16px;border:1px solid rgba(255,255,255,.5);border-radius:20px;color:#fff;font-size:13px;cursor:pointer;background:transparent}',
  '.printbtn:hover{background:rgba(255,255,255,.12)}',
  '.layout{max-width:1280px;margin:0 auto;padding:26px 20px 70px;display:flex;gap:26px;align-items:flex-start}',
  '.sidebar{width:272px;flex:0 0 272px;position:sticky;top:20px;max-height:calc(100vh - 40px);overflow:auto;background:var(--card);border-radius:14px;padding:18px 16px;box-shadow:0 8px 28px rgba(13,59,102,.08)}',
  '.navtitle{font-size:12px;letter-spacing:3px;color:var(--muted);margin:0 0 10px 8px}',
  '.toc{list-style:none;margin:0;padding:0;font-size:13.5px}',
  '.toc li{margin:1px 0}',
  '.toc a{display:block;padding:4px 9px;border-radius:6px;color:#3a4655;text-decoration:none;border-left:3px solid transparent}',
  '.toc a:hover{background:#eef4fa;color:var(--accent)}',
  '.toc .chap>a{font-weight:700;color:var(--accent);margin-top:8px;font-size:13.5px}',
  '.toc .chap ul{list-style:none;padding-left:10px;margin:2px 0 6px}',
  '.toc .chap ul a{font-size:12.5px;color:#5c6b7d;padding:3px 8px}',
  '.content{flex:1;min-width:0;background:var(--card);border-radius:16px;padding:42px 52px;box-shadow:0 10px 36px rgba(13,59,102,.09)}',
  'h1{font-size:29px;line-height:1.4;margin:0 0 22px;padding-bottom:12px;border-bottom:3px solid var(--accent);letter-spacing:1px}',
  'h2{font-size:21px;margin:38px 0 14px;padding-left:12px;border-left:6px solid var(--accent);line-height:1.5}',
  'h3{font-size:17px;margin:26px 0 10px;color:var(--accent2)}',
  'h4{font-size:15.5px;margin:20px 0 8px;color:#274b6b}',
  'p{margin:11px 0;text-align:justify}',
  'code{background:#eaf1f7;color:#0b4a6f;padding:1px 5px;border-radius:4px;font-family:"Cascadia Code","Consolas",monospace;font-size:.92em}',
  'strong{color:#0b2f52}',
  'a{color:var(--accent2)}',
  'hr{border:none;border-top:1px dashed #cfd8e1;margin:30px 0}',
  '.chapter{margin-bottom:54px}',
  '.chapter:last-child{margin-bottom:0}',
  'ul,ol{padding-left:26px;margin:10px 0}',
  'li{margin:5px 0}',
  '.tablewrap{overflow-x:auto;margin:18px 0}',
  'table{border-collapse:collapse;width:100%;font-size:14.5px;background:#fff}',
  'th,td{border:1px solid var(--line);padding:8px 11px;vertical-align:top;text-align:left}',
  'th{background:#e9f1f8;color:var(--accent);font-weight:600;white-space:normal}',
  'tbody tr:nth-child(even){background:#fbfcfd}',
  'blockquote{margin:16px 0;padding:10px 18px;background:var(--soft);border-left:4px solid #3d8bcd;border-radius:0 10px 10px 0;color:#2f4358}',
  'blockquote p{margin:6px 0}',
  'img{max-width:100%;height:auto;display:block;margin:20px auto 8px;border:1px solid #e3e8ee;border-radius:10px;background:#fff}',
  'p:has(>em:only-child){text-align:center;font-size:13px;color:#5b6675;margin:0 auto 18px;line-height:1.6}',
  '.content img{cursor:zoom-in;transition:box-shadow .15s}',
  '.content img:hover{box-shadow:0 6px 20px rgba(13,59,102,.18)}',
  '.mathblock{margin:16px 0;overflow-x:auto}',
  'pre.code{background:#0f2740;color:#e8eef5;padding:16px 18px;border-radius:10px;overflow-x:auto;font-size:13px;line-height:1.7;font-family:"Cascadia Code","Consolas",monospace}',
  'pre.code code{background:none;color:inherit;padding:0}',
  'mjx-container[display="true"]{margin:14px 0!important;overflow-x:auto;overflow-y:hidden;max-width:100%}',
  'footer{max-width:1180px;margin:0 auto;padding:0 28px 40px;color:#8b96a5;font-size:12.5px;text-align:center}',
  '@media (max-width:960px){.sidebar{display:none}.layout{padding:16px 10px 50px}.content{padding:26px 20px;border-radius:10px}.top h1{font-size:25px}.top{padding:32px 0 24px}}',
  '@media print{body{background:#fff}.top{background:#fff;color:#000;padding:0 0 10px;border-bottom:2px solid #000}.top .kicker,.top .hint,.printbtn,footer{display:none}.top h1{font-size:26px}.top .sub{color:#333}.layout{display:block;padding:0;max-width:none}.sidebar{display:none}.content{box-shadow:none;padding:0;border-radius:0}.chapter{page-break-before:always}.chapter:first-child{page-break-before:auto}h1,h2,h3{page-break-after:avoid}table,img,blockquote{page-break-inside:avoid}a{color:inherit;text-decoration:none}}'
].join('\n');

const html = [
  '<!DOCTYPE html>',
  '<html lang="zh-CN">',
  '<head>',
  '<meta charset="utf-8">',
  '<meta name="viewport" content="width=device-width, initial-scale=1">',
  '<title>设计与制造 1 · L1–L5 复习</title>',
  '<style>',
  css,
  '</style>',
  '</head>',
  '<body>',
  '<header class="top"><div class="wrap">',
  '<div class="kicker">DESIGN &amp; MANUFACTURING</div>',
  '<h1>设计与制造 1 · L1–L5 复习</h1>',
  '<p class="sub">L1 机构基础 · L2 四杆分析与综合 · L3 电机与传动 · L4 设计流程/材料/齿轮几何 · L5 齿轮受力与强度</p>',
  '<p class="hint">按官方课件 L1–L5 组织：概念 + 公式 + 例题 + 说明；公式由 MathJax 渲染（需联网），Ctrl+P 可打印或存 PDF。</p>',
  '<button class="printbtn" onclick="window.print()">打印 / 存 PDF</button>',
  '</div></header>',
  '<div class="layout">',
  '<aside class="sidebar">',
  toc,
  '</aside>',
  '<main class="content">',
  body,
  '</main>',
  '</div>',
  '<footer>依据官方课件 L1–L5 与 2023 期末卷整理 · 【课件】为原文，【补充】已单独标注</footer>',
  '<script>',
  'window.MathJax = { tex: { inlineMath: [["$","$"]], displayMath: [["$$","$$"]] }, svg: { fontCache: "global" }, options: { skipHtmlTags: ["script","noscript","style","textarea","pre","code"] } };',
  '</script>',
  '<script async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>',
  '<script>',
  'document.querySelectorAll(".content img").forEach(function (im) {',
  '  im.title = "点击查看原图";',
  '  im.addEventListener("click", function () { window.open(im.src, "_blank"); });',
  '});',
  '</script>',
  '</body>',
  '</html>'
].join('\n');

fs.writeFileSync(path.join(dir, 'index.html'), html, 'utf8');
console.log('wrote index.html', html.length, 'chars,', headings.length, 'headings,', mathStore.length, 'math items');
