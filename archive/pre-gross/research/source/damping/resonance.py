import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import root
import json
from pathlib import Path
W=.9034743879157499

def profile(x,w=W):
 return np.sqrt(2*(1-w*w)/(1+np.sqrt(4*w*w-3)*np.cosh(2*np.sqrt(1-w*w)*x)))

def shoot(om,w=W,R=20,tol=2e-11,dense=False):
 k=np.sqrt((w+om)**2-1+0j); kap=np.sqrt(1-(w-om)**2+0j)
 init=np.array([[1,0],[1j*k,0],[0,1],[0,-kap]],complex)
 def fun(x,yy):
  y=yy.reshape(4,2);f=profile(x,w);s=f*f;A=1-4*s+9*s*s;B=-2*s+6*s*s
  return np.array([y[1],(A-(w+om)**2)*y[0]+B*y[2],y[3],B*y[0]+(A-(w-om)**2)*y[2]]).ravel()
 sol=solve_ivp(fun,(R,0),init.ravel(),method='DOP853',rtol=tol,atol=tol*.01,dense_output=dense)
 if not sol.success:raise RuntimeError(sol.message)
 Y=sol.y[:,-1].reshape(4,2);D=Y[[1,3],:];D=D/np.linalg.norm(Y,axis=0)[None,:]
 return np.linalg.det(D),sol,Y

def pole(w=W,R=20,tol=2e-11,guess=1.727-1e-6j):
 def fun(p):
  a=shoot(p[0]+1j*p[1],w,R,tol)[0];return [a.real,a.imag]
 z=root(fun,[guess.real,guess.imag],tol=1e-10)
 om=z.x[0]+1j*z.x[1];err=np.linalg.norm(fun(z.x))
 if not z.success or err>1e-8:raise RuntimeError(str(z))
 return dict(w=w,R=R,tol=tol,Omega_real=float(om.real),Omega_imag=float(om.imag),det_residual=float(err),root_success=bool(z.success))

if __name__=='__main__':
 out=[]
 for R,tol in [(16,2e-10),(20,2e-10),(24,2e-10),(20,2e-12),(24,2e-12)]:
  r=pole(R=R,tol=tol);out.append(r);print(r,flush=True)
 Path('results/resonance_checks.json').write_text(json.dumps(out,indent=2))
 r=out[-1];om=r['Omega_real']+1j*r['Omega_imag'];_,sol,Y=shoot(om,R=r['R'],tol=r['tol'],dense=True)
 D=Y[[1,3],:];a=np.array([-D[0,1],D[0,0]]);a=a/(Y[2]@a)
 x=np.linspace(0,r['R'],2401);yy=np.einsum('ijk,j->ik',sol.sol(x).reshape(4,2,-1),a)
 print('origin',yy[:,0], 'outer',yy[:,-1]);np.savez('results/resonance_mode.npz',x=x,u=yy[0],du=yy[1],v=yy[2],dv=yy[3],omega=W,Omega=om)
