"""Check that new experiment Markdown uses the repository's math rendering syntax.

Historical source papers are outside this check. Checksummed canonical runs are
scanned but never rewritten, so new reports cannot silently introduce a broken
math expression into the reader-facing experiment documents.
"""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
paths = sorted((ROOT / "docs/research").glob("gross*.md"))
paths += sorted((ROOT / "research/experiments").glob("gross*/**/*.md"))
problems = []

for path in paths:
    in_fence = False
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if "\\operatorname" in line:
            problems.append((path, number, "use a supported math command such as \\mathrm"))
        if "{}_" in line:
            problems.append((path, number, "remove empty groups before subscripts in inline math"))
        if "^*" in line:
            problems.append((path, number, "write complex conjugation without a Markdown emphasis marker"))
        if any(mark in line for mark in ("\\(", "\\)", "\\[", "\\]")):
            problems.append((path, number, "use $...$ or standalone $$ lines"))
        if "$$" in line and line.strip() != "$$":
            problems.append((path, number, "put display-math $$ delimiters on separate lines"))

for path, number, message in problems:
    print(f"{path.relative_to(ROOT)}:{number}: {message}", file=sys.stderr)

print(f"Checked math formatting in {len(paths)} experiment Markdown files")
sys.exit(bool(problems))
