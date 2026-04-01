import { readFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

// ── Resolve data directory ──────────────────────────────────────────────────
let _dir: string;
try {
  _dir = dirname(fileURLToPath(import.meta.url));
} catch {
  _dir = __dirname;
}
const dataDir = resolve(_dir, "..", "data");

// ── Load xor filter once at import ──────────────────────────────────────────
const meta: {
  type: string;
  fpBits: number;
  seed: number;
  segmentLength: number;
  arrayLength: number;
} = JSON.parse(readFileSync(resolve(dataDir, "meta.json"), "utf-8"));

const SEED = meta.seed;
const SEG = meta.segmentLength;
const FP_MASK = meta.fpBits === 8 ? 0xff : 0xffff;

const rawBuf = readFileSync(resolve(dataDir, "filter.bin"));
const B: Uint8Array | Uint16Array =
  meta.fpBits === 8
    ? new Uint8Array(rawBuf.buffer, rawBuf.byteOffset, rawBuf.byteLength)
    : new Uint16Array(
        rawBuf.buffer.slice(rawBuf.byteOffset, rawBuf.byteOffset + rawBuf.byteLength)
      );

// ── Hash helpers ────────────────────────────────────────────────────────────
const FNV_SEED1 = 0x811c9dc5;
const FNV_SEED2 = 0xc6a4a793;
const FNV_PRIME = 0x01000193;

function mix32(x: number): number {
  x = Math.imul(x ^ (x >>> 16), 0x85ebca6b);
  x = Math.imul(x ^ (x >>> 13), 0xc2b2ae35);
  return (x ^ (x >>> 16)) >>> 0;
}

// ── Lookup ──────────────────────────────────────────────────────────────────

/**
 * Returns `true` if `word` is a recognized English word.
 *
 * - Case-insensitive (internally lowercased)
 * - O(1) lookup via xor filter — exactly 3 array accesses
 * - Zero false negatives
 * - False positive rate ≈ 0.39% (xor8) or ≈ 0.0015% (xor16)
 */
export function isWord(word: string): boolean {
  const len = word.length;
  if (len === 0) return false;

  // Single pass: validate, lowercase, and dual-hash
  let ha = FNV_SEED1;
  let hb = FNV_SEED2;
  for (let i = 0; i < len; i++) {
    let c = word.charCodeAt(i);
    if (c >= 65 && c <= 90) c = c | 32;
    if (c < 97 || c > 122) return false;
    ha = Math.imul(ha ^ c, FNV_PRIME);
    hb = Math.imul(hb ^ c, FNV_PRIME);
  }
  ha = ha >>> 0;
  hb = hb >>> 0;

  // Derive 3 positions + fingerprint via splitmix32
  const r0 = mix32((ha ^ SEED) >>> 0);
  const r1 = mix32((hb ^ SEED) >>> 0);
  const r2 = mix32(((ha ^ hb) ^ SEED) >>> 0);

  const h0 = r0 % SEG;
  const h1 = SEG + (r1 % SEG);
  const h2 = 2 * SEG + (r2 % SEG);
  const fp = (r0 ^ r1 ^ r2) & FP_MASK;

  return fp === ((B[h0] ^ B[h1] ^ B[h2]) & FP_MASK);
}
