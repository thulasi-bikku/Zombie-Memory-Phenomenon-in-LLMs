"""Recompute every Wilson interval and the seed-level tests quoted in the manuscript."""
import math, re, sys
from itertools import product
from pathlib import Path

Z = 1.959963984540054


def wilson(k, n, z=Z):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return 100 * max(0.0, c - h), 100 * min(1.0, c + h)


def wilcoxon_exact(diffs):
    """Exact Wilcoxon signed-rank p-values (one-sided: x > 0; two-sided) with average ranks, zeros dropped."""
    d = [x for x in diffs if x != 0]
    n = len(d)
    order = sorted(range(n), key=lambda i: abs(d[i]))
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and abs(d[order[j + 1]]) == abs(d[order[i]]):
            j += 1
        for t in range(i, j + 1):
            ranks[order[t]] = (i + j) / 2 + 1
        i = j + 1
    w_obs = sum(r for r, x in zip(ranks, d) if x > 0)
    tot = 0
    ge = le = 0
    for signs in product([0, 1], repeat=n):
        w = sum(r for r, s in zip(ranks, signs) if s)
        tot += 1
        ge += w >= w_obs - 1e-9
        le += w <= w_obs + 1e-9
    p_one = ge / tot
    p_two = min(1.0, 2 * min(ge, le) / tot)
    return p_one, p_two


CI_RE = re.compile(r"(\d+)\s*/\s*(\d+)[^\[\]/\n]{0,90}?\[\s*([\d.]+)\\%\s*,\s*(?:\\,)?\s*([\d.]+)\\%\s*\]")


def check_wilson(tex):
    problems, n_ok = [], 0
    for m in CI_RE.finditer(tex):
        k, n, lo, hi = int(m[1]), int(m[2]), float(m[3]), float(m[4])
        clo, chi = wilson(k, n)
        if abs(clo - lo) > 0.051 or abs(chi - hi) > 0.051:
            problems.append(f"Wilson mismatch for {k}/{n}: manuscript [{lo}, {hi}] vs computed [{clo:.1f}, {chi:.1f}]")
        else:
            n_ok += 1
    return problems, n_ok


def check_seed_stats(counts_unl, counts_q, per_seed_n=50):
    out = []
    diffs = [q - u for q, u in zip(counts_q, counts_unl)]
    p1, p2 = wilcoxon_exact(diffs)
    rates = [100 * q / per_seed_n for q in counts_q]
    mean = sum(rates) / len(rates)
    sd = math.sqrt(sum((r - mean) ** 2 for r in rates) / (len(rates) - 1))
    out.append(("pooled successes", sum(counts_q), 10))
    out.append(("Wilcoxon one-sided p", round(p1, 5), 0.03125))
    out.append(("Wilcoxon two-sided p", round(p2, 4), 0.0625))
    out.append(("mean rate (%)", round(mean, 1), 4.0))
    out.append(("sample SD (pp)", round(sd, 1), 1.4))
    return [f"{name}: computed {a}, manuscript {b}" for name, a, b in out if abs(a - b) > 1e-9]


if __name__ == "__main__":
    tex = Path(sys.argv[1]).read_text(encoding="utf-8")
    probs, ok = check_wilson(tex)
    probs += check_seed_stats([0, 0, 0, 0, 0], [2, 2, 1, 2, 3])
    print(f"{ok} Wilson intervals verified")
    print("\n".join(probs) if probs else "no statistical mismatches")
    sys.exit(1 if probs else 0)
