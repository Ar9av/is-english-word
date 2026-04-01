"""
Generate all figures for the fast-is-english-word paper.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

OUT = os.path.join(os.path.dirname(__file__), 'figures')
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif'],
    'font.size': 8,
    'axes.titlesize': 9,
    'axes.titleweight': 'bold',
    'axes.labelsize': 8,
    'axes.linewidth': 0.6,
    'legend.fontsize': 7,
    'legend.framealpha': 0.95,
    'legend.edgecolor': '#cccccc',
    'xtick.labelsize': 7,
    'ytick.labelsize': 7,
    'figure.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.08,
    'grid.alpha': 0.15,
    'grid.linewidth': 0.5,
    'lines.linewidth': 1.3,
})

BLUE = '#2060cc'
RED = '#cc3030'
GREEN = '#208040'
ORANGE = '#cc7020'
PURPLE = '#8040cc'
GOLD = '#b08020'
GRAY = '#666666'

# ═══════════════════════════════════════════════════════════════════
# Figure 1: Package Size Comparison
# ═══════════════════════════════════════════════════════════════════
def fig1_package_size():
    packages = [
        'check-if-word',
        'an-array-of-\nenglish-words',
        'word-list',
        'wordlist-\nenglish',
        'fast-is-\nenglish-word',
    ]
    sizes_kb = [39600, 3370, 2810, 1490, 271]
    colors = [GRAY, GRAY, GRAY, GRAY, BLUE]

    fig, ax = plt.subplots(figsize=(5.5, 2.5))
    bars = ax.barh(range(len(packages)), sizes_kb, color=colors, alpha=0.85,
                   edgecolor='white', linewidth=0.3)
    ax.set_yticks(range(len(packages)))
    ax.set_yticklabels(packages, fontsize=6.5)
    ax.set_xlabel('Package Size (KB)')
    ax.invert_yaxis()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_xscale('log')

    for bar, val in zip(bars, sizes_kb):
        label = f'{val:,} KB' if val >= 1000 else f'{val} KB'
        ax.text(bar.get_width() * 1.15, bar.get_y() + bar.get_height() / 2,
                label, va='center', fontsize=6, fontweight='bold')

    fig.savefig(os.path.join(OUT, 'fig1_package_size.png'))
    plt.close()
    print('  fig1_package_size.png')


# ═══════════════════════════════════════════════════════════════════
# Figure 2: Filter Size — Bloom vs Xor8 vs Xor16
# ═══════════════════════════════════════════════════════════════════
def fig2_filter_size():
    labels = ['Bloom\n(0.1% FP)', 'Bloom\n(1% FP)', 'Xor8\n(0.39% FP)', 'Xor16\n(0.0015% FP)']
    sizes = [411.5, 275, 281.6, 563.2]
    bits_per_elem = [14.4, 9.6, 9.84, 19.7]
    colors = [GRAY, GRAY, BLUE, ORANGE]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(5.5, 2.3))

    # Left: filter size in KB
    bars = ax1.bar(range(len(labels)), sizes, color=colors, alpha=0.85, edgecolor='white')
    ax1.set_xticks(range(len(labels)))
    ax1.set_xticklabels(labels, fontsize=6)
    ax1.set_ylabel('Filter Size (KB)')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    for bar, val in zip(bars, sizes):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 8,
                 f'{val:.0f}', ha='center', fontsize=6, fontweight='bold')

    # Right: bits per element
    bars2 = ax2.bar(range(len(labels)), bits_per_elem, color=colors, alpha=0.85, edgecolor='white')
    ax2.set_xticks(range(len(labels)))
    ax2.set_xticklabels(labels, fontsize=6)
    ax2.set_ylabel('Bits per Element')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.axhline(y=9.97, color=RED, linewidth=0.8, linestyle='--', alpha=0.7)
    ax2.text(3.4, 10.3, 'Information-\ntheoretic\nlimit', fontsize=5, color=RED, ha='center')
    for bar, val in zip(bars2, bits_per_elem):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                 f'{val:.1f}', ha='center', fontsize=6, fontweight='bold')

    fig.tight_layout()
    fig.savefig(os.path.join(OUT, 'fig2_filter_size.png'))
    plt.close()
    print('  fig2_filter_size.png')


# ═══════════════════════════════════════════════════════════════════
# Figure 3: Lookup Speed — Optimization Progression
# ═══════════════════════════════════════════════════════════════════
def fig3_speed_progression():
    stages = ['v1\nBloom\nbaseline', 'v2\nBloom\noptimized', 'v3\nXor8\nfinal']

    # ns/op for different workloads
    known = [42, 32, 24]
    nonword = [26, 10, 13]
    short = [21, 10, 7]
    mixed_per_word = [94.1, 22.1, 19.35]  # mixed/20

    x = np.arange(len(stages))
    w = 0.2

    fig, ax = plt.subplots(figsize=(5.5, 2.5))
    ax.bar(x - 1.5*w, known, w, color=BLUE, alpha=0.85, label='Known word')
    ax.bar(x - 0.5*w, nonword, w, color=RED, alpha=0.85, label='Non-word')
    ax.bar(x + 0.5*w, short, w, color=GREEN, alpha=0.85, label='Short word')
    ax.bar(x + 1.5*w, mixed_per_word, w, color=ORANGE, alpha=0.85, label='Mixed (per word)')

    ax.set_xticks(x)
    ax.set_xticklabels(stages, fontsize=7)
    ax.set_ylabel('Latency (ns/op)')
    ax.legend(fontsize=6, ncol=4, loc='upper right')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, axis='y')

    fig.savefig(os.path.join(OUT, 'fig3_speed_progression.png'))
    plt.close()
    print('  fig3_speed_progression.png')


# ═══════════════════════════════════════════════════════════════════
# Figure 4: Optimization Breakdown — Individual Impact
# ═══════════════════════════════════════════════════════════════════
def fig4_optimization_breakdown():
    opts = [
        'Baseline',
        'No regex',
        'Inline consts',
        'Uint32Array',
        'Fused hash',
        'Unrolled probes',
        'Power-of-2 mask',
        'All combined',
        'Native Set',
    ]
    # Mixed workload ns/op (20 words)
    mixed_ns = [1837, 589, 759, 691, 410, 633, 648, 388, 227]

    colors_list = [GRAY] + [ORANGE]*6 + [BLUE, PURPLE]

    fig, ax = plt.subplots(figsize=(5.5, 2.8))
    bars = ax.barh(range(len(opts)), mixed_ns, color=colors_list, alpha=0.85,
                   edgecolor='white', linewidth=0.3)
    ax.set_yticks(range(len(opts)))
    ax.set_yticklabels(opts, fontsize=6.5)
    ax.set_xlabel('Latency per batch of 20 lookups (ns)')
    ax.invert_yaxis()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    for bar, val in zip(bars, mixed_ns):
        pct = f' ({(1 - val/1837)*100:.0f}% faster)' if val < 1837 else ''
        ax.text(bar.get_width() + 20, bar.get_y() + bar.get_height()/2,
                f'{val} ns{pct}', va='center', fontsize=5.5)

    fig.savefig(os.path.join(OUT, 'fig4_optimization_breakdown.png'))
    plt.close()
    print('  fig4_optimization_breakdown.png')


# ═══════════════════════════════════════════════════════════════════
# Figure 5: Xor Filter — How It Works (schematic)
# ═══════════════════════════════════════════════════════════════════
def fig5_xor_schematic():
    fig, ax = plt.subplots(figsize=(5.5, 2.0))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3)
    ax.axis('off')

    # Three segments
    seg_colors = [BLUE, GREEN, ORANGE]
    seg_labels = ['Segment 0', 'Segment 1', 'Segment 2']
    for i, (c, label) in enumerate(zip(seg_colors, seg_labels)):
        x0 = 1 + i * 2.8
        rect = plt.Rectangle((x0, 0.3), 2.2, 0.8, facecolor=c, alpha=0.2,
                              edgecolor=c, linewidth=1.2)
        ax.add_patch(rect)
        ax.text(x0 + 1.1, 0.7, label, ha='center', va='center', fontsize=7,
                fontweight='bold', color=c)
        # Position markers
        pos_x = x0 + 0.5 + i * 0.4
        ax.plot(pos_x, 0.3, 'v', color=c, markersize=8)
        ax.text(pos_x, 0.12, f'h{i}', ha='center', fontsize=6, color=c)

    # Word at top
    ax.text(5, 2.6, '"hello"', ha='center', fontsize=10, fontweight='bold',
            fontfamily='monospace')

    # Arrows from word to hash
    ax.annotate('', xy=(2.5, 1.5), xytext=(4.5, 2.3),
                arrowprops=dict(arrowstyle='->', color=BLUE, lw=1))
    ax.annotate('', xy=(5, 1.5), xytext=(5, 2.3),
                arrowprops=dict(arrowstyle='->', color=GREEN, lw=1))
    ax.annotate('', xy=(7.5, 1.5), xytext=(5.5, 2.3),
                arrowprops=dict(arrowstyle='->', color=ORANGE, lw=1))

    # Hash + XOR
    ax.text(5, 1.7, 'FNV-1a + splitmix32', ha='center', fontsize=6.5,
            style='italic', color=GRAY)

    # Result
    ax.text(5, -0.15, 'B[h0] \u2295 B[h1] \u2295 B[h2] == fingerprint(word) ?',
            ha='center', fontsize=7.5, fontfamily='monospace', color='black')

    fig.savefig(os.path.join(OUT, 'fig5_xor_schematic.png'))
    plt.close()
    print('  fig5_xor_schematic.png')


# ═══════════════════════════════════════════════════════════════════
# Figure 6: Probes per Lookup — Bloom vs Xor
# ═══════════════════════════════════════════════════════════════════
def fig6_probes():
    filters = ['Bloom\n(0.1% FP)', 'Bloom\n(1% FP)', 'Xor8', 'Xor16',
               'Cuckoo', 'Binary\nFuse 8']
    probes = [10, 7, 3, 3, 2, 3]
    colors_list = [GRAY, GRAY, BLUE, ORANGE, PURPLE, GREEN]

    fig, ax = plt.subplots(figsize=(5.5, 2.0))
    bars = ax.bar(range(len(filters)), probes, color=colors_list, alpha=0.85, edgecolor='white')
    ax.set_xticks(range(len(filters)))
    ax.set_xticklabels(filters, fontsize=6.5)
    ax.set_ylabel('Memory Accesses per Lookup')
    ax.set_ylim(0, 12)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    for bar, val in zip(bars, probes):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                str(val), ha='center', fontsize=7, fontweight='bold')

    fig.savefig(os.path.join(OUT, 'fig6_probes.png'))
    plt.close()
    print('  fig6_probes.png')


# ═══════════════════════════════════════════════════════════════════
# Figure 7: Memory Usage Comparison
# ═══════════════════════════════════════════════════════════════════
def fig7_memory():
    approaches = ['Native Set\n(234k words)', 'JSON Array\n+ includes()', 'Sorted Array\n+ bsearch',
                  'Bloom Filter', 'Xor8 Filter\n(ours)']
    memory_kb = [36000, 3400, 2400, 412, 282]
    colors_list = [PURPLE, GRAY, GRAY, GRAY, BLUE]

    fig, ax = plt.subplots(figsize=(5.5, 2.3))
    bars = ax.barh(range(len(approaches)), memory_kb, color=colors_list, alpha=0.85,
                   edgecolor='white', linewidth=0.3)
    ax.set_yticks(range(len(approaches)))
    ax.set_yticklabels(approaches, fontsize=6.5)
    ax.set_xlabel('Runtime Memory (KB)')
    ax.set_xscale('log')
    ax.invert_yaxis()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    for bar, val in zip(bars, memory_kb):
        label = f'{val/1000:.0f} MB' if val >= 1000 else f'{val} KB'
        ax.text(bar.get_width() * 1.2, bar.get_y() + bar.get_height()/2,
                label, va='center', fontsize=6, fontweight='bold')

    fig.savefig(os.path.join(OUT, 'fig7_memory.png'))
    plt.close()
    print('  fig7_memory.png')


# ═══════════════════════════════════════════════════════════════════
# Generate all
# ═══════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print('Generating figures...')
    fig1_package_size()
    fig2_filter_size()
    fig3_speed_progression()
    fig4_optimization_breakdown()
    fig5_xor_schematic()
    fig6_probes()
    fig7_memory()
    print('Done.')
