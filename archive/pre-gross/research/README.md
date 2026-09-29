# Research collection

This directory is the versioned evidence and source collection for the Signal Space research program.

## Collections

- `papers/`: theory manuscripts, model definitions, and critical correspondence grids.
- `milestones/`: reports produced from executed calculations.
- `figures/`: curated diagnostic images used by those reports.
- `source/`: reproducibility code, configurations, provenance, manifests, and compact derived results imported from the original calculation bundles.
- `experiments/`: accepted immutable run packages following `docs/research/artifact-contract.md`.

`catalog.json` drives the local research explorer. `archive-manifest.json` records every tracked research file and SHA-256 digest. Run `npm run verify:research` to detect missing, changed, or uncatalogued top-level evidence.

## Import boundary

The imported source bundles contained large raw CSV trajectories, probe streams, field snapshots, and array files. Those high-volume intermediates are intentionally excluded from Git. The imported compact results, code, configurations, reports, and figures preserve the practical scientific audit surface, while `archive-manifest.json` checksums every included byte. New work uses immutable externally stored run packages with checksummed locators rather than committing raw arrays to Git history.

Papers, reports, source references, filenames, and figure titles were normalized to the active Signal Space project name during import. Duplicate rendered manuscripts with embedded historical titles were omitted in favor of their complete Markdown sources. Equations, numerical values, and scientific status statements were otherwise preserved.

## Adding material

1. Place the artifact in the appropriate collection.
2. Add or update its `catalog.json` entry.
3. Run `npm run research:manifest` and inspect the diff.
4. Run `npm run verify:research` and the normal repository checks.
5. Link source, report, figure, and experiment relationships in catalog metadata.
