# Signal Space / GROSS Test 1

Completed under issue #52. Scientific classification: **pass for the stated algebra checks**.

Start with the [reader export](export-run-2ae9c65dbd171851/README.md), [results PDF](export-run-2ae9c65dbd171851/Experiment_Results.pdf), or [canonical run manifest](run-2ae9c65dbd171851/manifest.json).

The run contains 1,000 seeded samples and six passed checks. The maximum normalized residual is 3.963119603223247e-14, below 1e-10. The omitted-weight control returns 0.6321205588285577; singular aggregates are rejected. This does not establish physical geometry.

`provenance/` preserves execution/validation logs and the original local Git commits. The connected GitHub app publishes identical source trees with different commit metadata. To recover the exact solver revision in a clone with the base commit available:

```sh
git bundle verify research/experiments/gross.operator-identities.v1/provenance/solver-source.bundle
git fetch research/experiments/gross.operator-identities.v1/provenance/solver-source.bundle HEAD:refs/heads/reproduce-gross-test-01
git fetch research/experiments/gross.operator-identities.v1/provenance/report-source.bundle HEAD:refs/heads/reproduce-gross-report-02
```

See `provenance/source-identity.json` for commit/tree mapping and `provenance/validation.json` for the verification summary. Browser tests were attempted but Chromium installation is blocked in this environment. The original raw run, both report versions, and the locked decision criteria are preserved.
