import { describe, it, expect } from "vitest";
import { isWord } from "../src/index";

describe("isWord", () => {
  it("recognizes common English words", () => {
    const words = [
      "hello", "world", "the", "a", "is", "cat", "dog",
      "computer", "algorithm", "function",
      "apple", "banana", "orange", "elephant", "mountain",
    ];
    for (const w of words) {
      expect(isWord(w)).toBe(true);
    }
  });

  it("is case-insensitive", () => {
    expect(isWord("Hello")).toBe(true);
    expect(isWord("WORLD")).toBe(true);
    expect(isWord("Algorithm")).toBe(true);
  });

  it("rejects non-words", () => {
    const nonWords = [
      "asdfgh", "qwerty", "zzzzz", "xjqkv", "blorft",
      "fnord", "zxcvbn",
    ];
    let falsePositives = 0;
    for (const w of nonWords) {
      if (isWord(w)) falsePositives++;
    }
    // Allow at most 1 false positive from this small set
    expect(falsePositives).toBeLessThanOrEqual(1);
  });

  it("rejects empty strings and non-alpha input", () => {
    expect(isWord("")).toBe(false);
    expect(isWord(" ")).toBe(false);
    expect(isWord("123")).toBe(false);
    expect(isWord("hello world")).toBe(false);
    expect(isWord("it's")).toBe(false);
    expect(isWord("well-known")).toBe(false);
  });

  it("handles single-letter words", () => {
    expect(isWord("a")).toBe(true);
    expect(isWord("i")).toBe(true);
  });
});
