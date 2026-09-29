from __future__ import annotations

import hashlib


STREAM_NAMES = ("initialization", "perturbations", "sampling", "analysis")


def seed_ledger(root: int) -> dict[str, int]:
    return {
        name: int.from_bytes(hashlib.sha256(f"sha256-stream-v1:{root}:{name}".encode()).digest()[:8], "big")
        for name in STREAM_NAMES
    }


def next_state(state: int) -> int:
    """A fixed 64-bit xorshift state transition for checkpointable fixture streams."""
    state &= 0xFFFFFFFFFFFFFFFF
    state ^= state << 13 & 0xFFFFFFFFFFFFFFFF
    state ^= state >> 7
    state ^= state << 17 & 0xFFFFFFFFFFFFFFFF
    return state & 0xFFFFFFFFFFFFFFFF
