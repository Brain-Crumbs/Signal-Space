import numpy as np,json
from pathlib import Path
from setup_scan import equilibrium,LAM,QREF

def energy(q,h,dt,width=20):
 x,F,w,_=equilibrium(h,dt,q)
 p=np.cos(w*dt/2)*F;vel=2*np.sin(w*dt/2)/dt*F;s=p*p
 bond=np.diff(p)**2/h**2
 density=vel**2+s-s*s+s*s*s
 density[:-1]+=.5*bond;density[1:]+=.5*bond
 mask=abs(x)<=width+h/4
 return float(h*np.sum(density[mask])/LAM),float(2*h/LAM*np.sum((p*vel)[mask]))
if __name__=='__main__':
 from analyze_scan import mass
 out=[]
 for h,dt in [(.05,.01),(.025,.005),(.025,.0025),(.0125,.0025)]:
  for width in [20,40,60]:
   e,q=energy(QREF,h,dt,width);eps=.01;ep,qp=energy(QREF+eps,h,dt,width);em,qm=energy(QREF-eps,h,dt,width)
   corr=e-mass(q)[0];der=(ep-mass(qp)[0]-em+mass(qm)[0])/(qp-qm)
   out.append(dict(dx=h,dt=dt,width=width,charge=q,energy=e,continuum_mass_offset=corr,offset_derivative=der))
 Path('results/ground_correction.json').write_text(json.dumps(out,indent=2));print(out)
