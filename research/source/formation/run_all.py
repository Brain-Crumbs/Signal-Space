"""Regenerate all simulations, diagnostics, report and figures, without network access."""
import pathlib,subprocess,sys,os
ROOT=pathlib.Path(__file__).resolve().parent
(ROOT/'results').mkdir(exist_ok=True)
env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
subprocess.run(['g++','-O3','-std=c++17',str(ROOT/'evolve.cpp'),'-o',str(ROOT/'evolve')],check=True)
for name in ['run_scan.py','run_refined_scan.py','run_checks.py','run_extra.py','run_long_validation.py','run_protocol_refinement.py']:
 subprocess.run([sys.executable,str(ROOT/name)],check=True,env=env)
subprocess.run([str(ROOT/'evolve'),str(ROOT/'results/pilot'),'.9','2','.9','.05','.01','800','gauss','0'],check=True)
for name in ['analyze.py','make_figures.py','make_report.py']:
 subprocess.run([sys.executable,str(ROOT/name)],check=True,env=env)
