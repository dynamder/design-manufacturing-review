import path from "node:path";
import { build } from "esbuild";

const root = process.cwd();

await build({
  entryPoints: [path.join(root, "scripts", "entry.js")],
  bundle: true,
  format: "iife",
  target: ["es2020"],
  outfile: path.join(root, "public", "app.js"),
  sourcemap: false,
  logLevel: "info",
});
