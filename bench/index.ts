import { isWord } from "../src/index";

const KNOWN_WORDS = [
  "hello", "world", "algorithm", "javascript", "function",
  "elephant", "mountain", "computer", "beautiful", "extraordinary",
];
const NON_WORDS = [
  "asdfgh", "qwerty", "xjqkv", "blorft", "zxcvbn",
  "fnordx", "abcxyz", "qqqqq", "zzzzz", "plmkj",
];
const MIXED = [...KNOWN_WORDS, ...NON_WORDS];

function bench(label: string, fn: () => void, iterations: number) {
  // Warmup
  for (let i = 0; i < 1000; i++) fn();

  const start = performance.now();
  for (let i = 0; i < iterations; i++) fn();
  const elapsed = performance.now() - start;

  const opsPerSec = ((iterations / elapsed) * 1000).toFixed(0);
  const nsPerOp = ((elapsed / iterations) * 1e6).toFixed(0);
  console.log(`${label.padEnd(30)} ${opsPerSec.padStart(12)} ops/s  ${nsPerOp.padStart(6)} ns/op`);
}

console.log("Benchmark: fast-is-english-word\n");

const ITERS = 1_000_000;

bench("isWord (known word)", () => isWord("algorithm"), ITERS);
bench("isWord (non-word)", () => isWord("xjqkv"), ITERS);
bench("isWord (mixed, 20 words)", () => {
  for (const w of MIXED) isWord(w);
}, ITERS / 20);
bench("isWord (short word)", () => isWord("a"), ITERS);
bench("isWord (long word)", () => isWord("extraordinary"), ITERS);

console.log("\nDone.");
