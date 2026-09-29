# Historical archive

These sources are inactive and excluded from package discovery, runtime
registration, CLI commands and CI test discovery. **GROSS is authoritative.**
Historical instructions and model claims here do not govern current work.

`pre-gross/` preserves the old repository-relative paths, including Paper I
issue #1 code, browser/Node/TypeScript sources, E00/E01 implementations, older
charged/knot research, their tests/docs, and superseded repository instructions.
The two retired one-off GROSS recovery tools are explicitly categorized in the
manifest. Historical files remain unmodified; this is not a supported legacy
installation or a promise of compatibility.

`manifest.json` maps original paths to preserved bytes, with SHA-256, size,
category, and whether the file was moved or copied before an active replacement.
The baseline is main `89b3b307c621033cade9d34b518a6a4389558ecb`.
`python scripts/verify-repository.py` verifies these archive identities and the
active boundary. Git history retains the original full project topology.

All GROSS canonical evidence stays at its original `research/experiments/`
paths. Its checksummed source snapshots may contain historical dependencies;
those snapshots are evidence, not active code, and are never rewritten by this
migration.
