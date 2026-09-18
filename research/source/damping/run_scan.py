from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
import json,subprocess,time,sys
ROOT=Path(__file__).resolve().parent
subprocess.run(['g++','-O3','-march=native','-std=c++17','evolve_scan.cpp','-o','evolve_scan'],check=True,cwd=ROOT)
def run(p):
 meta=json.loads(p.read_text());tag=p.stem;t=time.time()
 subprocess.run([str(ROOT/'evolve_scan'),str(ROOT/'results'/tag),str(p.with_suffix('.bin')),str(meta['dx']),str(meta['dt']),str(meta['T']),'.1'],check=True)
 return tag,round(time.time()-t,2)
ps=list((ROOT/'inputs').glob('*.json'))
if len(sys.argv)>1:ps=[p for p in ps if any(s in p.stem for s in sys.argv[1:])]
with ThreadPoolExecutor(max_workers=3) as ex:
 for r in as_completed([ex.submit(run,p) for p in ps]):print(r.result(),flush=True)
