from pathlib import Path
import re, subprocess
ROOT=Path(__file__).resolve().parent
NAME='Signal_Space_Part_II_Signal_States_Lorentz_Cones_and_Operational_Clocks'
text=(ROOT/'metadata.yaml').read_text()+'\n'+'\n'.join(p.read_text() for p in sorted((ROOT/'sections').glob('*.md')))
tags=re.findall(r'\\tag\{([^}]+)\}',text)
assert len(tags)==len(set(tags)), 'Duplicate equation identifiers'
assert text.count('$$')%2==0, 'Unpaired display math delimiter'
assert not re.search(r'\b(TODO|TBD|FIXME)\b',text)
(ROOT/(NAME+'.md')).write_text(text)
subprocess.run(['pandoc',NAME+'.md','--standalone','--pdf-engine=xelatex','-V','mainfont=Latin Modern Roman','-V','monofont=Latin Modern Mono','-o',NAME+'.pdf'],cwd=ROOT,check=True)
print(f'Built {NAME}: {len(text.split())} whitespace-separated tokens, {len(tags)} labeled equations.')
