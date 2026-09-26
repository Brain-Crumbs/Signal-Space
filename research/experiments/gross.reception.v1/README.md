# Test 7: surface-only predicted reception

**Technical completion; scientific fail.** Ten checks pass, two fail. The clock response is resolved, but the nominal single-pulse interval prediction misses its locked 5% tolerance and coarse-grid marker timing misses its bound. No thresholds were changed.

- [Reviewed analysis and next calculation](export-run-b1677e67610c5870/Experiment_Analysis_and_Next.md)
- [Reader package](export-run-b1677e67610c5870/README.md)
- [Setup PDF](export-run-b1677e67610c5870/Experimental_Setup.pdf)
- [Results PDF with six interpreted figures](export-run-b1677e67610c5870/Experiment_Results.pdf)
- [Canonical evidence](run-b1677e67610c5870/manifest.json)
- [Publication provenance and validation](provenance/local-run-b1677e67610c5870/README.md)
- [Post-hoc diagnostic values](provenance/local-run-b1677e67610c5870/posthoc-marker-decomposition.json) and [reproduction source](provenance/local-run-b1677e67610c5870/posthoc_marker_diagnostic.py)

The post-hoc diagnostic is separate from locked acceptance. It suggests an omitted fourth-order response term; it does not turn the failed prediction into a pass. Test 8 remains blocked by this acceptance result. No two-object recoil, coordinate-invariance or emergent-spacetime claim is made.
