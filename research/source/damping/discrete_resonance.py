import numpy as np,json
from scipy.optimize import root
from setup_scan import equilibrium

def calc(h,dt,R=24):
 x,F,w,meta=equilibrium(h,dt);n=round(R/h);s=np.interp(np.arange(n+1)*h,x,F)**2;A=1-4*s+9*s*s;B=-2*s+6*s*s
 def residual(z):
  om=z[0]+1j*z[1];sp=2*np.sin((w+om)*dt/2)/dt;sm=2*np.sin((w-om)*dt/2)/dt
  k=2/h*np.arcsin(h/2*np.sqrt(sp**2-1+0j));kap=2/h*np.arcsinh(h/2*np.sqrt(1-sm**2+0j))
  curr=np.eye(2,dtype=complex);nxt=np.diag([np.exp(1j*k*h),np.exp(-kap*h)])
  for j in range(n,0,-1):
   prev=np.array([[2+h*h*(A[j]-sp**2),h*h*B[j]],[h*h*B[j],2+h*h*(A[j]-sm**2)]])@curr-nxt
   nxt,curr=curr,prev
  D=nxt-np.array([[1+.5*h*h*(A[0]-sp**2),.5*h*h*B[0]],[.5*h*h*B[0],1+.5*h*h*(A[0]-sm**2)]])@curr
  D/=np.linalg.norm(curr,axis=0)[None,:]
  det=np.linalg.det(D)/h**2;return [det.real,det.imag]
 z=root(residual,[1.728514,-1.43e-6],tol=1e-9)
 r=dict(dx=h,dt=dt,w=w,Omega_real=z.x[0],Omega_imag=z.x[1],residual=float(np.linalg.norm(residual(z.x))),success=bool(z.success));print(r,flush=True);return r
if __name__=='__main__':
 out=[calc(h,dt) for h,dt in [(.05,.01),(.025,.005),(.025,.0025),(.0125,.0025)]]
 open('results/discrete_resonance.json','w').write(json.dumps(out,indent=2))
