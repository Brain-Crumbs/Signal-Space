import subprocess,concurrent.futures,time,pathlib
r=pathlib.Path(__file__).resolve().parent
source=r/'inputs/excited_state.bin'
jobs=[('kick_coarse',.05,.01),('kick_fine',.025,.005),('kick_timefine',.025,.0025)]
def run(job):
 n,dx,dt=job;t=time.time();subprocess.run([str(r/'evolve_kick'),str(r/'results'/n),str(source),str(dx),str(dt),'1000','.1'],check=True);return n,time.time()-t
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
 for a in ex.map(run,jobs):print(a,flush=True)
