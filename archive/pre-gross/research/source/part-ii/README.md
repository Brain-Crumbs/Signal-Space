# Signal Space Foundations Part II source package

**Signal States, Lorentz Cones and Operational Clocks**

Version 0.1.0, 11 September 2026. This continues the completed *Composition of Signal Histories*, Foundations Part I, version 0.1.0. It is distinct from the earlier numbered Signal Space Papers I-IV.

## Contents

- `sections/`: authoritative editable manuscript sections in publication order.
- `metadata.yaml`: title, version, date, and PDF typography.
- `build.py`: assembles Markdown, checks equation identifiers, and builds the PDF with Pandoc and XeLaTeX.
- `verify.py`: deterministic verification and figure generation.
- `results.json`: executed results and software versions.
- `figures/`: vector PDF and PNG of the clock comparison.
- `ARCHITECTURE_REVIEW.md`: architecture assessment and Part III handoff.
- `CLAIM_LEDGER.md`: assumptions, dependencies, and claim boundaries.
- `SOURCE_PROVENANCE.json`: names and hashes of the exact three input manuscripts.
- `CHANGELOG.md`: revision history.
- `Signal_Space_Part_II_Signal_States_Lorentz_Cones_and_Operational_Clocks.md/.pdf`: assembled reading copies.

## Rebuild

Requirements: Python 3, NumPy, SciPy, Matplotlib, Pandoc, XeLaTeX, and a normal TeX installation with amsmath, microtype, fancyhdr and float. The executed Python versions are recorded in `results.json`. Latin Modern is used by the PDF build.

```bash
python3 verify.py
python3 build.py
```

Both commands work from any current directory. The verification uses no network and no empirical dataset. PDF builds may differ in timestamp metadata while preserving content. Inspect a fresh PDF visually after substantial edits; successful compilation is not a layout review.

## Editing procedure

Edit the relevant section file, not the assembled copy. Preserve stable equation tags when changing prose. If an assumption or equation changes, update its row in the claim ledger and any affected verification calculation. Re-run verification, rebuild, and check the PDF. Increment the version in metadata and add a changelog entry.

The standalone Markdown copy supplied outside this package keeps the figure caption and numerical tables; the figure itself is included in the PDF and the complete source package. This makes that Markdown copy independent of a companion image path. The packaged assembled manuscript retains its relative figure link.

## Interpretation of the benchmark

The count process is a driven two-state control whose ensemble mean matches a chosen accelerated curve. The cavity is a separately prescribed bounded field model with that center curve. Their agreement on the reference curve does not make them one autonomous physical model. Acceleration switching, detector sampling, binding, recoil and energetic normalization are outside the executed calculation.

## Submission preparation

The manuscript has complete technical prose, equations, proofs, references and reproducible controls. The submitting author must provide accurate authorship, affiliations, disclosure of assistance and any venue-specific declarations. No journal, affiliation or external peer-review status is assumed.
