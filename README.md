# is-english-word

Blazingly fast English word lookup. **~42M ops/s**, **270 KB** on npm, zero runtime dependencies.

Uses an [xor filter](https://arxiv.org/abs/1912.08258) — a space-efficient probabilistic data structure that's smaller and faster than bloom filters. The entire 234k-word dictionary compresses into a 282 KB binary with only **3 array accesses** per lookup.

## Install

```bash
npm install is-english-word
```

## Usage

```js
import { isWord } from "is-english-word";

isWord("hello");     // true
isWord("world");     // true
isWord("asdfgh");    // false
isWord("Hello");     // true  (case-insensitive)
isWord("it's");      // false (alpha-only)
```

## Performance

| Benchmark | ops/s | ns/op |
|-----------|------:|------:|
| Known word (`"algorithm"`) | 42,000,000 | 24 |
| Non-word (`"xjqkv"`) | 76,000,000 | 13 |
| Short word (`"a"`) | 140,000,000 | 7 |
| Long word (`"extraordinary"`) | 30,000,000 | 34 |

```bash
npm run bench
```

## How it works

An **xor filter** stores 8-bit fingerprints in a compact array. For each query, 3 positions are computed and the XOR of those 3 entries is compared against the word's fingerprint.

- **Zero false negatives** — if a word is in the dictionary, `isWord` always returns `true`
- **False positive rate ≈ 0.39%** (xor8) — ~1 in 256 non-words may return `true`
- **O(1) lookup** — exactly 3 array accesses, independent of dictionary size
- **282 KB** — vs ~2.5 MB for a raw word list, or ~36 MB for a `Set`

## API

### `isWord(word: string): boolean`

Returns `true` if `word` is a recognized English word.

- Case-insensitive (lowercased internally)
- Returns `false` for empty strings, numbers, hyphens, apostrophes, spaces
- Only ASCII a–z characters are supported

## Configuration

The filter is pre-built with **xor8** by default (smallest size). You can rebuild with different options:

### Fingerprint size

| Mode | FP rate | Filter size | Package size |
|------|---------|------------|-------------|
| `xor8` (default) | ≈ 0.39% | 282 KB | 270 KB |
| `xor16` | ≈ 0.0015% | 563 KB | 534 KB |

```bash
# Rebuild with 16-bit fingerprints (higher accuracy, 2x size)
npm run build:filter:xor16
npm run build
```

### Custom word list

```bash
# Use any newline-separated word list
node scripts/build-filter.mjs --words=./my-words.txt

# Combine options
node scripts/build-filter.mjs --bits=16 --words=./my-words.txt

npm run build
```

## Comparison

| Package | Approach | Size | Lookup |
|---------|----------|------|--------|
| **is-english-word** | Xor filter | **270 KB** | **24 ns** |
| `an-array-of-english-words` | JSON array | 3.4 MB | ~ms (linear scan) |
| `word-list` | Text file | 2.8 MB | user builds own |
| `check-if-word` | Giant regex | 39.6 MB | slow |

## License

MIT
