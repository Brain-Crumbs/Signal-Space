import subprocess,concurrent.futures,pathlib,time
root=pathlib.Path(__file__).resolve().parent
source=root/'results/fine_o0.90_w2_n0.9_final.bin';jobs=[]
for ph in [0,1.5707963267948966,3.141592653589793]:
 jobs.append([str(root/'evolve'),str(root/'results'/f'readout_fine_p{ph:.4f}'),'.9','2','.9','.025','.005','650','readout','0',str(source),str(ph),'60'])
for frac in [.05,-.05]:
 jobs.append([str(root/'evolve'),str(root/'results'/f'neutral_fine_{frac:g}'),'.9','2','.9','.025','.005','240','formed',str(frac),str(source)])
def run(cmd):
 t=time.time();subprocess.run(cmd,check=True);return pathlib.Path(cmd[1]).name,round(time.time()-t,1)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for r in pool.map(run,jobs):print(r,flush=True)
