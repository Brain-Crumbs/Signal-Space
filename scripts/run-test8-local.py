#!/usr/bin/env python3
"""Compatibility wrapper for the generic recoverable quiet pipeline and handoff."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from signal_space.workflow.artifacts import handoff, pack as _pack
from signal_space.workflow.pipeline import Pipeline
from signal_space.runtime.io import sha256_file as sha


def pack(folder, output):
    # Historical callers expect this strict single-use helper.
    if Path(output).exists(): raise ValueError('archive already exists; preserve its identity')
    return _pack(folder,output)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--package-only',action='store_true')
    parser.add_argument('--resume',action='store_true')
    parser.add_argument('--threads',type=int,default=1)
    parser.add_argument('--case-jobs',type=int,default=1)
    parser.add_argument('--recipe',choices=['gross-test-08-quiet','gross-test-08-quiet-optimized'],default='gross-test-08-quiet-optimized')
    parser.add_argument('--locator')
    args=parser.parse_args()
    try:
        if not args.package_only:
            code=Pipeline(ROOT,args.output,args.recipe,args.threads,args.case_jobs,resume=args.resume).run()
            if code: return code
        import json
        print(json.dumps(handoff(args.output,locator=args.locator),indent=2))
        return 0
    except (ValueError,OSError) as error:
        print(f'quiet handoff rejected: {error}',file=sys.stderr);return 1


if __name__=='__main__':
    raise SystemExit(main())
