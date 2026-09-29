import subprocess,concurrent.futures,pathlib,time
root=pathlib.Path(__file__).resolve().parent
jobs=[]
for w in [.5,1,2,4]:
 for nu in [.8,.9,1.]:
  for dx,dt,label in [(.05,.01,'scan'),(.025,.005,'fine')]:
   name=f'{label}_o0.90_w{w:g}_n{nu:g}'
   jobs.append([str(root/'evolve'),str(root/'results'/name),'.9',str(w),str(nu),str(dx),str(dt),'800','gauss','0'])
def run(cmd):
 t=time.time();subprocess.run(cmd,check=True);return pathlib.Path(cmd[1]).name,round(time.time()-t,1)
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  for r in pool.map(run,jobs):print(r,flush=True)
