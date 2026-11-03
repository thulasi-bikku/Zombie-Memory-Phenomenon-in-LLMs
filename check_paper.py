"""Consistency checks for paper/main.tex.  Exit code 1 if any check fails.

    python tools/check_paper.py [paper/main.tex]
"""
import re, sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from stats_check import check_wilson, check_seed_stats  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "paper" / "main.tex"
tex = path.read_text(encoding="utf-8")
body = re.sub(r"(?<!\\)%.*", "", tex)            # drop comments
text_body = body[: body.index("\\begin{thebibliography}")]
fails, notes = [], []


def fail(msg): fails.append(msg)


# 1. unresolved placeholders ------------------------------------------------
for pat in [r"\\needed", r"\[n_?\{?mem", r"\[n_?\{?non", r"\[K\]", r"\bTODO\b", r"\bXXX\b", r"\bTBD\b", r"\?\?"]:
    for m in re.finditer(pat, body):
        fail(f"placeholder pattern {pat!r} near: {body[max(0, m.start()-30):m.end()+30]!r}")
sett = (path.parent / "lira_settings.tex")
if not sett.exists():
    fail("paper/lira_settings.tex is missing")
else:
    for macro in ["LiRAnmem", "LiRAnnon", "LiRAK"]:
        m = re.search(r"\\newcommand\{\\" + macro + r"\}\{([^}]*)\}", sett.read_text())
        if not m or not m.group(1).strip().isdigit():
            fail(f"LiRA setting \\{macro} is not filled with an integer (run tools/make_lira_settings.py)")

# 2. labels / references ------------------------------------------------------
labels = re.findall(r"\\label\{([^}]+)\}", body)
for l, c in Counter(labels).items():
    if c > 1: fail(f"duplicate label {l}")
refs = set()
for m in re.finditer(r"\\(?:ref|eqref|autoref)\{([^}]+)\}", body):
    refs.add(m.group(1))
for r in sorted(refs - set(labels)): fail(f"\\ref to undefined label {r}")
for l in sorted(set(labels) - refs):
    if l.startswith(("fig:", "tab:")): fail(f"{l} is never referenced in the text")

# 3. citations ------------------------------------------------------------------
bib_keys = re.findall(r"\\bibitem\{([^}]+)\}", body)
cited = []
for m in re.finditer(r"\\cite[a-z]*\{([^}]+)\}", text_body):
    cited += [k.strip() for k in m.group(1).split(",")]
for k in sorted(set(cited) - set(bib_keys)): fail(f"cited key without bibliography entry: {k}")
for k in sorted(set(bib_keys) - set(cited)): fail(f"bibliography entry never cited: {k}")
first = []
for k in cited:
    if k not in first: first.append(k)
if [k for k in bib_keys if k in first] != first:
    fail("bibliography is not in order of first citation")

# 4. figures ------------------------------------------------------------------------
gp = re.search(r"\\graphicspath\{\{([^}]+)\}\}", body)
gdir = path.parent / (gp.group(1) if gp else "")
for m in re.finditer(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", body):
    name = m.group(1)
    if not any((gdir / (name + e)).exists() for e in ["", ".pdf", ".png", ".jpg"]):
        fail(f"figure file not found: {name}")

# 5. numbers ----------------------------------------------------------------------------
p, ok = check_wilson(body)
fails.extend(p); notes.append(f"{ok} Wilson intervals verified")
fails.extend(check_seed_stats([0] * 5, [2, 2, 1, 2, 3]))
must = ["10/250", "0/250", "0.0625", "0.03125", "91.8"]
for s in must:
    if s not in body: fail(f"expected figure {s} not found")
for bad in ["0.0625 two", "p = 0.062 "]:
    pass

# 6. typography ----------------------------------------------------------------------------
for pat, why in [(r"\d\s+\\?%", "space before percent sign"), (r"\\,\\%", "thin space before percent sign"),
                 (r"\$\d+(?:\.\d+)?\\%\$", "percentage in math mode"), (r"\bp-value", "p-value without math italics"),
                 (r"\b124 M\b", "124 M"), (r"\bGPT-?2\s+small\b", "GPT-2 small (lower case)"),
                 (r"\bbitsandbytes\b(?!\})", "bitsandbytes outside \\texttt")]:
    for m in re.finditer(pat, text_body):
        ctx = text_body[max(0, m.start()-25):m.end()+25].replace("\n", " ")
        if "texttt{bitsandbytes" in ctx: continue
        if "\\newcommand" in ctx: continue
        fail(f"{why}: ...{ctx}...")

# 7. repeated content ---------------------------------------------------------------------------
heads = re.findall(r"\\(?:sub)*section\*?\{([^}]+)\}", body)
for h, c in Counter(heads).items():
    if c > 1: fail(f"duplicate heading: {h}")
plain = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?", " ", text_body)
plain = re.sub(r"[{}$\\]", " ", plain)
sents = [re.sub(r"\W+", " ", s).strip().lower() for s in re.split(r"(?<=[.!?])\s+", plain)]
seen = Counter(s for s in sents if len(s) > 60)
for s, c in seen.items():
    if c > 1: fail(f"sentence appears {c} times: {s[:90]}...")
# paragraph-level near duplicates (shared 8-word shingles)
paras = [re.sub(r"\W+", " ", p).lower().split() for p in re.split(r"\n\s*\n", plain) if len(p.split()) > 40]
def sh(w): return {" ".join(w[i:i+8]) for i in range(len(w) - 7)}
for i in range(len(paras)):
    for j in range(i + 1, len(paras)):
        a, b = sh(paras[i]), sh(paras[j])
        if a and b and len(a & b) / min(len(a), len(b)) > 0.35:
            fail(f"paragraphs {i} and {j} overlap strongly: {' '.join(paras[i][:10])}...")

print("\n".join("ok   " + n for n in notes))
if fails:
    print(f"\n{len(fails)} problem(s):"); print("\n".join(" - " + f for f in fails)); sys.exit(1)
print("all consistency checks passed")
