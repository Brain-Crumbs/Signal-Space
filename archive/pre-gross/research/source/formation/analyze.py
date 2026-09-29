import json, pathlib, numpy as np
from scipy.optimize import brentq,minimize_scalar,least_squares
from scipy.integrate import cumulative_trapezoid
ROOT=pathlib.Path(__file__).resolve().parent
LAM=.01

def branch(o):
 r=np.arctanh(2*np.sqrt(1-o*o));q=2*o*r/LAM;e=((o*o+.75)*r+.25*np.tanh(r))/LAM
 return q,e

def oq(q):
 return brentq(lambda o:branch(o)[0]-abs(q),np.sqrt(.75)+1e-12,1-1e-12)

def profile(o,x):
 k=np.sqrt(1-o*o);return np.sqrt(2*k*k/(1+np.sqrt(1-4*k*k)*np.cosh(2*k*x)))

def snapshots(path):
 with open(path,'rb') as f:
  n=int(np.fromfile(f,np.int32,1)[0]); dx=np.fromfile(f,np.float64,1)[0];data=np.fromfile(f,np.float64).reshape(-1,4*n+1)
 return (np.arange(n)-n//2)*dx,data[:,0],data[:,1:].reshape(-1,4,n)

def analyze(prefix):
 meta=json.loads(pathlib.Path(str(prefix)+'_meta.json').read_text());h=np.genfromtxt(str(prefix)+'.csv',names=True,delimiter=',');t=h['t'];fit_span=min(800,t[-1]/2);late=t>=max(0,t[-1]-fit_span);half=t>=max(0,t[-1]-200)
 result={'name':prefix.name,**meta,'fit_span':fit_span,'E0':float(h['E'][0]),'Q0':float(h['Q'][0]),'E0_minus_Q0':float(h['E'][0]-h['Q'][0]),'energy_drift':float(np.max(np.abs(h['E']/h['E'][0]-1))),'charge_drift':float(np.max(np.abs(h['Q']/h['Q'][0]-1))),'P0':float(h['P'][0]),'Pfinal':float(h['P'][-1]),'momentum_drift_over_E':float(np.max(np.abs(h['P']-h['P'][0]))/h['E'][0]),'Ea0':float(h['Ea'][0]),'Eafinal':float(h['Ea'][-1])}
 for W in [20,30,40]:
  q=h[f'Q{W}'];E=h[f'E{W}'];ph=np.unwrap(h[f'phase{W}']);coef=np.polyfit(t[late],ph[late],1);res=ph[late]-np.polyval(coef,t[late]);qmean=np.mean(q[late]);om=oq(qmean)
  result[f'window{W}']={'Q_mean':float(qmean),'Q_final':float(q[-1]),'Q_range':float(np.ptp(q[late])),'E_mean':float(np.mean(E[late])),'E_final':float(E[-1]),'omega_Q':om,'omega_phase':float(-coef[0]),'phase_rms':float(np.std(res)),'phase_max':float(np.max(np.abs(res))),'R_mean':float(np.mean(h[f'R{W}'][late])),'Q_late_change':float(q[-1]-q[np.searchsorted(t,max(0,t[-1]-200))])}
 F=h['fluxEcum'] if 'fluxEcum' in h.dtype.names else cumulative_trapezoid(h['fluxE'],t,initial=0);Fq=h['fluxQcum'] if 'fluxQcum' in h.dtype.names else cumulative_trapezoid(h['fluxQ'],t,initial=0)
 result['flux']={'energy_out':float(F[-1]),'charge_out':float(Fq[-1]),'energy_balance_relative':float(np.max(abs(h['E30']+F-h['E30'][0]))/h['E'][0]),'charge_balance_relative':float(np.max(abs(h['Q30']+Fq-h['Q30'][0]))/h['Q'][0]),'energy_exterior_final':float(h['E'][-1]-h['E30'][-1]),'charge_exterior_final':float(h['Q'][-1]-h['Q30'][-1])}
 if meta['mode']=='readout':
  for W in [20,30,40]:
   result[f'window{W}']={k:v for k,v in result[f'window{W}'].items() if not k.startswith(('omega','phase'))}
  result['profile_fit']={'not_applicable':'Two-object collision; no single-clock fit is interpreted.'};return result
 x,ts,raw=snapshots(str(prefix)+'_snap.bin');sel=(abs(x)<=12);xs=x[sel];fits=[]
 for time,f in zip(ts,raw):
  if time<max(0,ts[-1]-fit_span):continue
  phi=f[0,sel]+1j*f[1,sel]
  def err(o):
   ref=profile(o,xs);phase=np.angle(np.vdot(ref,phi));return np.sum(abs(phi-np.exp(1j*phase)*ref)**2)/np.sum(abs(phi)**2)
  opt=minimize_scalar(err,bounds=(np.sqrt(.75)+1e-8,.999999),method='bounded',options={'xatol':1e-12});o=opt.x
  center=0.
  if meta['mode'] in ['perturbed','formed']:
   init=[o,float(np.sum(xs*abs(phi)**2)/np.sum(abs(phi)**2)),float(np.angle(np.vdot(profile(o,xs),phi)))]
   def resid(p):
    a=(phi-profile(p[0],xs-p[1])*np.exp(1j*p[2]))/np.sqrt(np.sum(abs(phi)**2));return np.r_[a.real,a.imag]
   fit=least_squares(resid,init,bounds=([np.sqrt(.75)+1e-8,-10,-np.inf],[.999999,10,np.inf]),xtol=1e-11,ftol=1e-11,gtol=1e-11);o,center,phase=fit.x;opt.fun=np.sum(fit.fun**2)
  ref=profile(o,xs);rad=np.sqrt(np.sum(xs*xs*ref**2)/np.sum(ref**2));fits.append([float(time),float(o),float(np.sqrt(opt.fun)),float(rad),float(center)])
 a=np.array(fits);result['profile_fit']={'omega_mean':float(a[:,1].mean()),'omega_std':float(a[:,1].std()),'relative_L2_mean':float(a[:,2].mean()),'relative_L2_max':float(a[:,2].max()),'R_mean':float(a[:,3].mean()),'R_std':float(a[:,3].std()),'center_final':float(a[-1,4]),'center_speed':float(np.polyfit(a[:,0],a[:,4],1)[0]),'late_samples':fits}
 return result

if __name__=='__main__':
 import sys
 names=sys.argv[1:] or [p.name[:-10] for p in (ROOT/'results').glob('*_meta.json')]
 rr=[]
 for name in names:
  r=analyze(ROOT/'results'/name);rr.append(r)
 (ROOT/'results'/'analysis.json').write_text(json.dumps(rr,indent=2))
 for r in rr:
  if r['mode']=='readout':
   print(r['name'],'two-object collision; see conservation and local intensity histories');continue
  w=r['window20'];f=r['profile_fit'];print(r['name'],f"E-Q={r['E0_minus_Q0']:.3f} Qc={w['Q_mean']:.3f} om={w['omega_phase']:.7f} res={f['relative_L2_mean']:.4f} phase={w['phase_rms']:.4f} dE={r['energy_drift']:.2g} flux={r['flux']['energy_balance_relative']:.2g}")
