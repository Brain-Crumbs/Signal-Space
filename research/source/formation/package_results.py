import pathlib,zipfile,hashlib,json
R=pathlib.Path(__file__).resolve().parent
keep=[]
for p in R.iterdir():
 if p.suffix in ['.py','.cpp','.md','.json'] or p.name=='analysis_stdout.txt':keep.append(p)
keep+=list((R/'inputs').glob('*.md'))
keep+=list((R/'deliverables').glob('*.md'))+list((R/'deliverables').glob('*.png'))+list((R/'deliverables').glob('*.csv'))
keep+=list((R/'results').glob('*.csv'))+list((R/'results').glob('*.json'))
for name in ['settled_fine','readout_fine_p0.0000','readout_fine_p1.5708','readout_fine_p3.1416']:
 keep.append(R/'results'/f'{name}_snap.bin')
for name in ['scan_o0.90_w2_n0.9','fine_o0.90_w2_n0.9','settled_fine','unbound_settled_fine']:
 keep.append(R/'results'/f'{name}_final.bin')
keep=sorted(set(keep));manifest={str(p.relative_to(R)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in keep}
(R/'deliverables/MANIFEST.json').write_text(json.dumps(manifest,indent=2))
out=R/'deliverables/Signal_Space_Formation_Source.zip'
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in keep:z.write(p,str(p.relative_to(R)))
 z.write(R/'deliverables/MANIFEST.json','MANIFEST.json')
with zipfile.ZipFile(out) as z:
 bad=z.testzip();assert bad is None,bad
 print('archive_files',len(z.namelist()),'archive_MiB',round(out.stat().st_size/1024**2,2))
