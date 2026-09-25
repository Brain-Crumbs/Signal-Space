# Failed pipeline attempts (diagnostic evidence)

These are retained to audit failed work, not validated reader exports. The source commitments, seed ledgers and raw arrays are preserved in their respective run directories. **Do not re-seal the corrupted first package to make it appear verified.**

1. `01-checksum`: source commit `07f0f1a`; solver and analysis completed and their checks passed. At report stage the event log's saved bytes no longer matched the canonical checksum. The retained run is integrity-invalid and should not support the selected result.
2. `02-question-mismatch`: source commit `07f0f1a`; its solver, analysis, report and canonical verification completed. Packaging rejected a figure interpretation question that differed from the locked plan; no reader export was produced. The physics settings and thresholds were unchanged.

The selected run `run-d3333c7602af3e47` used source commit `b79f765` with atomic PDF publication and a matching figure question. See its independent canonical verification and reviewed reader export in the parent experiment folder.
