import subprocess,concurrent.futures,pathlib,time
root=pathlib.Path(__file__).resolve().parent
source=root/'results/scan_o0.90_w2_n0.9_final.bin'
jobs=[]
def add(name,om=.9,w=2,nu=.9,dx=.05,dt=.01,T=800,mode='gauss',frac=0,extra=[]):
 jobs.append([str(root/'evolve'),str(root/'results'/name),str(om),str(w),str(nu),str(dx),str(dt),str(T),mode,str(frac)]+list(map(str,extra)))
for mode in ['exact','perturbed']:add(mode,mode=mode)
for w,nu in [(2,.9),(.5,1),(4,.9),(1,.8)]:
 for dx,dt,tag in [(.05,.005,'dt'),(.025,.005,'fine')]:add(f'refine_w{w:g}_n{nu:g}_{tag}',w=w,nu=nu,dx=dx,dt=dt)
add('long_narrow',w=.5,nu=1,T=2400)
add('long_broad',w=4,nu=.9,T=2400)
add('long_unbound098',om=.98,w=1,nu=.8,T=2400)
for ph in [0,1.5707963267948966,3.141592653589793]:add(f'readout_p{ph:.4f}',T=650,mode='readout',extra=[source,ph,60])
for frac in [0,.001,.01,.05,-.001,-.01,-.05]:add(f'neutral_{frac:g}',T=240,mode='formed',frac=frac,extra=[source])
# Prepared neutral radiation DURING formation, not a vacuum source.
for frac in [.01,-.01]:add(f'seeded_formation_{frac:g}',frac=frac)
def run(cmd):
 t=time.time();subprocess.run(cmd,check=True);return pathlib.Path(cmd[1]).name,round(time.time()-t,1)
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  for r in pool.map(run,jobs):print(r,flush=True)
