/**
 * Benchmark comparing each optimization against the baseline.
 * Each variant is self-contained so we measure the exact delta.
 */

import { readFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const _dir = dirname(fileURLToPath(import.meta.url));
const dataDir = resolve(_dir, "..", "data");
const meta: { numHashes: number; numBits: number } = JSON.parse(
  readFileSync(resolve(dataDir, "meta.json"), "utf-8")
);
const filterBuf = new Uint8Array(readFileSync(resolve(dataDir, "filter.bin")));

// ═══════════════════════════════════════════════════════════════════════════
// BASELINE — current implementation (as shipped)
// ═══════════════════════════════════════════════════════════════════════════

const baseline = (() => {
  const SEED1 = 0x811c9dc5;
  const SEED2 = 0xc6a4a793;
  const filter = filterBuf;

  function fnv1a(str: string, seed: number): number {
    let h = seed;
    for (let i = 0; i < str.length; i++) {
      h ^= str.charCodeAt(i);
      h = Math.imul(h, 0x01000193);
    }
    return h >>> 0;
  }

  return function isWord(word: string): boolean {
    const w = word.toLowerCase();
    if (w.length === 0 || !/^[a-z]+$/.test(w)) return false;

    const h1 = fnv1a(w, SEED1);
    const h2 = fnv1a(w, SEED2);

    for (let i = 0; i < meta.numHashes; i++) {
      const bit = ((h1 + Math.imul(i, h2)) >>> 0) % meta.numBits;
      if ((filter[bit >>> 3] & (1 << (bit & 7))) === 0) return false;
    }
    return true;
  };
})();

// ═══════════════════════════════════════════════════════════════════════════
// OPT 1 — Replace regex with charCode loop
// ═══════════════════════════════════════════════════════════════════════════

const opt1_noRegex = (() => {
  const SEED1 = 0x811c9dc5;
  const SEED2 = 0xc6a4a793;
  const filter = filterBuf;

  function fnv1a(str: string, seed: number): number {
    let h = seed;
    for (let i = 0; i < str.length; i++) {
      h ^= str.charCodeAt(i);
      h = Math.imul(h, 0x01000193);
    }
    return h >>> 0;
  }

  return function isWord(word: string): boolean {
    const w = word.toLowerCase();
    if (w.length === 0) return false;
    for (let i = 0; i < w.length; i++) {
      const c = w.charCodeAt(i);
      if (c < 97 || c > 122) return false;
    }

    const h1 = fnv1a(w, SEED1);
    const h2 = fnv1a(w, SEED2);

    for (let i = 0; i < meta.numHashes; i++) {
      const bit = ((h1 + Math.imul(i, h2)) >>> 0) % meta.numBits;
      if ((filter[bit >>> 3] & (1 << (bit & 7))) === 0) return false;
    }
    return true;
  };
})();

// ═══════════════════════════════════════════════════════════════════════════
// OPT 2 — Inline constants (no meta object property lookups)
// ═══════════════════════════════════════════════════════════════════════════

const opt2_inlineConsts = (() => {
  const SEED1 = 0x811c9dc5;
  const SEED2 = 0xc6a4a793;
  const filter = filterBuf;
  const NUM_HASHES = meta.numHashes;
  const NUM_BITS = meta.numBits;

  function fnv1a(str: string, seed: number): number {
    let h = seed;
    for (let i = 0; i < str.length; i++) {
      h ^= str.charCodeAt(i);
      h = Math.imul(h, 0x01000193);
    }
    return h >>> 0;
  }

  return function isWord(word: string): boolean {
    const w = word.toLowerCase();
    if (w.length === 0 || !/^[a-z]+$/.test(w)) return false;

    const h1 = fnv1a(w, SEED1);
    const h2 = fnv1a(w, SEED2);

    for (let i = 0; i < NUM_HASHES; i++) {
      const bit = ((h1 + Math.imul(i, h2)) >>> 0) % NUM_BITS;
      if ((filter[bit >>> 3] & (1 << (bit & 7))) === 0) return false;
    }
    return true;
  };
})();

// ═══════════════════════════════════════════════════════════════════════════
// OPT 3 — Uint32Array instead of Uint8Array (fewer shifts per probe)
// ═══════════════════════════════════════════════════════════════════════════

const opt3_uint32 = (() => {
  const SEED1 = 0x811c9dc5;
  const SEED2 = 0xc6a4a793;

  // Reinterpret the Uint8Array as Uint32Array (pad to multiple of 4)
  const padded = Math.ceil(filterBuf.length / 4) * 4;
  const aligned = new ArrayBuffer(padded);
  new Uint8Array(aligned).set(filterBuf);
  const filter32 = new Uint32Array(aligned);

  function fnv1a(str: string, seed: number): number {
    let h = seed;
    for (let i = 0; i < str.length; i++) {
      h ^= str.charCodeAt(i);
      h = Math.imul(h, 0x01000193);
    }
    return h >>> 0;
  }

  return function isWord(word: string): boolean {
    const w = word.toLowerCase();
    if (w.length === 0 || !/^[a-z]+$/.test(w)) return false;

    const h1 = fnv1a(w, SEED1);
    const h2 = fnv1a(w, SEED2);

    for (let i = 0; i < meta.numHashes; i++) {
      const bit = ((h1 + Math.imul(i, h2)) >>> 0) % meta.numBits;
      if ((filter32[bit >>> 5] & (1 << (bit & 31))) === 0) return false;
    }
    return true;
  };
})();

// ═══════════════════════════════════════════════════════════════════════════
// OPT 4 — Fuse toLowerCase + validation + hash in a single pass
// ═══════════════════════════════════════════════════════════════════════════

const opt4_fusedHash = (() => {
  const SEED1 = 0x811c9dc5;
  const SEED2 = 0xc6a4a793;
  const PRIME = 0x01000193;
  const filter = filterBuf;

  return function isWord(word: string): boolean {
    const len = word.length;
    if (len === 0) return false;

    // Single pass: validate, lowercase, and hash simultaneously
    let h1 = SEED1;
    let h2 = SEED2;
    for (let i = 0; i < len; i++) {
      let c = word.charCodeAt(i);
      // uppercase A-Z → lowercase
      if (c >= 65 && c <= 90) c = c | 32;
      // reject non a-z
      if (c < 97 || c > 122) return false;
      h1 = Math.imul(h1 ^ c, PRIME);
      h2 = Math.imul(h2 ^ c, PRIME);
    }
    h1 = h1 >>> 0;
    h2 = h2 >>> 0;

    for (let i = 0; i < meta.numHashes; i++) {
      const bit = ((h1 + Math.imul(i, h2)) >>> 0) % meta.numBits;
      if ((filter[bit >>> 3] & (1 << (bit & 7))) === 0) return false;
    }
    return true;
  };
})();

// ═══════════════════════════════════════════════════════════════════════════
// OPT 5 — Unrolled probes (no loop for 10 hashes)
// ═══════════════════════════════════════════════════════════════════════════

const opt5_unrolled = (() => {
  const SEED1 = 0x811c9dc5;
  const SEED2 = 0xc6a4a793;
  const filter = filterBuf;
  const NB = meta.numBits;

  function fnv1a(str: string, seed: number): number {
    let h = seed;
    for (let i = 0; i < str.length; i++) {
      h ^= str.charCodeAt(i);
      h = Math.imul(h, 0x01000193);
    }
    return h >>> 0;
  }

  // Hardcoded for k=10
  return function isWord(word: string): boolean {
    const w = word.toLowerCase();
    if (w.length === 0 || !/^[a-z]+$/.test(w)) return false;

    const h1 = fnv1a(w, SEED1);
    const h2 = fnv1a(w, SEED2);
    let bit: number;

    bit = (h1 >>> 0) % NB;
    if ((filter[bit >>> 3] & (1 << (bit & 7))) === 0) return false;
    bit = ((h1 + h2) >>> 0) % NB;
    if ((filter[bit >>> 3] & (1 << (bit & 7))) === 0) return false;
    bit = ((h1 + Math.imul(2, h2)) >>> 0) % NB;
    if ((filter[bit >>> 3] & (1 << (bit & 7))) === 0) return false;
    bit = ((h1 + Math.imul(3, h2)) >>> 0) % NB;
    if ((filter[bit >>> 3] & (1 << (bit & 7))) === 0) return false;
    bit = ((h1 + Math.imul(4, h2)) >>> 0) % NB;
    if ((filter[bit >>> 3] & (1 << (bit & 7))) === 0) return false;
    bit = ((h1 + Math.imul(5, h2)) >>> 0) % NB;
    if ((filter[bit >>> 3] & (1 << (bit & 7))) === 0) return false;
    bit = ((h1 + Math.imul(6, h2)) >>> 0) % NB;
    if ((filter[bit >>> 3] & (1 << (bit & 7))) === 0) return false;
    bit = ((h1 + Math.imul(7, h2)) >>> 0) % NB;
    if ((filter[bit >>> 3] & (1 << (bit & 7))) === 0) return false;
    bit = ((h1 + Math.imul(8, h2)) >>> 0) % NB;
    if ((filter[bit >>> 3] & (1 << (bit & 7))) === 0) return false;
    bit = ((h1 + Math.imul(9, h2)) >>> 0) % NB;
    if ((filter[bit >>> 3] & (1 << (bit & 7))) === 0) return false;

    return true;
  };
})();

// ═══════════════════════════════════════════════════════════════════════════
// OPT 6 — Power-of-2 filter size (bitwise AND instead of modulo)
// ═══════════════════════════════════════════════════════════════════════════
// NOTE: This requires a differently-sized filter. We simulate by using
// the next power of 2 from our current numBits. Some probes will hit
// unused bits (always 0) increasing FP rate, but this benchmarks the
// speed gain from avoiding modulo.

const opt6_powerOf2 = (() => {
  const SEED1 = 0x811c9dc5;
  const SEED2 = 0xc6a4a793;
  const filter = filterBuf;

  // Next power of 2 >= numBits
  let po2 = 1;
  while (po2 < meta.numBits) po2 <<= 1;
  // If po2 exceeds filter length in bits, clamp to filter's actual bit range
  const MASK = Math.min(po2, filterBuf.length * 8) - 1;

  function fnv1a(str: string, seed: number): number {
    let h = seed;
    for (let i = 0; i < str.length; i++) {
      h ^= str.charCodeAt(i);
      h = Math.imul(h, 0x01000193);
    }
    return h >>> 0;
  }

  return function isWord(word: string): boolean {
    const w = word.toLowerCase();
    if (w.length === 0 || !/^[a-z]+$/.test(w)) return false;

    const h1 = fnv1a(w, SEED1);
    const h2 = fnv1a(w, SEED2);

    for (let i = 0; i < meta.numHashes; i++) {
      const bit = ((h1 + Math.imul(i, h2)) >>> 0) & MASK;
      if ((filter[bit >>> 3] & (1 << (bit & 7))) === 0) return false;
    }
    return true;
  };
})();

// ═══════════════════════════════════════════════════════════════════════════
// COMBINED — All optimizations together
// ═══════════════════════════════════════════════════════════════════════════

const combined = (() => {
  const SEED1 = 0x811c9dc5;
  const SEED2 = 0xc6a4a793;
  const PRIME = 0x01000193;

  const padded2 = Math.ceil(filterBuf.length / 4) * 4;
  const aligned = new ArrayBuffer(padded2);
  new Uint8Array(aligned).set(filterBuf);
  const filter32 = new Uint32Array(aligned);

  const NUM_HASHES = meta.numHashes;
  const NUM_BITS = meta.numBits;

  return function isWord(word: string): boolean {
    const len = word.length;
    if (len === 0) return false;

    // Fused: validate + lowercase + dual hash in one pass
    let h1 = SEED1;
    let h2 = SEED2;
    for (let i = 0; i < len; i++) {
      let c = word.charCodeAt(i);
      if (c >= 65 && c <= 90) c = c | 32;
      if (c < 97 || c > 122) return false;
      h1 = Math.imul(h1 ^ c, PRIME);
      h2 = Math.imul(h2 ^ c, PRIME);
    }
    h1 = h1 >>> 0;
    h2 = h2 >>> 0;

    // Uint32Array probes with inlined constants
    for (let i = 0; i < NUM_HASHES; i++) {
      const bit = ((h1 + Math.imul(i, h2)) >>> 0) % NUM_BITS;
      if ((filter32[bit >>> 5] & (1 << (bit & 31))) === 0) return false;
    }
    return true;
  };
})();

// ═══════════════════════════════════════════════════════════════════════════
// NATIVE SET BASELINE — for comparison: how fast is a native JS Set?
// ═══════════════════════════════════════════════════════════════════════════

const nativeSet = (() => {
  const raw = readFileSync("/usr/share/dict/words", "utf-8");
  const wordSet = new Set(
    raw.split(/\r?\n/).map(w => w.trim().toLowerCase()).filter(w => w.length > 0 && /^[a-z]+$/.test(w))
  );
  return function isWord(word: string): boolean {
    return wordSet.has(word.toLowerCase());
  };
})();

// ═══════════════════════════════════════════════════════════════════════════
// BENCHMARK HARNESS
// ═══════════════════════════════════════════════════════════════════════════

function bench(label: string, fn: () => void, iterations: number): { label: string; opsPerSec: number; nsPerOp: number } {
  // Warmup
  for (let i = 0; i < 10_000; i++) fn();

  const start = performance.now();
  for (let i = 0; i < iterations; i++) fn();
  const elapsed = performance.now() - start;

  const opsPerSec = Math.round((iterations / elapsed) * 1000);
  const nsPerOp = Math.round((elapsed / iterations) * 1e6);
  return { label, opsPerSec, nsPerOp };
}

// ── Correctness check ───────────────────────────────────────────────────────
const CHECK_WORDS = ["hello", "world", "algorithm", "the", "cat"];
const CHECK_NON   = ["xjqkv", "blorft", "asdfgh"];

const variants: [string, (w: string) => boolean][] = [
  ["Baseline (current)",       baseline],
  ["Opt1: No regex",           opt1_noRegex],
  ["Opt2: Inline constants",   opt2_inlineConsts],
  ["Opt3: Uint32Array",        opt3_uint32],
  ["Opt4: Fused hash",         opt4_fusedHash],
  ["Opt5: Unrolled probes",    opt5_unrolled],
  ["Opt6: Power-of-2 mask",   opt6_powerOf2],
  ["ALL COMBINED",             combined],
  ["Native Set (reference)",   nativeSet],
];

console.log("Correctness check:");
for (const [name, fn] of variants) {
  const ok = CHECK_WORDS.every(w => fn(w)) && CHECK_NON.every(w => !fn(w));
  console.log(`  ${ok ? "✓" : "✗"} ${name}`);
}

console.log("\n" + "═".repeat(80));
console.log("BENCHMARK: known word (\"algorithm\")");
console.log("═".repeat(80));

const ITERS = 2_000_000;

const knownResults: { label: string; opsPerSec: number; nsPerOp: number }[] = [];
for (const [name, fn] of variants) {
  const r = bench(name, () => fn("algorithm"), ITERS);
  knownResults.push(r);
}

const baselineKnown = knownResults[0].nsPerOp;
console.log("");
console.log(`${"Variant".padEnd(30)} ${"ops/s".padStart(14)} ${"ns/op".padStart(8)} ${"vs base".padStart(10)}`);
console.log("─".repeat(66));
for (const r of knownResults) {
  const delta = baselineKnown > 0 ? `${r.nsPerOp < baselineKnown ? "-" : "+"}${Math.abs(Math.round((1 - r.nsPerOp / baselineKnown) * 100))}%` : "";
  console.log(`${r.label.padEnd(30)} ${r.opsPerSec.toLocaleString().padStart(14)} ${String(r.nsPerOp).padStart(8)} ${delta.padStart(10)}`);
}

console.log("\n" + "═".repeat(80));
console.log("BENCHMARK: non-word (\"xjqkv\")");
console.log("═".repeat(80));

const nonResults: { label: string; opsPerSec: number; nsPerOp: number }[] = [];
for (const [name, fn] of variants) {
  const r = bench(name, () => fn("xjqkv"), ITERS);
  nonResults.push(r);
}

const baselineNon = nonResults[0].nsPerOp;
console.log("");
console.log(`${"Variant".padEnd(30)} ${"ops/s".padStart(14)} ${"ns/op".padStart(8)} ${"vs base".padStart(10)}`);
console.log("─".repeat(66));
for (const r of nonResults) {
  const delta = baselineNon > 0 ? `${r.nsPerOp < baselineNon ? "-" : "+"}${Math.abs(Math.round((1 - r.nsPerOp / baselineNon) * 100))}%` : "";
  console.log(`${r.label.padEnd(30)} ${r.opsPerSec.toLocaleString().padStart(14)} ${String(r.nsPerOp).padStart(8)} ${delta.padStart(10)}`);
}

console.log("\n" + "═".repeat(80));
console.log("BENCHMARK: mixed (10 known + 10 non-words)");
console.log("═".repeat(80));

const MIXED_WORDS = [...CHECK_WORDS, "elephant", "mountain", "banana", "computer", "dog"];
const MIXED_NON = ["xjqkv", "blorft", "asdfgh", "qqqqq", "zzzzz", "plmkj", "fnordx", "abcxyz", "wvwvw", "qpqpq"];
const MIXED = [...MIXED_WORDS, ...MIXED_NON];

const mixedResults: { label: string; opsPerSec: number; nsPerOp: number }[] = [];
for (const [name, fn] of variants) {
  const r = bench(name, () => { for (const w of MIXED) fn(w); }, ITERS / 20);
  mixedResults.push(r);
}

const baselineMixed = mixedResults[0].nsPerOp;
console.log("");
console.log(`${"Variant".padEnd(30)} ${"ops/s".padStart(14)} ${"ns/op".padStart(8)} ${"vs base".padStart(10)}`);
console.log("─".repeat(66));
for (const r of mixedResults) {
  const delta = baselineMixed > 0 ? `${r.nsPerOp < baselineMixed ? "-" : "+"}${Math.abs(Math.round((1 - r.nsPerOp / baselineMixed) * 100))}%` : "";
  console.log(`${r.label.padEnd(30)} ${r.opsPerSec.toLocaleString().padStart(14)} ${String(r.nsPerOp).padStart(8)} ${delta.padStart(10)}`);
}

console.log("\nDone.");
