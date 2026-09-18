from pathlib import Path
import json,numpy as np
from resonance import W,profile
ROOT=Path(__file__).resolve().parent
rows=sorted([json.loads(p.read_text()) for p in (ROOT/'results').glob('*_200_700_analysis.json')],key=lambda r:(r['dx'],r['dt'],r['b_input']))
small=sorted([r for r in rows if r['dx']==.025 and r['dt']==.005 and r['b_input']<=.02],key=lambda r:r['b_measured'])
b=np.array([r['b_measured'] for r in small]);slopes={}
for n in [1,-2,2]:
 power=np.array([next(l for l in r['lines'] if l['n']==n)['power_both'][7] for r in small])
 slopes[str(n)]=dict(exponent=float(np.polyfit(np.log(b),np.log(power),1)[0]),b=b.tolist(),power=power.tolist(),coefficient=(power/b**(2 if n==1 else 4)).tolist())
z=np.load(ROOT/'results/resonance_mode.npz');x=z['x'];u=z['u'];v=z['v'];w=float(z['omega']);om=complex(z['Omega']);s=profile(x)**2;A=1-4*s+9*s*s;B=-2*s+6*s*s
K2=2/.01*np.trapezoid((abs(om)**2+A-w*w)*(abs(u)**2+abs(v)**2)+abs(z['du'])**2+abs(z['dv'])**2+2*B*np.real(u*v.conj()),x)
k=np.sqrt((w+om.real)**2-1);P=4/.01*(w+om.real)*k*abs(u[-1])**2;J=P/(w+om.real)
r=np.load(ROOT/'inputs/parent_radiation_profiles.npz');xr=r['x'];mask=(xr>=0)&(xr<=12);xx=xr[mask];vr=np.interp(xx,x,v.real)+1j*np.interp(xx,x,-v.imag);a=r['A'][3,mask]
inner=lambda a,b:np.trapezoid(a.conj()*b,xx)
c=inner(vr,a)/inner(vr,vr);overlap=abs(inner(vr,a))/np.sqrt(inner(vr,vr).real*inner(a,a).real)
lin=dict(omega=w,Omega_real=om.real,Omega_imag=om.imag,energy_decay_rate=-2*om.imag,amplitude_efold=-1/om.imag,energy_efold=-1/(2*om.imag),energy_half_time=-np.log(2)/(2*om.imag),energy_efold_carrier_cycles=-w/(4*np.pi*om.imag),K2_coefficient=float(K2),power_coefficient=float(P),excess_loss_coefficient=float(P-w*J),flux_over_energy=float((P-w*J)/K2),parent_mode_overlap=float(overlap),parent_shape_residual=float(np.sqrt(inner(a-c*vr,a-c*vr).real/inner(a,a).real)),parent_fitted_mode_amplitude=float(abs(c)),parent_frequency=float(r['fit'][1]),parent_frequency_relative_difference=float((om.real-r['fit'][1])/om.real))
# A null control checks the exact discrete rotating background.
led=np.genfromtxt(ROOT/'results/b0_coarse_ledger.csv',delimiter=',',names=True)
from analyze_scan import load
_t,_x,raw=load('b0_coarse');sel=_t>=200;vel=raw[sel,7,2]+1j*raw[sel,7,3];g=raw[sel,7,4]+1j*raw[sel,7,5];control=dict(E_range=float(np.ptp(led['E'])),Q_range=float(np.ptp(led['Q'])),absolute_mean_power20=float(abs(np.mean(-4/.01*np.real(vel.conj()*g)))))
tt=_t[sel];tau=tt-450;win=np.sqrt(np.hanning(len(tt)));ns=np.arange(-3,4);design=np.exp(-1j*tau[:,None]*(.9034745040045122+ns*1.7285161750829272));H=np.linalg.pinv(design*win[:,None])*win[None,:]
vfit=H@vel;gfit=H@g
control['harmonic_power_floor']={str(n):float(abs(-4/.01*np.real(vfit[i].conjugate()*gfit[i]))) for i,n in enumerate(ns) if abs(.9034745+n*1.728516)>1}
summary=dict(linear=lin,slopes=slopes,control=control,rows=rows)
(ROOT/'results/summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(dict(linear=lin,slopes=slopes,control=control),indent=2))
# Export compact numerical table.
import csv
with open(ROOT/'results/amplitude_scan.csv','w') as f:
 writer=csv.writer(f);writer.writerow(['run','dx','dt','b_prepared','b_measured','carrier','Omega','power_n_plus_1','power_n_minus_2','harmonic_excitation_loss','calibrated_excitation_energy','gamma_amplitude_fit','charge_relative_drift'])
 for r in rows:
  c=r['core'][0];line=lambda n:next(l for l in r['lines'] if l['n']==n)['power_both'][7]
  writer.writerow([r['tag'],r['dx'],r['dt'],r['b_input'],r['b_measured'],r['carrier'],r['Omega'],line(1),line(-2),c['harmonic_excess_loss'],c['excess_calibrated'],r['amplitude_gamma_fit'],r['Q_rel_drift']])
