import { defineConfig } from "tsup";

export default defineConfig([
  // Node entry — tiny JS, reads filter.bin from disk
  {
    entry: { index: "src/index.ts" },
    format: ["esm", "cjs"],
    dts: true,
    clean: true,
    minify: true,
    splitting: false,
    sourcemap: false,
    treeshake: true,
  },
  // Browser entry — self-contained, filter embedded as base64
  {
    entry: { browser: "src/browser.ts" },
    format: ["esm"],
    dts: true,
    clean: false, // don't wipe the Node build
    minify: true,
    splitting: false,
    sourcemap: false,
    treeshake: true,
  },
]);
