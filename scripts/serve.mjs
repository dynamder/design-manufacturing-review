import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

// Minimal static server for dist/. No dependencies, no fallback routing:
// unknown paths get the branded 404 page, like GitHub Pages.

const root = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "..",
  "dist",
);
const port = Number(process.env.PORT) || 5173;

const mime = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".mjs": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".svg": "image/svg+xml",
  ".woff2": "font/woff2",
  ".ico": "image/x-icon",
  ".txt": "text/plain; charset=utf-8",
};

function send(response, status, file) {
  fs.readFile(file, (error, data) => {
    if (error) {
      response.writeHead(500, { "Content-Type": "text/plain; charset=utf-8" });
      response.end("500 Internal Server Error");
      return;
    }
    response.writeHead(status, {
      "Content-Type": mime[path.extname(file)] ?? "application/octet-stream",
      "Cache-Control": "no-store",
    });
    response.end(data);
  });
}

const server = http.createServer((request, response) => {
  const url = new URL(request.url, "http://localhost");
  const pathname = decodeURIComponent(url.pathname);
  let file = path.resolve(root, "." + pathname);

  if (file !== root && !file.startsWith(root + path.sep)) {
    response.writeHead(403).end("Forbidden");
    return;
  }

  if (fs.existsSync(file) && fs.statSync(file).isDirectory()) {
    file = path.join(file, "index.html");
  }

  if (!fs.existsSync(file)) {
    send(response, 404, path.join(root, "404.html"));
    return;
  }

  send(response, 200, file);
});

server.listen(port, "127.0.0.1", () => {
  console.log(`课程资料库: http://127.0.0.1:${port}/`);
  console.log(`（静态目录：${root}）`);
});
