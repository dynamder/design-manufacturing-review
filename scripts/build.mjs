import { execSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { assemble } from "./assemble.mjs";

// One-command build:
//   catalog.json -> mdbook build per course -> gleam build -> bundle -> dist/
//
// Child processes are used only here. The rest of the build (catalog + dist
// assembly) is plain Node so it can be tested in isolation.

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const site = path.join(root, "site");

function run(command, cwd) {
  console.log(`$ ${command}`);
  execSync(command, { cwd, stdio: "inherit" });
}

run(`"${process.execPath}" "scripts/gen-catalog.mjs"`, root);

const catalog = JSON.parse(
  fs.readFileSync(path.join(root, "catalog.json"), "utf8"),
);

for (const course of catalog.courses) {
  const dir = path.join(root, "courses", course.slug);
  const summary = path.join(dir, "src", "SUMMARY.md");
  if (!fs.existsSync(summary)) continue;
  run(`mdbook build "${dir}"`, root);
}

run("gleam build", site);
run(`"${process.execPath}" "scripts/bundle.mjs"`, site);

assemble();
