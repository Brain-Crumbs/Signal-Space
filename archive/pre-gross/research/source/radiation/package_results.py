import pathlib,zipfile,json,hashlib,numpy as np
R=pathlib.Path(__file__).resolve().parent
names=['evolve_spectrum.cpp','analyze_spectrum.py','diagnostics.py','make_figure.py','make_report.py','run_all.py','run_kick.py','package_results.py','README.md','environment.json']
files=[R/n for n in names]+list((R/'inputs').iterdir())
for pattern in ['kick_*_probes.bin','kick_*_ledger.csv','kick_*_spectrum.json','kick_*_profiles.npz','kick_*_diagnostics.npz']:
 files+=list((R/'results').glob(pattern))
files.append(R/'results/diagnostics.json');files+=list((R/'deliverables').glob('*.md'))+list((R/'deliverables').glob('*.png'))
for name in ['kick_coarse','kick_fine','kick_timefine']:
 h=np.genfromtxt(R/'results'/f'{name}_ledger.csv',names=True,delimiter=',');assert h['t'][-1]==1000 and np.isfinite(h['E']).all()
 with open(R/'results'/f'{name}_probes.bin','rb') as f:
  n=np.fromfile(f,np.int32,1)[0];x=np.fromfile(f,float,n);a=np.fromfile(f,float);assert a.size%(1+8*n)==0;assert a.reshape(-1,1+8*n)[-1,0]==1000
report=(R/'deliverables/Signal_Space_Charged_Clock_Radiation_Milestone.md').read_text();assert '%%' not in report and report.count('$$')%2==0
files=sorted(set(files));manifest={str(p.relative_to(R)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files}
output=R/'deliverables/Signal_Space_Radiation_Source.zip'
with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,str(p.relative_to(R)))
 z.writestr('MANIFEST.json',json.dumps(manifest,indent=2))
with zipfile.ZipFile(output) as z:assert z.testzip() is None;print('Verified files',len(z.namelist()),'archive MiB',round(output.stat().st_size/1024**2,2))
