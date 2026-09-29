#!/usr/bin/env python3
"""Regenerate the current summary from the reviewed, hash-linked research ledger."""
import argparse
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from signal_space.workflow.ledger import markdown
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--check',action='store_true')
args=parser.parse_args()
path=ROOT/'docs/research/gross-current.md'
expected=markdown()
if args.check:
    if not path.exists() or path.read_text(encoding='utf-8')!=expected:
        raise SystemExit('current research summary is stale; run scripts/update-research-ledger.py')
else: path.write_text(expected,encoding='utf-8')
