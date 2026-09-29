"""Reproduce the fixed-charge amplitude scan and resonance calculation."""
from pathlib import Path
import subprocess,os,sys
ROOT=Path(__file__).resolve().parent
os.environ['OPENBLAS_NUM_THREADS']='1'
for script in ['resonance.py','setup_scan.py','discrete_resonance.py','ground_correction.py','run_scan.py','analyze_scan.py']:
 subprocess.run([sys.executable,str(ROOT/script)],cwd=ROOT,check=True)
from analyze_scan import analyze
for tag in ['b0.0025_fine','b0.01_superfine','b0.09_fine']:
 for lo,hi in [(200,450),(450,700)]:analyze(tag,lo,hi)
for script in ['summarize.py','make_figure.py','make_report.py']:
 subprocess.run([sys.executable,str(ROOT/script)],cwd=ROOT,check=True)
