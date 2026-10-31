import fs from "node:fs";
import path from "node:path";

// Windows without Developer Mode cannot create the directory symlinks Gleam
// uses to link a package's `priv` directory. This sample does not use server
// components, so dropping the unused package assets is enough to build.
if (process.platform !== "win32") process.exit(0);

const packages = path.resolve("build", "packages");
if (!fs.existsSync(packages)) process.exit(0);

for (const name of fs.readdirSync(packages)) {
  const priv = path.join(packages, name, "priv");
  if (fs.existsSync(priv)) fs.rmSync(priv, { recursive: true, force: true });
}

console.log("stripped unused package priv directories (Windows symlink workaround)");
