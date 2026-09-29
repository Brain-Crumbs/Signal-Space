#!/usr/bin/env python3
"""Compatibility entrypoint for the shared recoverable GROSS pipeline."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from signal_space.workflow.pipeline import Pipeline, assessment, RECIPES, main
if __name__ == '__main__':
    raise SystemExit(main())
