import subprocess, concurrent.futures, pathlib, time
root=pathlib.Path(__file__).resolve().parent
jobs=[]
for om in [.90,.88,.95,.98]:
 for wr in [.5,1,2,4]:
  for nu in [.8,.9,1.]:
   name=f'scan_o{om:.2f}_w{wr:g}_n{nu:g}'
   jobs.append([str(root/'evolve'),str(root/'results'/name),str(om),str(wr),str(nu),'.05','.01','800','gauss','0'])
def run(cmd):
 t=time.time(); subprocess.run(cmd,check=True); return pathlib.Path(cmd[1]).name,round(time.time()-t,1)
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  for result in pool.map(run,jobs): print(result,flush=True)
