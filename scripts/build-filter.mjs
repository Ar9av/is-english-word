/**
 * Generates an Xor filter from a word list.
 *
 * Supports two modes:
 *   xor8  — 8-bit fingerprints, ~1.23n bytes, FP ≈ 0.39%  (default)
 *   xor16 — 16-bit fingerprints, ~2.46n bytes, FP ≈ 0.0015%
 *
 * Outputs:
 *   - data/filter.bin  (filter fingerprint array)
 *   - data/meta.json   (seed, segmentLength, arrayLength, fingerprint bits)
 *
 * Usage:
 *   node scripts/build-filter.mjs [options] [path-to-word-list]
 *
 * Options:
 *   --bits=8|16      Fingerprint size (default: 8)
 *   --words=<path>   Path to newline-separated word list
 *                    (default: /usr/share/dict/words)
 *
 * Examples:
 *   node scripts/build-filter.mjs
 *   node scripts/build-filter.mjs --bits=16
 *   node scripts/build-filter.mjs --words=./my-words.txt
 *   node scripts/build-filter.mjs --bits=16 --words=./my-words.txt
 */

import { readFileSync, writeFileSync, mkdirSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, "..");

// ── Parse args ──────────────────────────────────────────────────────────────
let fpBits = 8;
let wordListPath = "/usr/share/dict/words";

for (const arg of process.argv.slice(2)) {
  if (arg.startsWith("--bits=")) {
    fpBits = parseInt(arg.slice(7), 10);
    if (fpBits !== 8 && fpBits !== 16) {
      console.error("Error: --bits must be 8 or 16");
      process.exit(1);
    }
  } else if (arg.startsWith("--words=")) {
    wordListPath = arg.slice(8);
  } else if (!arg.startsWith("-")) {
    wordListPath = arg; // positional fallback
  }
}

const fpMask = fpBits === 8 ? 0xff : 0xffff;
const fpLabel = `xor${fpBits}`;
const expectedFpRate = 1 / (1 << fpBits);

console.log(`Mode: ${fpLabel} (${fpBits}-bit fingerprints, FP ≈ ${(expectedFpRate * 100).toFixed(4)}%)`);

// ── Read & clean words ──────────────────────────────────────────────────────
const raw = readFileSync(wordListPath, "utf-8");
const words = [
  ...new Set(
    raw
      .split(/\r?\n/)
      .map((w) => w.trim().toLowerCase())
      .filter((w) => w.length > 0 && /^[a-z]+$/.test(w))
  ),
];
console.log(`Words: ${words.length}`);

// ── Hash functions ──────────────────────────────────────────────────────────
const FNV_SEED1 = 0x811c9dc5;
const FNV_SEED2 = 0xc6a4a793;
const FNV_PRIME = 0x01000193;

function fnv1a(str, seed) {
  let h = seed;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = Math.imul(h, FNV_PRIME);
  }
  return h >>> 0;
}

function mix32(x) {
  x = Math.imul(x ^ (x >>> 16), 0x85ebca6b);
  x = Math.imul(x ^ (x >>> 13), 0xc2b2ae35);
  return (x ^ (x >>> 16)) >>> 0;
}

function getPositions(ha, hb, seed, segLen) {
  const r0 = mix32((ha ^ seed) >>> 0);
  const r1 = mix32((hb ^ seed) >>> 0);
  const r2 = mix32(((ha ^ hb) ^ seed) >>> 0);
  return {
    h0: r0 % segLen,
    h1: segLen + (r1 % segLen),
    h2: 2 * segLen + (r2 % segLen),
    fp: (r0 ^ r1 ^ r2) & fpMask,
  };
}

// ── Pre-hash all words ──────────────────────────────────────────────────────
const keyHashes = words.map((w) => ({
  ha: fnv1a(w, FNV_SEED1),
  hb: fnv1a(w, FNV_SEED2),
}));

// ── Xor filter construction ────────────────────────────────────────────────
const n = words.length;
const segLen = Math.ceil((n * 1.23) / 3);
const arrayLen = 3 * segLen;
const bytesPerEntry = fpBits / 8;
const totalBytes = arrayLen * bytesPerEntry;

console.log(`Filter: ${arrayLen} entries × ${bytesPerEntry}B = ${totalBytes} bytes (${(totalBytes / 1024).toFixed(1)} KB)`);

let filterEntries; // Uint8Array or Uint16Array
let constructionSeed = 0;

for (let seed = 0; ; seed++) {
  const positions = keyHashes.map(({ ha, hb }) => getPositions(ha, hb, seed, segLen));

  // Peeling: count + XOR-of-indices per position
  const count = new Int32Array(arrayLen);
  const keyXor = new Int32Array(arrayLen);

  for (let i = 0; i < n; i++) {
    const { h0, h1, h2 } = positions[i];
    count[h0]++;  keyXor[h0] ^= i;
    count[h1]++;  keyXor[h1] ^= i;
    count[h2]++;  keyXor[h2] ^= i;
  }

  const queue = [];
  for (let j = 0; j < arrayLen; j++) {
    if (count[j] === 1) queue.push(j);
  }

  const stack = [];
  while (queue.length > 0) {
    const pos = queue.pop();
    if (count[pos] !== 1) continue;
    const keyIdx = keyXor[pos];
    stack.push({ keyIdx, pos });
    const { h0, h1, h2 } = positions[keyIdx];
    for (const h of [h0, h1, h2]) {
      count[h]--;
      keyXor[h] ^= keyIdx;
      if (count[h] === 1) queue.push(h);
    }
  }

  if (stack.length !== n) {
    console.log(`  Seed ${seed}: peeling incomplete (${stack.length}/${n}), retrying...`);
    continue;
  }

  console.log(`  Seed ${seed}: peeling complete ✓`);
  constructionSeed = seed;

  // Assign fingerprints in reverse peel order
  filterEntries = fpBits === 8 ? new Uint8Array(arrayLen) : new Uint16Array(arrayLen);
  for (let i = stack.length - 1; i >= 0; i--) {
    const { keyIdx, pos } = stack[i];
    const { h0, h1, h2, fp } = positions[keyIdx];
    filterEntries[pos] = fp ^ filterEntries[h0] ^ filterEntries[h1] ^ filterEntries[h2];
  }
  break;
}

// ── Verify ──────────────────────────────────────────────────────────────────
let misses = 0;
for (let i = 0; i < n; i++) {
  const { ha, hb } = keyHashes[i];
  const { h0, h1, h2, fp } = getPositions(ha, hb, constructionSeed, segLen);
  if (fp !== ((filterEntries[h0] ^ filterEntries[h1] ^ filterEntries[h2]) & fpMask)) misses++;
}
if (misses > 0) {
  console.error(`ERROR: ${misses} words not found in filter!`);
  process.exit(1);
}
console.log(`Verified: all ${n} words found ✓`);

// ── Empirical FP rate ───────────────────────────────────────────────────────
let fpCount = 0;
const FP_TESTS = 100000;
for (let i = 0; i < FP_TESTS; i++) {
  const fake = "zzzz" + i.toString(36) + "qqqq";
  const ha = fnv1a(fake, FNV_SEED1);
  const hb = fnv1a(fake, FNV_SEED2);
  const p = getPositions(ha, hb, constructionSeed, segLen);
  if (p.fp === ((filterEntries[p.h0] ^ filterEntries[p.h1] ^ filterEntries[p.h2]) & fpMask)) fpCount++;
}
console.log(`Empirical FP rate: ${fpCount}/${FP_TESTS} = ${((fpCount / FP_TESTS) * 100).toFixed(4)}% (expected ≈ ${(expectedFpRate * 100).toFixed(4)}%)`);

// ── Write output ────────────────────────────────────────────────────────────
mkdirSync(resolve(ROOT, "data"), { recursive: true });

// Write as raw bytes (Uint8Array for xor8, little-endian Uint16 for xor16)
const buf = fpBits === 8
  ? Buffer.from(filterEntries.buffer)
  : Buffer.from(filterEntries.buffer);
writeFileSync(resolve(ROOT, "data", "filter.bin"), buf);

const metaObj = {
  type: fpLabel,
  fpBits,
  seed: constructionSeed,
  segmentLength: segLen,
  arrayLength: arrayLen,
  words: n,
};
writeFileSync(resolve(ROOT, "data", "meta.json"), JSON.stringify(metaObj));

// ── Write src/data.ts (embedded base64 for browser builds) ──────────────────
const b64 = buf.toString("base64");
const dataTs = `// Auto-generated by scripts/build-filter.mjs — do not edit
export const FILTER_B64 = "${b64}";
export const FP_BITS = ${fpBits};
export const SEED = ${constructionSeed};
export const SEGMENT_LENGTH = ${segLen};
export const ARRAY_LENGTH = ${arrayLen};
export const FP_MASK = 0x${fpMask.toString(16)};
`;
writeFileSync(resolve(ROOT, "src", "data.ts"), dataTs);

console.log(`\nWrote data/filter.bin (${(buf.length / 1024).toFixed(1)} KB)`);
console.log(`Wrote data/meta.json`);
console.log(`Wrote src/data.ts (${(b64.length / 1024).toFixed(1)} KB base64)`);
console.log(`\n${fpLabel}: ${n} words → ${(buf.length / 1024).toFixed(1)} KB, FP ≈ ${(expectedFpRate * 100).toFixed(4)}%`);
