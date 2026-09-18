import json,sys
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares,brentq
from setup_scan import QREF,LAM
ROOT=Path(__file__).resolve().parent
NS=np.arange(-3,4)
def mass(q):
 w=brentq(lambda w:2*w*np.arctanh(2*np.sqrt(1-w*w))/LAM-q,np.sqrt(.75)+1e-9,.999999,xtol=1e-13)
 r=np.arctanh(2*np.sqrt(1-w*w));return ((w*w+.75)*r+.25*np.tanh(r))/LAM,w

def load(tag):
 with open(ROOT/'results'/f'{tag}_probes.bin','rb') as f:
  n=np.fromfile(f,np.int32,1)[0];x=np.fromfile(f,float,n);r=np.fromfile(f,float).reshape(-1,1+8*n)
 return r[:,0],x,r[:,1:].reshape(-1,n,8)

def analyze(tag,lo=200,hi=700):
 meta=json.loads((ROOT/'inputs'/f'{tag}.json').read_text());t,x,r=load(tag);sel=(t>=lo)&(t<=hi);t=t[sel];r=r[sel];tc=(lo+hi)/2;tau=t-tc;sw=np.sqrt(np.hanning(len(t)))
 phi=r[:,:,0]+1j*r[:,:,1];vel=r[:,:,2]+1j*r[:,:,3];grad=r[:,:,4]+1j*r[:,:,5]
 def B(p):return np.exp(-1j*(tau[:,None]*(p[0]+NS*p[1])+.5*tau[:,None]**2*1e-6*(p[2]+NS*p[3])))
 def residual(p):
  bb=B(p)*sw[:,None];coef=np.linalg.lstsq(bb,phi[:,0]*sw,rcond=None)[0];rr=(bb@coef-phi[:,0]*sw)/np.sqrt(len(t));return np.r_[rr.real,rr.imag]
 fit=least_squares(residual,[meta['omega']-.004*(meta['b']/.09)**2,1.7285,0,0],x_scale=[.001,.001,.01,.01],diff_step=1e-4,ftol=1e-12,gtol=1e-12,xtol=1e-12,max_nfev=60)
 p=fit.x;bb=B(p);design=np.c_[bb,bb*tau[:,None]/250];H=np.linalg.pinv(design*sw[:,None])*sw[None,:]
 CC=H@phi;VV=H@vel;GG=H@grad;C=CC[:len(NS)];V=VV[:len(NS)];G=GG[:len(NS)];sig=p[0]+NS*p[1]
 out=dict(tag=tag,b_input=meta['b'],dx=meta['dx'],dt=meta['dt'],lo=lo,hi=hi,carrier=p[0],Omega=p[1],chirps=(p[2:]*1e-6).tolist(),b_measured=abs(C[2,0]),center_fit_residual=float(np.linalg.norm(fit.fun)/np.sqrt(np.mean(abs(phi[:,0]*sw)**2))),lines=[])
 out['amplitude_gamma_fit']=float(-np.real(CC[len(NS)+2,0]/C[2,0])/250)
 for i,n in enumerate(NS):
  pp=-4/LAM*np.real(V[i].conj()*G[i]);jj=4/LAM*np.imag(C[i].conj()*G[i])
  out['lines'].append(dict(n=int(n),sigma=sig[i],power_both=pp.tolist(),charge_both=jj.tolist(),center_amplitude=float(abs(C[i,0]))))
 led=np.genfromtxt(ROOT/'results'/f'{tag}_ledger.csv',delimiter=',',names=True);q=led['Q'];e=led['E'];out['Q_rel_drift']=float(max(abs(q-q[0]))/q[0]);out['E_rel_drift']=float(max(abs(e-e[0]))/e[0])
 ls=(led['t']>=lo)&(led['t']<=hi);tl=led['t'][ls];ta=tl-tc;weight=np.hanning(len(ta));
 # Remove resolved fast oscillatory finite-step contributions while estimating secular slope.
 mat=np.c_[np.ones(len(ta)),ta,*[f(n*(p[1]*ta+.5*p[3]*1e-6*ta*ta)) for n in range(1,7) for f in (np.sin,np.cos)]]
 norm=mat*np.sqrt(weight)[:,None]
 out['core']=[]
 for width in [20,40,60]:
  qe=led[f'Q{width}'][ls];ee=led[f'E{width}'][ls];mm=np.array([mass(a)[0] for a in qe]);de=ee-mm
  beta=np.linalg.lstsq(norm,de*np.sqrt(weight),rcond=None)[0];omegaq=mass(np.average(qe,weights=weight))[1]
  oi=int(np.argmin(abs(x-width)));power=sum(l['power_both'][oi] for l in out['lines'] if abs(l['sigma'])>1);charge=sum(l['charge_both'][oi] for l in out['lines'] if abs(l['sigma'])>1)
  # Direct Hann-weighted flux at the same detector, including unresolved transients.
  directP=np.average(-4/LAM*np.real(vel[:,oi].conj()*grad[:,oi]),weights=sw**2);directJ=np.average(4/LAM*np.imag(phi[:,oi].conj()*grad[:,oi]),weights=sw**2)
  out['core'].append(dict(width=width,charge=float(np.average(qe,weights=weight)),omega_Q=omegaq,excess_mean=float(beta[0]),excess_loss_fit=float(-beta[1]),harmonic_power=float(power),harmonic_charge=float(charge),harmonic_excess_loss=float(power-omegaq*charge),direct_power=float(directP),direct_charge=float(directJ),direct_excess_loss=float(directP-omegaq*directJ),fit_rms=float(np.sqrt(np.average((de-mat@beta)**2,weights=weight)))))
  corrections=json.loads((ROOT/'results/ground_correction.json').read_text())
 for c in out['core']:
  corr=next(a for a in corrections if a['dx']==meta['dx'] and a['dt']==meta['dt'] and a['width']==c['width'])
  offset=corr['continuum_mass_offset']+corr['offset_derivative']*(c['charge']-corr['charge'])
  c['ground_offset']=offset;c['excess_calibrated']=c['excess_mean']-offset
  c['harmonic_energy_decay_rate']=c['harmonic_excess_loss']/c['excess_calibrated']
 out['balance_E_max']=float(max(abs(led['E20']+led['intP20']-led['E20'][0])));out['balance_Q_max']=float(max(abs(led['Q20']+led['intJ20']-led['Q20'][0])))
 np.savez_compressed(ROOT/'results'/f'{tag}_{lo}_{hi}_fit.npz',x=x,n=NS,sigma=sig,C=C,V=V,G=G,fit=p,CC=CC)
 (ROOT/'results'/f'{tag}_{lo}_{hi}_analysis.json').write_text(json.dumps(out,indent=2))
 c=out['core'][0];print(tag,'b',out['b_measured'],'w,Om',p[:2],'res',out['center_fit_residual'],'P',c['harmonic_power'],'rate',c['harmonic_excess_loss']/c['excess_mean'],'decay fit',c['excess_loss_fit']/c['excess_mean'],'gammafit',out['amplitude_gamma_fit'],flush=True)
 return out
if __name__=='__main__':
 ps=sorted((ROOT/'inputs').glob('*.json'))
 if len(sys.argv)>1:ps=[p for p in ps if any(s in p.stem for s in sys.argv[1:])]
 out=[analyze(p.stem) for p in ps if json.loads(p.read_text())['b']>0]
 (ROOT/'results/scan_analysis.json').write_text(json.dumps(out,indent=2))
