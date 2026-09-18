"""Regenerate the three spectral continuations and the report from the saved state."""
import pathlib,subprocess,sys,os
R=pathlib.Path(__file__).resolve().parent
(R/'results').mkdir(exist_ok=True);(R/'deliverables').mkdir(exist_ok=True)
env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
subprocess.run(['g++','-O3','-std=c++17',str(R/'evolve_spectrum.cpp'),'-o',str(R/'evolve_kick')],check=True)
def py(script,*args):subprocess.run([sys.executable,str(R/script),*args],check=True,env=env)
py('run_kick.py')
for n in ['kick_coarse','kick_fine','kick_timefine']:py('analyze_spectrum.py',n)
py('analyze_spectrum.py','kick_fine','200','600');py('analyze_spectrum.py','kick_fine','600','1000')
for s in ['diagnostics.py','make_figure.py','make_report.py']:py(s)
