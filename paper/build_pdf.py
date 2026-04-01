"""
Academic paper: fast-is-english-word
IEEE single-column style with data-driven charts.
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    KeepTogether, HRFlowable
)

BASE = os.path.dirname(__file__)
FIG_DIR = os.path.join(BASE, 'figures')
OUT = os.path.join(BASE, 'fast_is_english_word.pdf')

# ── Styles ──
styles = getSampleStyleSheet()

title_style = ParagraphStyle('Title', parent=styles['Title'],
    fontName='Times-Bold', fontSize=15, leading=18, alignment=TA_CENTER,
    spaceAfter=6, textColor=black)

author_style = ParagraphStyle('Author', parent=styles['Normal'],
    fontName='Times-Roman', fontSize=11, alignment=TA_CENTER,
    spaceAfter=2, textColor=HexColor('#333333'))

affil_style = ParagraphStyle('Affil', parent=styles['Normal'],
    fontName='Times-Italic', fontSize=9, alignment=TA_CENTER,
    spaceAfter=12, textColor=HexColor('#555555'))

abstract_title = ParagraphStyle('AbsTitle', parent=styles['Normal'],
    fontName='Times-Bold', fontSize=10, alignment=TA_CENTER, spaceAfter=4)

abstract_style = ParagraphStyle('Abstract', parent=styles['Normal'],
    fontName='Times-Italic', fontSize=9, leading=12, alignment=TA_JUSTIFY,
    leftIndent=30, rightIndent=30, spaceAfter=12)

h1 = ParagraphStyle('H1', parent=styles['Heading1'],
    fontName='Helvetica-Bold', fontSize=11, leading=14,
    spaceBefore=14, spaceAfter=6, textColor=black)

h2 = ParagraphStyle('H2', parent=styles['Heading2'],
    fontName='Helvetica-Bold', fontSize=9.5, leading=12,
    spaceBefore=10, spaceAfter=4, textColor=black)

body = ParagraphStyle('Body', parent=styles['Normal'],
    fontName='Times-Roman', fontSize=9.5, leading=12.5, alignment=TA_JUSTIFY,
    spaceAfter=4)

caption = ParagraphStyle('Caption', parent=styles['Normal'],
    fontName='Times-Italic', fontSize=8, leading=10, alignment=TA_CENTER,
    spaceAfter=8, spaceBefore=2)

ref_style = ParagraphStyle('Ref', parent=styles['Normal'],
    fontName='Times-Roman', fontSize=8, leading=10,
    leftIndent=20, firstLineIndent=-20, spaceAfter=2)

table_header_style = ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, leading=10, alignment=TA_LEFT)
table_cell_style = ParagraphStyle('TC', fontName='Times-Roman', fontSize=8, leading=10, alignment=TA_LEFT)

def P(text, style=body):
    return Paragraph(text, style)

def H1(text):
    return Paragraph(text, h1)

def H2(text):
    return Paragraph(text, h2)

def Fig(filename, w=5.2, cap=''):
    path = os.path.join(FIG_DIR, filename)
    elems = []
    if os.path.exists(path):
        elems.append(Image(path, width=w*inch, height=w*0.48*inch))
    elems.append(P(cap, caption))
    return KeepTogether(elems)

def make_table(headers, rows, col_widths=None):
    data = [[P(h, table_header_style) for h in headers]]
    for row in rows:
        data.append([P(str(c), table_cell_style) for c in row])
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), HexColor('#e8e8f0')),
        ('TEXTCOLOR', (0,0), (-1,0), black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,0), 0.5, HexColor('#999999')),
        ('LINEBELOW', (0,0), (-1,0), 1, black),
        ('LINEBELOW', (0,-1), (-1,-1), 0.5, HexColor('#999999')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [HexColor('#ffffff'), HexColor('#f5f5fa')]),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    return t

# ── Build document ──
doc = SimpleDocTemplate(OUT, pagesize=letter,
    topMargin=0.75*inch, bottomMargin=0.75*inch,
    leftMargin=0.85*inch, rightMargin=0.85*inch)

story = []

# ══════════════════════════════════════════════════════════════════
# TITLE BLOCK
# ══════════════════════════════════════════════════════════════════
story.append(P('Sub-30 Nanosecond Dictionary Lookup in JavaScript:<br/>'
               'Xor Filters for Compact English Word Recognition', title_style))
story.append(Spacer(1, 4))
story.append(P('Arnav Gupta', author_style))
story.append(P('Independent Research | ar9avg@gmail.com', affil_style))
story.append(Spacer(1, 6))
story.append(HRFlowable(width='60%', thickness=0.5, color=HexColor('#cccccc')))
story.append(Spacer(1, 8))

# ══════════════════════════════════════════════════════════════════
# ABSTRACT
# ══════════════════════════════════════════════════════════════════
story.append(P('<b>Abstract</b>', abstract_title))
story.append(P(
    'We present <i>fast-is-english-word</i>, an npm package for English word recognition that achieves '
    '24 nanosecond lookups in a 271 KB package with zero runtime dependencies. The core insight is applying '
    'xor filters\u2014a modern probabilistic data structure\u2014to the dictionary membership problem in '
    'JavaScript. Starting from a standard bloom filter baseline (42 ns/op, 412 KB), we apply six targeted '
    'optimizations: fused single-pass hashing, regex elimination, constant inlining, Uint32Array bit access, '
    'loop unrolling, and power-of-2 masking. We then replace the bloom filter entirely with an xor8 filter, '
    'reducing the data structure from 412 KB to 282 KB (31% reduction) while cutting memory accesses from '
    '10 to 3 per query. The combined approach yields a 4.7\u00d7 throughput improvement over the baseline on '
    'mixed workloads. We benchmark against existing npm alternatives (an-array-of-english-words, word-list, '
    'check-if-word) and demonstrate 100\u00d7 smaller package size than check-if-word (271 KB vs 39.6 MB) '
    'with sub-microsecond latency. The package supports configurable fingerprint widths (8-bit or 16-bit) '
    'and custom word lists.', abstract_style))

story.append(P('<b>Keywords:</b> xor filters, probabilistic data structures, bloom filters, '
               'dictionary lookup, JavaScript, npm, performance optimization', ParagraphStyle('KW', parent=body,
               fontName='Times-Roman', fontSize=8, alignment=TA_CENTER, spaceAfter=12)))

story.append(HRFlowable(width='100%', thickness=0.5, color=HexColor('#cccccc')))
story.append(Spacer(1, 8))

# ══════════════════════════════════════════════════════════════════
# 1. INTRODUCTION
# ══════════════════════════════════════════════════════════════════
story.append(H1('1. Introduction'))
story.append(P(
    'Checking whether a string is a valid English word is a common operation in spell checkers, word games, '
    'natural language processing pipelines, and input validation. In the JavaScript ecosystem, existing solutions '
    'fall into two categories: (a) ship the entire word list as JSON or text (2\u20134 MB), requiring the consumer '
    'to build their own lookup structure, or (b) use heavyweight approaches like giant regular expressions '
    '(39.6 MB for check-if-word). Neither approach is satisfactory for performance-sensitive or '
    'size-constrained applications.'))

story.append(P(
    'We observe that English word recognition is a <i>static set membership</i> problem\u2014the dictionary '
    'does not change at runtime. This makes it an ideal candidate for probabilistic filters optimized for '
    'immutable sets. While bloom filters [1] are the classical choice, recent work on xor filters [2] and '
    'binary fuse filters [3] has produced data structures that are both smaller and faster.'))

story.append(P('We contribute:'))
story.append(P('<b>1.</b> A systematic evaluation of six micro-optimizations for bloom filter lookups in V8 '
               'JavaScript, with isolated benchmarks showing individual and combined impact.'))
story.append(P('<b>2.</b> A practical implementation of xor8 filters for dictionary membership in JavaScript, '
               'achieving 3 memory accesses per query with 9.84 bits per element.'))
story.append(P('<b>3.</b> An open-source npm package (<i>fast-is-english-word</i>) containing 234,454 words '
               'in 271 KB, with configurable accuracy/size tradeoffs.'))

# ══════════════════════════════════════════════════════════════════
# 2. RELATED WORK
# ══════════════════════════════════════════════════════════════════
story.append(H1('2. Related Work'))

story.append(P(
    '<b>Existing npm packages.</b> The most downloaded packages for English word lookup ship raw word lists '
    'without optimized lookup structures. <i>an-array-of-english-words</i> (~7k weekly downloads) exports '
    'a 3.4 MB JSON array requiring O(n) linear scan or manual Set construction (~36 MB heap). <i>word-list</i> '
    '(~12k downloads) exports a file path, requiring filesystem I/O and string splitting. <i>check-if-word</i> '
    'compiles a giant RegExp alternation of all words (39.6 MB), which is pathologically slow in most regex engines.'))

story.append(Spacer(1, 4))
story.append(Fig('fig1_package_size.png', 5.5,
    '<b>Figure 1:</b> Package size comparison of npm word-checking packages (log scale). '
    'fast-is-english-word is 12\u00d7 smaller than the next smallest alternative.'))

story.append(P(
    '<b>Bloom filters</b> [1] are the classical probabilistic membership test. For a false positive rate '
    '<i>p</i> with <i>n</i> elements, they require \u2212n\u00b7ln(p) / (ln 2)\u00b2 bits, with '
    'k = \u2212log\u2082(p) hash probes per query. At 0.1% FP rate, this is 14.4 bits/element and 10 probes. '
    'The <i>bloomfilter.js</i> library [4] uses FNV-1a hashing with the Kirsch-Mitzenmacker double hashing '
    'optimization [5].'))

story.append(P(
    '<b>Xor filters</b> [2] achieve approximately 1.23 \u00d7 8 = 9.84 bits/element with 8-bit fingerprints, '
    'requiring exactly 3 memory accesses per query regardless of the false positive rate. Graf and Lemire [2] '
    'showed that xor filters are both smaller and faster than bloom filters, with 3.5 cache misses vs 7.5 for '
    'bloom. <b>Binary fuse filters</b> [3] further reduce the space to ~1.125n entries, approximately 9 '
    'bits/element.'))

story.append(P(
    '<b>Other structures.</b> DAWGs (Directed Acyclic Word Graphs) [6] share common suffixes for '
    'zero-false-positive lookup but typically require 400\u2013500 KB for 234k words. Succinct tries [7] '
    'encode trie topology in ~2 bits per node. These provide exact answers but are larger than xor filters '
    'for equivalent dictionaries.'))

# ══════════════════════════════════════════════════════════════════
# 3. METHODOLOGY
# ══════════════════════════════════════════════════════════════════
story.append(H1('3. Methodology'))
story.append(H2('3.1 Baseline: Bloom Filter'))
story.append(P(
    'Our initial implementation uses a standard bloom filter with the following parameters: 234,454 words '
    'from <i>/usr/share/dict/words</i> (filtered to lowercase alphabetic entries), false positive rate '
    'target of 0.1%, yielding a 421,361-byte filter with k=10 hash functions. The hash function is FNV-1a '
    '[8] with the Kirsch-Mitzenmacker double hashing optimization: h<sub>i</sub>(x) = h<sub>1</sub>(x) + '
    'i \u00b7 h<sub>2</sub>(x), where h<sub>1</sub> and h<sub>2</sub> are FNV-1a with different seeds.'))

story.append(H2('3.2 Optimization Pass'))
story.append(P(
    'We evaluated six optimizations in isolation against the baseline, measuring each on three workloads: '
    'known words, non-words, and a mixed batch of 20 lookups. All benchmarks ran 2M iterations after a '
    '10k-iteration warmup on Node.js v24 (V8 TurboFan JIT).'))

story.append(make_table(
    ['Optimization', 'Description', 'Rationale'],
    [['No regex', 'Replace /^[a-z]+$/.test() with charCode loop', 'Regex engine overhead per call'],
     ['Inline constants', 'Extract meta.numHashes to top-level const', 'Eliminate object property lookup in hot loop'],
     ['Uint32Array', 'Reinterpret filter as Uint32Array for bit access', 'Fewer shift operations per probe (>>>5 vs >>>3)'],
     ['Fused hash', 'Combine toLowerCase + validation + dual hash in one pass', 'Eliminate string allocation and extra traversal'],
     ['Unrolled probes', 'Manually unroll k=10 probe loop', 'Remove loop overhead and branch prediction'],
     ['Power-of-2 mask', 'Use bitwise AND instead of modulo', 'Integer division is expensive on hot path']],
    col_widths=[1.1*inch, 2.4*inch, 2.3*inch]))

story.append(Spacer(1, 4))
story.append(Fig('fig4_optimization_breakdown.png', 5.5,
    '<b>Figure 2:</b> Impact of each optimization on the mixed workload (20 lookups per iteration). '
    'Fused hash provides the largest single improvement (\u221278%); combined optimizations yield 4.7\u00d7 speedup.'))

story.append(P(
    'The <b>fused hash</b> optimization provides the largest individual improvement because it eliminates '
    'three operations that the baseline performs sequentially: (1) <i>String.prototype.toLowerCase()</i>, '
    'which allocates a new string on each call; (2) regex validation, which invokes the regex engine; and '
    '(3) a second traversal of the string for the second FNV-1a hash. The fused version performs validation, '
    'lowercasing (via <i>c | 32</i> for A\u2013Z), and both hashes in a single character-by-character pass '
    'with zero allocations.'))

story.append(H2('3.3 Xor8 Filter'))
story.append(P(
    'We replace the bloom filter with an xor8 filter [2]. The construction uses the peeling algorithm on a '
    '3-partite random hypergraph. For n keys, we allocate an array of 3\u00b7\u2308n\u00b71.23/3\u2309 '
    'bytes. Each key maps to three positions (one per segment) via FNV-1a double hashing mixed through '
    'splitmix32, plus an 8-bit fingerprint derived from the mixed hash values. The peeling algorithm '
    'iteratively removes keys that have a singleton position (a position shared by no other key), recording '
    'the removal order. Fingerprints are then assigned in reverse order: B[pos] = fp \u2295 B[h0] \u2295 '
    'B[h1] \u2295 B[h2], guaranteeing that B[h0] \u2295 B[h1] \u2295 B[h2] = fp for all inserted keys.'))

story.append(Spacer(1, 4))
story.append(Fig('fig5_xor_schematic.png', 5.2,
    '<b>Figure 3:</b> Xor filter query. A word is hashed to three segment positions. The XOR of the three '
    'fingerprint entries is compared against the word\u2019s fingerprint. Match \u2192 probably in set; '
    'mismatch \u2192 definitely not.'))

story.append(P(
    'Lookup requires exactly 3 array reads and 2 XOR operations. The false positive rate is 1/2<sup>f</sup> '
    'where f is the fingerprint width in bits: 1/256 \u2248 0.39% for xor8, 1/65536 \u2248 0.0015% for xor16.'))

story.append(Spacer(1, 4))
story.append(Fig('fig2_filter_size.png', 5.5,
    '<b>Figure 4:</b> Left: filter data structure size in KB. Right: bits per element, with the '
    'information-theoretic lower bound at 9.97 bits (dashed red). Xor8 achieves 9.84 bits/element, '
    'near-optimal space efficiency.'))

# ══════════════════════════════════════════════════════════════════
# 4. RESULTS
# ══════════════════════════════════════════════════════════════════
story.append(H1('4. Results'))
story.append(H2('4.1 Lookup Performance'))

story.append(make_table(
    ['Version', 'Known word', 'Non-word', 'Short word', 'Long word', 'Mixed (20)'],
    [['v1: Bloom baseline', '42 ns', '26 ns', '21 ns', '54 ns', '1,837 ns'],
     ['v2: Bloom optimized', '32 ns', '10 ns', '10 ns', '44 ns', '442 ns'],
     ['v3: Xor8 (final)', '24 ns', '13 ns', '7 ns', '34 ns', '387 ns']],
    col_widths=[1.2*inch, 0.9*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1.0*inch]))

story.append(Spacer(1, 4))
story.append(Fig('fig3_speed_progression.png', 5.5,
    '<b>Figure 5:</b> Latency progression across three implementation versions. The Xor8 filter achieves '
    '24 ns for known words (1.75\u00d7 baseline) and 7 ns for short words (3\u00d7 baseline).'))

story.append(P(
    'The final xor8 implementation achieves 42M ops/s for known words and 140M ops/s for short words on '
    'an Apple M-series processor running Node.js v24. Non-word rejection is faster than word recognition '
    'because mismatched fingerprints short-circuit immediately after 3 reads, while valid words must also '
    'complete the full hash computation.'))

story.append(H2('4.2 Package Size'))

story.append(make_table(
    ['Package', 'Approach', 'Packed size', 'Unpacked', 'Lookup'],
    [['check-if-word', 'Giant regex', '39,600 KB', '39,600 KB', 'Regex match'],
     ['an-array-of-english-words', 'JSON array', '3,370 KB', '3,370 KB', 'User builds Set'],
     ['word-list', 'Text file', '2,810 KB', '2,810 KB', 'User reads file'],
     ['wordlist-english', 'JSON object', '1,490 KB', '1,490 KB', 'User builds lookup'],
     ['fast-is-english-word (xor8)', 'Xor filter', '271 KB', '297 KB', '24 ns']],
    col_widths=[1.7*inch, 0.9*inch, 0.9*inch, 0.9*inch, 1.1*inch]))

story.append(H2('4.3 Memory Accesses'))
story.append(Spacer(1, 4))
story.append(Fig('fig6_probes.png', 5.5,
    '<b>Figure 6:</b> Memory accesses per lookup across filter types. Xor and binary fuse filters require '
    'exactly 3, compared to 7\u201310 for bloom filters. Cuckoo filters require 2 but are larger.'))

story.append(H2('4.4 Memory Footprint'))
story.append(Spacer(1, 4))
story.append(Fig('fig7_memory.png', 5.5,
    '<b>Figure 7:</b> Runtime memory usage (log scale). A JavaScript Set for 234k words consumes ~36 MB. '
    'Our xor8 filter uses 282 KB\u2014a 128\u00d7 reduction.'))

story.append(H2('4.5 False Positive Rate'))
story.append(P(
    'Empirical validation over 100,000 random non-word strings confirms the theoretical false positive rates. '
    'For xor8 (8-bit fingerprints), we measured 0.402% (expected: 0.391%). For xor16 (16-bit fingerprints), '
    'we measured 0.001% (expected: 0.0015%). Zero false negatives were observed across all 234,454 dictionary '
    'words in both configurations.'))

# ══════════════════════════════════════════════════════════════════
# 5. DISCUSSION
# ══════════════════════════════════════════════════════════════════
story.append(H1('5. Discussion'))

story.append(P(
    '<b>Fused hashing dominates micro-optimizations.</b> Of the six optimizations evaluated, the fused '
    'single-pass hash accounts for 78% of the speedup on mixed workloads. This is because the baseline '
    'performs three separate operations\u2014toLowerCase(), regex validation, and double FNV-1a\u2014each '
    'requiring a full traversal of the input string. Fusing these into a single pass with inline lowercasing '
    '(bitwise OR with 32) eliminates two string traversals and one string allocation per call.'))

story.append(P(
    '<b>Xor filters are strictly better than bloom for static sets.</b> For immutable dictionaries, xor '
    'filters provide a Pareto improvement: smaller (9.84 vs 14.4 bits/element at comparable FP rates) and '
    'faster (3 vs 10 memory accesses). The only tradeoff is construction time (peeling algorithm, ~200ms '
    'for 234k keys), which is irrelevant for a pre-built package.'))

story.append(P(
    '<b>The npm ecosystem lacks optimized lookup packages.</b> All existing alternatives ship raw word lists '
    'ranging from 1.5 to 39.6 MB. None employ compact data structures. This gap likely exists because bloom '
    'filters and xor filters are well-known in systems programming but underused in the JavaScript ecosystem.'))

story.append(P(
    '<b>Limitations.</b> (1) The package requires Node.js filesystem access for loading the binary filter; '
    'browser support requires a bundler or custom loader. (2) Only ASCII alphabetic words are supported; '
    'hyphenated words, contractions, and Unicode are rejected. (3) The false positive rate of xor8 (0.39%) '
    'may be insufficient for applications requiring exact matching, though xor16 (0.0015%) addresses most '
    'such cases. (4) The dictionary is derived from <i>/usr/share/dict/words</i>, which may not match all '
    'users\u2019 definitions of \u201cEnglish words.\u201d'))

# ══════════════════════════════════════════════════════════════════
# 6. CONCLUSION
# ══════════════════════════════════════════════════════════════════
story.append(H1('6. Conclusion'))

story.append(P(
    'We demonstrate that xor filters, combined with careful JavaScript-specific optimizations, can solve '
    'the dictionary membership problem in 24 nanoseconds with a 271 KB package\u2014orders of magnitude '
    'smaller and faster than existing npm alternatives. The key technical contributions are: (1) showing '
    'that fused single-pass hashing eliminates the dominant bottleneck in JavaScript string processing; '
    '(2) providing the first practical xor filter implementation for dictionary lookup on npm; and '
    '(3) offering configurable accuracy via 8-bit or 16-bit fingerprints.'))

story.append(P(
    '<b>Future work.</b> (1) Binary fuse filters [3] could further reduce size by ~8% (1.125n vs 1.23n '
    'entries). (2) A WASM-compiled hash function (e.g., wyhash) could improve throughput for long words. '
    '(3) Browser-native support via embedding the filter as a Uint8Array literal would eliminate the '
    'filesystem dependency. (4) Supporting compound words, contractions, and Unicode would broaden '
    'applicability.'))

story.append(P(
    'The package is available at <font color="blue">https://www.npmjs.com/package/fast-is-english-word</font> '
    'under the MIT license. Source code: <font color="blue">https://github.com/Ar9av/is-english-word</font>.',
    ParagraphStyle('links', parent=body, fontSize=9, spaceAfter=8)))

# ══════════════════════════════════════════════════════════════════
# REFERENCES
# ══════════════════════════════════════════════════════════════════
story.append(H1('References'))
refs = [
    '[1] B. Bloom, "Space/time trade-offs in hash coding with allowable errors," '
    '<i>Communications of the ACM</i>, vol. 13, no. 7, pp. 422\u2013426, 1970.',

    '[2] T. M. Graf and D. Lemire, "Xor Filters: Faster and Smaller Than Bloom and Cuckoo Filters," '
    '<i>ACM Journal of Experimental Algorithmics</i>, vol. 25, pp. 1\u201316, 2020. '
    'arXiv:1912.08258.',

    '[3] T. M. Graf and D. Lemire, "Binary Fuse Filters: Fast and Smaller Than Xor Filters," '
    '<i>ACM Journal of Experimental Algorithmics</i>, vol. 27, 2022. arXiv:2201.01174.',

    '[4] J. Davies, "bloomfilter.js," GitHub repository, '
    'https://github.com/jasondavies/bloomfilter.js, 2013.',

    '[5] A. Kirsch and M. Mitzenmacker, "Less Hashing, Same Performance: Building a Better Bloom Filter," '
    '<i>Random Structures & Algorithms</i>, vol. 33, no. 2, pp. 187\u2013218, 2008.',

    '[6] J. Daciuk et al., "Incremental construction of minimal acyclic finite-state automata," '
    '<i>Computational Linguistics</i>, vol. 26, no. 1, pp. 3\u201316, 2000.',

    '[7] S. Hanov, "Succinct Data Structures: Cramming 80,000 words into a JavaScript file," '
    'http://stevehanov.ca/blog/?id=120, 2011.',

    '[8] G. Fowler, L. Noll, K. Vo, "FNV Hash," http://www.isthe.com/chongo/tech/comp/fnv/, 1991.',
]
for r in refs:
    story.append(P(r, ref_style))

# ── Build ──
doc.build(story)
print(f"PDF generated: {OUT}")
print(f"Size: {os.path.getsize(OUT)/1024:.0f} KB")
