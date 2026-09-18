# Research artifact contract

## 1. Purpose

A run package is the durable, inspectable evidence for one resolved experiment configuration. It must be sufficient to audit execution, resume when supported, reproduce analysis, regenerate reports, and determine exactly which bytes support a claim.

## 2. Package layout

```text
research/experiments/<experiment-id>/<run-id>/
  manifest.json
  resolved-config.json
  provenance/
    code.json
    environment.json
    dependencies.lock
    inputs.json
  attempts/<attempt-id>/
    attempt.json
    events.jsonl
    checkpoints/
    raw/
    logs/
  analyses/<analysis-id>/
    analysis.json
    checks.json
    derived/
  reports/<report-id>/
    report.md
    report.html
    report.pdf
    figures/
    plot-data/
  checksums.sha256
```

Large packages may live in external artifact storage. The Git archive keeps the same manifest, checksums, compact evidence, and durable locator; storage location never substitutes for content identity.

## 3. Identity and immutability

- `experiment_id` and `model_id` identify versioned registered definitions.
- `run_id` identifies the canonical resolved configuration and provenance key.
- `attempt_id` identifies one execution or resume chain member.
- `analysis_id` identifies code, parameters, and immutable input artifacts.
- `report_id` identifies an analysis selection and rendering specification.

Raw attempt bytes are append-only until the attempt reaches a terminal technical state, then immutable. Resume never edits the previous attempt. Reanalysis never edits raw data. Regeneration may reproduce an identical report ID only when all inputs and renderer identities match.

## 4. Required manifest fields

The versioned manifest records:

- schema, experiment, model, and package versions;
- run and parent IDs;
- created/updated timestamps and technical state;
- scientific classification: `pass`, `fail`, `unresolved`, or `not-evaluated`;
- canonical config hash and config path;
- code commit/tree state and dirty-patch hash;
- runtime, OS, architecture, dependencies, numeric libraries, and accelerator identity;
- seed algorithm and independent seed-stream ledger;
- attempts, checkpoints, analyses, reports, and artifact index;
- acceptance criteria and evidence links;
- completeness flags and known gaps;
- checksum algorithm and checksum file.

Unknown fields are rejected within a major schema version. Migrations create a new manifest while preserving the source manifest and recording the migration tool.

## 5. Events and logs

`events.jsonl` is append-only. Each event has a monotonically increasing sequence, attempt-local timestamp, event type, stage, and structured payload. Consumers reconnect with the last acknowledged sequence. Gaps, duplicates, and out-of-order delivery are detected; the stored log is authoritative.

Logs are diagnostic text, not the state machine. A visible error event and terminal attempt record are required even when the process exits unexpectedly.

## 6. Checkpoints and resume

A checkpoint includes every state needed for valid continuation: fields, conjugate variables, mesh/domain, adaptive solver state, continuation tangent/history, RNG streams, pending work, accumulated diagnostics, and checkpoint-format version. Its metadata records the producing config/code hash and parent attempt.

Resume is rejected when required identities differ or bytes fail checksums. A consciously supported numerical migration must be explicit, versioned, tested, and recorded as a new attempt.

## 7. Raw, derived, and presentation data

- **Raw:** direct solver output and conserved-ledger samples.
- **Derived:** profiles, spectra, fits, interpolations, convergence tables, classifications.
- **Plot data:** the exact rows/arrays displayed after declared transformations.
- **Figures:** renderings of plot data and a figure specification.
- **Reports:** narrative assembled from immutable references.

Downsampling, smoothing, unwrapping, normalization, fitting, and window selection are analysis operations. They must never silently replace raw data.

## 8. Claims and evidence

Every scientific claim is a record with:

- stable claim ID and cautious statement;
- scope and model version;
- status and confidence/error interpretation;
- required criteria;
- links to checks, datasets, plots, and controls;
- numerical and modeling limitations;
- superseded claim IDs when revised.

A report may summarize a claim but cannot create evidence that is absent from its linked analysis. `unresolved` remains visible and is not coerced to pass/fail.

## 9. Verification

`verify` checks schemas, hashes, referenced paths, sequence continuity, terminal-state consistency, parent links, checkpoint compatibility, acceptance-evidence completeness, and report/figure inputs. It does not declare the physics correct; it establishes package integrity and traceability.

## 10. Archive policy

Archive a package only when:

- configuration and provenance are complete;
- every attempt has an explicit technical state;
- missing/omitted raw artifacts are declared with content hashes and locators;
- analyses and reports pass integrity verification;
- scientific classification is explicit;
- limitations and failed controls remain included.

The current `research/source/` collection is an imported historical evidence archive, not a conforming run package. New experiments use this contract.
