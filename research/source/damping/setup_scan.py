from pathlib import Path
import numpy as np, json
from scipy.linalg import solve_banded
from scipy.optimize import brentq
from resonance import W,profile
ROOT=Path(__file__).resolve().parent
LAM=.01
QREF=2*W*np.arctanh(2*np.sqrt(1-W*W))/LAM

def equilibrium(h,dt,qtarget=QREF):
 xp=np.arange(round(40/h)+1)*h
 def solve(w):
  wh=2*np.sin(w*dt/2)/dt
  F=profile(xp,w);F[-1]=0
  for it in range(20):
   f=F[:-1];lap=(F[2:]-2*F[1:-1]+F[:-2])/h**2
   res=np.r_[2*(F[1]-F[0])/h**2,lap]+(wh**2-1)*f+2*f**3-3*f**5
   ab=np.zeros((3,len(f)));ab[0,1:]=1/h**2;ab[0,1]=2/h**2;ab[2,:-1]=1/h**2;ab[1]=-2/h**2+wh**2-1+6*f*f-15*f**4
   change=solve_banded((1,1),ab,-res);F[:-1]+=change
   if max(abs(change))<2e-14:break
  q=2*np.cos(w*dt/2)*wh*h*(2*np.sum(F**2)-F[0]**2)/LAM
  return q,F,float(max(abs(res)))
 w=brentq(lambda w:solve(w)[0]-qtarget,W-.001,W+.001,xtol=1e-14)
 q,F,res=solve(w)
 x=np.r_[-xp[:0:-1],xp];F=np.r_[F[:0:-1],F]
 return x,F,w,dict(dx=h,dt=dt,omega=w,Q=q,stationary_residual=res)

def make(b,h,dt,T,tag):
 xx,F,w,meta=equilibrium(h,dt)
 L=T+120;N=2*round(L/h)+1;x=(np.arange(N)-N//2)*h
 f=np.interp(x,xx,F,left=0,right=0)
 phi=np.cos(w*dt/2)*f+0j;vel=-1j*(2*np.sin(w*dt/2)/dt)*f
 mode=np.load(ROOT/'results/resonance_mode.npz');xm=mode['x'];Om=complex(mode['Omega'])
 def interp(z):
  return np.interp(abs(x),xm,z.real,right=0)+1j*np.interp(abs(x),xm,z.imag,right=0)
 u=interp(mode['u']);v=interp(mode['v']);tap=np.where(abs(x)<=16,1,np.where(abs(x)>=22,0,.5*(1+np.cos(np.pi*(abs(x)-16)/6))))
 dphi=(u+v.conj())*tap;dvel=(-1j*(w+Om)*u-1j*(w-Om.conjugate())*v.conj())*tap
 phi+=b*dphi;vel+=b*dvel
 Qraw=-2*h/LAM*np.imag(np.vdot(phi,vel));c=(QREF-Qraw)*LAM/(2*h*np.vdot(phi,phi).real);vel-=1j*c*phi
 out=ROOT/'inputs';out.mkdir(exist_ok=True)
 with open(out/f'{tag}.bin','wb') as fd:
  np.array([N],np.int32).tofile(fd);np.array([h]).tofile(fd)
  np.array([phi.real,phi.imag,vel.real,vel.imag]).tofile(fd)
 meta.update(b=b,T=T,L=L,charge_before_correction=float(Qraw),velocity_charge_correction=float(c),Q_initial=float(-2*h/LAM*np.imag(np.vdot(phi,vel))),Q_target=QREF)
 (out/f'{tag}.json').write_text(json.dumps(meta,indent=2));return meta

if __name__=='__main__':
 out=[]
 for b in [0,.005,.01,.02,.04,.06,.09]:
  out.append(make(b,.05,.01,700,f'b{b:g}_coarse'))
 for b in [.0025,.005,.01,.02,.04,.09]:out.append(make(b,.025,.005,700,f'b{b:g}_fine'))
 out.append(make(.01,.025,.0025,700,'b0.01_timefine'))
 out.append(make(.01,.0125,.0025,700,'b0.01_superfine'))
 (ROOT/'results/preparations.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
