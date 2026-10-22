#!/usr/bin/env node
/**
 * 零依赖静态文件服务器，用于本地预览构建结果。
 *
 *   npm run serve              # http://127.0.0.1:5173/
 *   PORT=8080 npm run serve    # 换端口
 *
 * 页面本身不需要服务器：直接双击 index.html 也能打开。
 */
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '..');

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.htm': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.md': 'text/markdown; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.webp': 'image/webp',
  '.ico': 'image/x-icon',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.ttf': 'font/ttf',
  '.map': 'application/json; charset=utf-8',
};

/**
 * @param {{ root?: string, port?: number, host?: string }} [options]
 * @returns {import('node:http').Server}
 */
export function startServer({ root = ROOT, port = 5173, host = '127.0.0.1' } = {}) {
  const server = http.createServer((req, res) => {
    let pathname;
    try {
      pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
    } catch {
      res.writeHead(400, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('400 Bad Request');
      return;
    }

    // 只允许访问 root 内的路径
    const file = path.resolve(root, '.' + pathname);
    if (file !== root && !file.startsWith(root + path.sep)) {
      res.writeHead(403, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('403 Forbidden');
      return;
    }

    fs.stat(file, (statErr, stat) => {
      const target = !statErr && stat.isDirectory() ? path.join(file, 'index.html') : file;
      fs.readFile(target, (readErr, data) => {
        if (readErr) {
          res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
          res.end('404 Not Found: ' + pathname);
          return;
        }
        res.writeHead(200, {
          'Content-Type': MIME[path.extname(target).toLowerCase()] || 'application/octet-stream',
          'Cache-Control': 'no-store',
        });
        res.end(data);
      });
    });
  });

  server.on('error', (err) => {
    if (err.code === 'EADDRINUSE') {
      console.error(`端口 ${port} 已被占用，可用 PORT=其他端口 npm run serve 重试。`);
    } else {
      console.error('服务器启动失败:', err.message);
    }
    process.exit(1);
  });

  server.listen(port, host, () => {
    console.log(`本地预览: http://${host}:${port}/`);
  });
  return server;
}

const isMain = process.argv[1] && pathToFileURL(process.argv[1]).href === import.meta.url;
if (isMain) {
  startServer({ port: Number(process.env.PORT) || 5173 });
}
