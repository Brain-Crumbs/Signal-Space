# Test 7 publication provenance

The solver completed one attempt with no solver failure. Original pipeline metadata and logs are preserved here; the canonical package preserves raw data, events, analysis and both reports. `original-evidence-index.json` describes the full original scratch pipeline package, not this selected publication subset. The original canonical manifest/checksum ledger is retained to identify report-0001's package before report-0002 was appended.

The redundant 63 MiB whole-repository source archive is identified by its original SHA-256 in `original-execution.json`; its exact Git source commit is 144ec614e1e3bfcfe84cd6c64fd90dab2322ef24. `solver-source.tar.gz` retains the relevant source tree, configs, contracts, plans and frozen inputs from that commit. The reader export also includes the final Python sources. Registry-order, missing-marker classification and presentation fixes have later source commits; the physical solver, action and locked criteria did not change.

`check.log` preserves the initial default-experiment ordering regression; `check-rerun.log` records the passing full gate after correction. Browser installation and test logs record the environmental block. No browser pass is claimed.

`posthoc_marker_diagnostic.py` and `posthoc-marker-decomposition.json` reproduce an explicitly post-hoc diagnostic. They neither replace the blind forecast nor change the scientific classification. Run with PYTHONPATH=python and --raw pointing to the canonical attempt raw directory, --config fixtures/research/gross-test-07.json, and --output a new JSON path.

Git command-line publication lacked credentials, so the connected GitHub Git-data API publishes the final tree with its own commit identity. `solver-commits.bundle` preserves the exact local solver/analysis/renderer commit ancestry (through b98f49d) on top of the original main commit. From a clone containing that main history, use `git fetch path/to/solver-commits.bundle provenance/test7-solver` to recover every source commit referenced by the canonical evidence. Bundle integrity was verified before publication.
