import subprocess,concurrent.futures,pathlib,time
root=pathlib.Path(__file__).resolve().parent
jobs=[]
for name,w,nu,T in [('settled',2,.9,1600),('unbound_settled',2,1.3,2400)]:
 for dx,dt,tag in [(.05,.01,'coarse'),(.025,.005,'fine')]:
  jobs.append([str(root/'evolve'),str(root/'results'/f'{name}_{tag}'),'.9',str(w),str(nu),str(dx),str(dt),str(T),'gauss','0'])
def run(cmd):
 t=time.time();subprocess.run(cmd,check=True);return pathlib.Path(cmd[1]).name,round(time.time()-t,1)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 for r in pool.map(run,jobs):print(r,flush=True)
