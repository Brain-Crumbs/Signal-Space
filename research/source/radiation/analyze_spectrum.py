import pathlib,json,sys,numpy as np
from scipy.optimize import least_squares
ROOT=pathlib.Path(__file__).resolve().parent
NS=np.arange(-4,5)

def probes(name):
 with open(ROOT/'results'/f'{name}_probes.bin','rb') as f:
  n=np.fromfile(f,np.int32,1)[0];x=np.fromfile(f,float,n);r=np.fromfile(f,float).reshape(-1,1+8*n)
 return r[:,0],x,r[:,1:].reshape(-1,n,8)

def field(name):
 with open(ROOT/'results'/f'{name}_field.bin','rb') as f:n=np.fromfile(f,np.int32,1)[0];h=np.fromfile(f,float,1)[0]
 a=np.memmap(ROOT/'results'/f'{name}_field.bin',dtype='float64',offset=12,mode='r').reshape(-1,1+2*n)
 return a[:,0],(np.arange(n)-n//2)*h,a[:,1:1+n],a[:,1+n:]

def design(t,p,tc):
 tau=t-tc;theta=p[0]*tau+.5*p[2]*1e-6*tau*tau;phase=p[1]*tau+.5*p[3]*1e-6*tau*tau
 e=np.exp(-1j*(theta[:,None]+phase[:,None]*NS));return np.concatenate([e,e*(tau/400)[:,None]],axis=1)

def analysis(name,dx,dt,lo=200,hi=1000):
 t,px,rr=probes(name);sel=(t>=lo)&(t<=hi);tt=t[sel];tc=(lo+hi)/2;f0=rr[sel,5,0]+1j*rr[sel,5,1];w=np.sqrt(np.hanning(len(tt)))
 def residual(p):
  B=design(tt,p,tc)[:,:len(NS)]*w[:,None];coef=np.linalg.lstsq(B,f0*w,rcond=None)[0];d=(B@coef-f0*w)/np.sqrt(len(tt));return np.r_[d.real,d.imag]
 opt=least_squares(residual,[.89992,1.728,0,0],diff_step=1e-5,xtol=1e-12,ftol=1e-12,gtol=1e-12,x_scale=[.001,.001,.01,.01],max_nfev=80)
 p=opt.x;sig=p[0]+NS*p[1];B=design(tt,p,tc);H=np.linalg.pinv(B*w[:,None])*w[None,:]
 vals=rr[sel];C=H@(vals[:,:,0]+1j*vals[:,:,1]);V=H@(vals[:,:,2]+1j*vals[:,:,3]);G=H@(vals[:,:,4]+1j*vals[:,:,5]);C=C[:len(NS)];V=V[:len(NS)];G=G[:len(NS)]
 tf,x,u,z=field(name);take=(tf>=lo)&(tf<=hi);tf=np.array(tf[take]);wf=np.sqrt(np.hanning(len(tf)));BF=design(tf,p,tc);HF=np.linalg.pinv(BF*wf[:,None])*wf[None,:]
 A=np.zeros((len(NS),len(x)),complex);S3=A.copy();S5=A.copy()
 for j in range(0,len(x),64):
  phi=np.array(u[take,j:j+64])+1j*np.array(z[take,j:j+64]);s=abs(phi)**2;A[:,j:j+64]=(HF@phi)[:len(NS)];S3[:,j:j+64]=(HF@(2*s*phi))[:len(NS)];S5[:,j:j+64]=(HF@(-3*s*s*phi))[:len(NS)]
 source=S3+S5
 result={'name':name,'dx':dx,'dt':dt,'window':[lo,hi],'center_time':tc,'carrier':p[0],'modulation':p[1],'carrier_chirp':p[2]*1e-6,'modulation_chirp':p[3]*1e-6,'center_fit_relative_rms':float(np.linalg.norm(opt.fun)/np.sqrt(np.mean(abs(f0*w)**2))),'lines':[]}
 for i,n in enumerate(NS):
  sigma=sig[i];st=2/dt*np.sin(sigma*dt/2);open_=abs(st)>1
  line={'n':int(n),'sigma':float(sigma),'open':bool(open_),'core_norm2':float(np.trapezoid(abs(A[i,abs(x)<=12])**2,x[abs(x)<=12])),'core_peak_amplitude':float(np.max(abs(A[i,abs(x)<=12])))}
  if open_:
   k=2/dx*np.arcsin(dx/2*np.sqrt(st*st-1));sg=np.sign(sigma);kd=np.sin(k*dx)/dx
   proj=np.exp(-1j*sg*k*x);I=np.trapezoid(source[i]*proj,x);I3=np.trapezoid(S3[i]*proj,x);I5=np.trapezoid(S5[i]*proj,x);absint=np.trapezoid(abs(source[i]),x);pred=-I/(2j*sg*kd)
   line.update(k=float(k),source_integral_abs=float(abs(I)),source_abs_integral=float(absint),coherence_ratio=float(abs(I)/absint),coherence_ratio3=float(abs(I3)/np.trapezoid(abs(S3[i]),x)),coherence_ratio5=float(abs(I5)/np.trapezoid(abs(S5[i]),x)),cubic_quintic_cancel=float(abs(I)/(abs(I3)+abs(I5))),predicted_right_amplitude=float(abs(pred)))
   dets=[]
   for j in [6,7,8,9,10]:
    a=C[i,j]/np.cos(sigma*dt/2);g=G[i,j]/np.cos(sigma*dt/2);out=.5*(a+g/(1j*sg*kd));inc=.5*(a-g/(1j*sg*kd));power=-2/.01*np.real(np.conj(V[i,j])*G[i,j]);charge=2/.01*np.imag(np.conj(C[i,j])*G[i,j]);phaseout=out*np.exp(-1j*sg*k*px[j]);
    dets.append({'x':float(px[j]),'out_amplitude':float(abs(out)),'in_amplitude':float(abs(inc)),'power_right':float(power),'charge_right':float(charge),'predicted_ratio':float(abs(pred)/abs(out)),'phase_difference':float(np.angle(pred/phaseout))})
   line['detectors']=dets
  else:
   line['kappa']=float(2/dx*np.arcsinh(dx/2*np.sqrt(1-st*st)))
  result['lines'].append(line)
 # Dense averaged power and charge currents, not a harmonic-only estimate.
 dense=[]
 for j in [6,7,8,9,10]:
  v=vals[:,j,2]+1j*vals[:,j,3];g=vals[:,j,4]+1j*vals[:,j,5];phi=vals[:,j,0]+1j*vals[:,j,1];P=-2/.01*np.real(np.conj(v)*g);J=2/.01*np.imag(np.conj(phi)*g)
  dense.append({'x':float(px[j]),'mean_power_both_sides':float(2*np.mean(P)),'mean_charge_both_sides':float(2*np.mean(J))})
 result['total_flux']=dense
 tag=f'{name}_{lo}_{hi}';(ROOT/'results'/f'{tag}_spectrum.json').write_text(json.dumps(result,indent=2));np.savez_compressed(ROOT/'results'/f'{tag}_profiles.npz',x=x,n=NS,sigma=sig,A=A,S3=S3,S5=S5,probe_x=px,C=C,V=V,G=G,fit=p)
 print(name,lo,hi,'frequencies',p,'relative residual',result['center_fit_relative_rms'])
 for a in result['lines']:
  if a['n'] not in [-2,-1,0,1,2]:continue
  print(a['n'],a['sigma'],'norm',a['core_norm2'],'peak',a['core_peak_amplitude'], 'coherence',a.get('coherence_ratio'),'P_both',2*a['detectors'][2]['power_right'] if a['open'] else 'closed','pred_ratio',a['detectors'][2]['predicted_ratio'] if a['open'] else '-')
 return result
if __name__=='__main__':
 name=sys.argv[1] if len(sys.argv)>1 else 'fine';dx=.05 if 'coarse' in name else .025;dt=.0025 if 'timefine' in name else dx*.2
 analysis(name,dx,dt,*map(float,sys.argv[2:]))
