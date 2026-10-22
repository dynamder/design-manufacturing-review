#!/usr/bin/env node
/**
 * 开发模式：构建一次 -> 启动本地服务器 -> 监听 src/ 变化并自动重建。
 *
 *   npm run dev
 */
import { watch } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { build } from './build.mjs';
import { startServer } from './serve.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '..');
const PORT = Number(process.env.PORT) || 5173;

build();
const server = startServer({ root: ROOT, port: PORT });

let timer = null;
function scheduleBuild() {
  clearTimeout(timer);
  timer = setTimeout(() => {
    try {
      build();
    } catch (err) {
      console.error('构建失败:', err.message);
    }
  }, 150);
}

try {
  watch(path.join(ROOT, 'src'), { recursive: true }, scheduleBuild);
  console.log('正在监听 src/ 变化（Ctrl+C 退出）');
} catch (err) {
  console.warn('无法递归监听 src/：' + err.message + '；修改后请手动运行 npm run build');
}

function shutdown() {
  server.close(() => process.exit(0));
}
process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);
