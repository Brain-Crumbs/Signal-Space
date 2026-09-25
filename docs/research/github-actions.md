# Run an experiment on GitHub

Tracking: #52; runtime dependency: #37. The workflow executes registered experiments with the same locked-plan gate used locally. Test 1 maps to operator program sections 2–4 and 15.1; this infrastructure adds no physical model or acceptance criteria.

## First run

1. Merge the PR containing `.github/workflows/run-experiment.yml` when ready. GitHub requires a manual workflow to exist on the default branch before it can be dispatched. This PR does not merge itself.
2. Open **Actions → Run experiment → Run workflow**.
3. Choose the branch containing the experiment implementation, select **gross-test-01**, and choose artifact retention (7, 30, or 90 days; repository policy also applies).
4. Run the workflow. The selected branch is resolved to a source commit; that exact checked-out commit and tree are saved with the results.
5. Read the job summary, then download both **evidence-gross-test-01-RUN-ATTEMPT** and **reader-gross-test-01-RUN-ATTEMPT** from that run's Artifacts section.

After the workflow is on `main`, the equivalent CLI invocation is:

```sh
gh workflow run run-experiment.yml \
  --repo Brain-Crumbs/Signal-Space \
  --ref research/gross-test-01-operator-identities \
  -f experiment=gross-test-01 -f retention_days=30
```

Use `--ref main` if the experiment branch has been deleted after merging. A new manual dispatch or GitHub rerun creates a fresh workspace and unique artifact names containing the Actions run ID and attempt number. It does not resume or overwrite an earlier experiment. A matching canonical run ID across equivalent environments is possible; Actions execution IDs still distinguish invocations.

## What executes

The workflow installs Python 3.12 and the pinned scientific dependencies on Ubuntu 24.04. BLAS thread counts are fixed to one. It requires a clean checkout, saves a source archive, validates the plan/configuration hash and resource estimate, executes through `run_plan.py`, then analyzes saved outputs, renders reports, verifies the canonical package, and builds and validates the reader export.

The initial recipe is the existing 1,000-sample Test 1 with seed 2026092501, three figures, and six locked algebra/implementation checks. Worker ceilings remain 60 seconds CPU/wall, 512 MiB memory and 16 MiB output. The workflow has a separate 15-minute total ceiling for dependency installation, analysis, reporting and uploads. End-to-end runtime is expected to be a few minutes; this is an estimate until measured on Actions.

Inputs intentionally select a reviewed recipe rather than override samples, tolerances, seeds or arbitrary shell commands. To add an experiment or change its scientific configuration, register its implementation and locked plan in a branch and extend `RECIPES` in `.agents/scripts/run_experiment.py` and the workflow's choice list. Each recipe must produce compatible figure interpretations and have an appropriate assessment adapter; the current assessment is specifically for Test 1.

## Downloads and interpretation

| Artifact | Contents                                                                                                                                                                                           |
| -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Evidence | `runs/<experiment-id>/<run-id>/` canonical package; raw inputs, seeds, analyses, reports and checksums; `source.tar.gz`; plan/config; `execution.json`; stage logs; status and an outer hash index |
| Reader   | README, setup/results PDFs, analysis/next-calculation Markdown, figures and their interpretations, exact plot data, Python sources and `export.json`                                               |

The source snapshot preserves the exact Git tree even if a branch is removed. Runtime provenance records the numerical environment; fixed versions and threads do not imply bitwise equality across different hardware.

The assessment is generated from this run's saved checks and explicitly awaits human scientific interpretation and visual review. A scientific `fail` or `unresolved` result is still a successful pipeline completion when execution, analysis, reporting and integrity checks complete. It remains visible in the summary and downloads. A technical failure stops dependent stages and fails the job; available evidence/logs are uploaded, and no completed reader artifact is advertised. Dependency-install failures retain the Actions log and a setup diagnostic artifact when available. Abrupt runner loss or cancellation can prevent uploads; artifacts are not a checkpoint service.

The workflow has read-only repository permissions and no automatic commit, PR, merge or archive step. It is manual-only; normal pushes/PRs continue to run the existing CI without launching this full research run. No API key is needed for templated reports.

## Verify and check in a selected result

Download the two artifacts from the same run **and attempt**, and extract them into separate `evidence/` and `reader/` directories outside your checkout. Install the repository's pinned Python dependencies. From the checkout, substitute the run ID shown in `evidence/status.json` and your download path:

```sh
export DOWNLOAD_DIR=/absolute/path/to/downloads
export EXPERIMENT_RUN_ID=run-REPLACE
export PYTHONPATH=python
python -m signal_space --workspace "$DOWNLOAD_DIR/evidence/runs" verify --run-id "$EXPERIMENT_RUN_ID"
python .agents/scripts/experiment_contract.py bundle "$DOWNLOAD_DIR/reader"
```

Before combining or committing the downloads, verify their pairing and the outer evidence index:

```sh
python - <<'PY'
import hashlib, json, os
from pathlib import Path
base = Path(os.environ['DOWNLOAD_DIR'])
index = json.loads((base / 'evidence/evidence-index.json').read_text())
for item in index['files']:
    actual = hashlib.sha256((base / 'evidence' / item['path']).read_bytes()).hexdigest()
    if actual != item['sha256']:
        raise SystemExit(f"Evidence checksum mismatch: {item['path']}")
export = json.loads((base / 'reader/export.json').read_text())
source = export['source_run']
if source['run_id'] != os.environ['EXPERIMENT_RUN_ID']:
    raise SystemExit('Selected run differs from reader export')
manifest = base / 'evidence/runs' / source['experiment_id'] / source['run_id'] / 'manifest.json'
if hashlib.sha256(manifest.read_bytes()).hexdigest() != source['manifest_sha256']:
    raise SystemExit('Reader and evidence are not the same canonical package')
print('Evidence hashes and reader/canonical pairing verified')
PY
```

On a results branch, copy the canonical directory to `research/experiments/<experiment-id>/<run-id>/` and the reader directory to `research/experiments/<experiment-id>/export-<run-id>/`. Refuse existing destinations; do not overwrite an earlier run/export. Keep their bytes unchanged so the reader's manifest hash remains valid. The reader's portable source locator already names that repository destination. Retain the outer evidence metadata/logs/source snapshot alongside them in a uniquely named `provenance/actions-<Actions-run-ID>-<attempt>/` directory.

Add a catalog entry in `research/catalog.json` pointing to the selected report and stating its scientific classification and limitations. Run `npm run research:manifest` to refresh the outer archive inventory, then `npm run check`, inspect the diff, commit and open a results PR. Do not run the runtime `archive` command on these already paired files: it transitions the manifest to `archived`, which would require a newly generated reader export with that new manifest hash. A verified completed package can be preserved byte-for-byte in Git without that optional state transition.

An optional future **Archive run** workflow can automate this verified import and open a PR. This first version intentionally delivers the manual run and download path; selection and check-in remain under your control. Preserve selected evidence before artifact expiry. Larger datasets should use durable external storage with hashes and locators committed to the catalog.

## Local rehearsal

From a clean, committed checkout and the pinned Python environment:

```sh
python .agents/scripts/run_experiment.py \
  --experiment gross-test-01 \
  --output /absolute/new/directory/outside-the-checkout
```

This executes the same orchestration as Actions, including failure handling, source snapshot, report packaging and verification. It does not test GitHub dispatch or artifact upload. Existing historical Test 1 results remain unchanged; a rehearsal or hosted execution is a separate invocation.

GitHub references: [manual dispatch](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow), [artifact download and retention](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/download-workflow-artifacts).
