# C1-4 pilot result and confirmation obstruction

Issue [#96](https://github.com/Brain-Crumbs/Signal-Space/issues/96), parent #92.
**All five locked pilot checks pass. Confirmation is blocked / not evaluated.**
The physical model and prior Tests1–11 classifications remain unchanged.

Run `run-4fb4fc6333a29dbd`, attempt `attempt-0001`, analysis
`analysis-0001-ec7930b5`, selected report `report-0002`. The scientific launch
used clean committed revision `770729bc416d866d0948fff34f01295dafb953fc`.
The [machine-readable handoff](gross-certificate-pilot-results.json) records
exact source/config/plan/checksum identities, readiness hash and archive locator.

Both fixed seeds at96/128-bit precision independently certify all three records
at both A/B endpoints for the full radius1e-6 physical preparation ball, including
all16 directions. Each of the four saved proof packets replays independently;
all endpoint horizons are two gates. Maximum preparation bound is
1.935833173903007e-6, below2.5e-4. This is a bounded one-cycle mathematical
certificate using the shared qualified arithmetic, not a physical detector,
all-time certificate, clock or geometry claim.

| Measurement | Pilot or forecast |
| --- | --- |
| Worker CPU / wall |9.488839947s /9.497990985s measured|
| Worker kernel self max-RSS |77,832,192bytes measured|
|32-cycle worker CPU / wall |2143.774055s /2147.134113s extrapolated|
|32-cycle memory / scientific output |2375.25MiB /60.781738MiB extrapolated|
| Reserved pilot / confirmation |60s /240s CPU and wall|

The coarse intact-product work-count extrapolation exceeds the190s confirmation
worker ceiling and1024MiB memory limit. It is neither a measured32-cycle cost
nor a rigorous runtime bound; it can reject a feasible implementation. Missing
process-monitor CPU/RSS are unavailable, not zero. Worker self metrics remain
saved; the analysis consumes its full15s reservation. Scientific output has
16MiB pilot and112MiB confirmation reservations within128MiB total.

No confirmation lock or Task5 command is fabricated. A new bounded cost-model
qualification or an explicit revised budget is needed before a separately
registered32-cycle plan can be locked. No32-cycle execution occurred.

The2.64MB evidence ZIP contains canonical raw/proof/checker bytes, immutable
analysis, both reports, budget reservations and retained checker staging, exact
figure data, reader setup/results PDFs, final readiness and source snapshot/Git
bundle. Archive SHA-256:
`f4c5e4986ac6d84ad01c1e5d0d441882987e895292482f9dc6bd498831a80764`.
The initial renderer failed before sealing; an integer-string presentation fix
produced report0001. Aligning figure-question strings with the immutable plan
produced report0002. Failed export notes and recovery logs remain saved. Raw
and scientific analysis were unchanged; no pilot retry occurred.

Validation:126 Python tests and13 agent-contract tests pass on Python3.12.14
with the performance dependency lock; repository/math checks, locked plan,
canonical verification and paired reader validation pass. Setup/results PDFs
were visually checked. Development tests and rendering are separate from the
scientific budget. Ubuntu/Windows hosted CI is tracked on the feature PR.
