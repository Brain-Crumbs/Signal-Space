import json,pathlib,numpy as np
from scipy.optimize import brentq
from scipy.integrate import cumulative_trapezoid
from analyze_spectrum import probes
R=pathlib.Path(__file__).resolve().parent

def branch(q):
 o=brentq(lambda o:2*o*np.arctanh(2*np.sqrt(1-o*o))/.01-q,np.sqrt(.75)+1e-12,.999999);r=np.arctanh(2*np.sqrt(1-o*o));return o,((o*o+.75)*r+.25*np.tanh(r))/.01
out=[]
for name in ['kick_coarse','kick_fine','kick_timefine']:
 s=json.loads((R/'results'/f'{name}_200_1000_spectrum.json').read_text());a=np.load(R/'results'/f'{name}_200_1000_profiles.npz');lines={l['n']:l for l in s['lines']};x=a['x'];i=list(a['n']).index(-1);sel=(x>=8)&(x<=14);decay=-np.polyfit(x[sel],np.log(abs(a['A'][i,sel])),1)[0]
 norm=sum(l['core_norm2'] for l in lines.values() if l['n']!=0);harmP=sum(2*l['detectors'][2]['power_right'] for l in lines.values() if l['open']);harmQ=sum(2*l['detectors'][2]['charge_right'] for l in lines.values() if l['open']);
 h=np.genfromtxt(R/'results'/f'{name}_ledger.csv',names=True,delimiter=',');sel=h['t']>=200;tt=h['t'][sel];qc=h['Q20'][sel];ec=h['E20'][sel];o,b=np.array([branch(q) for q in qc]).T;ex=ec-b;sd=-np.polyfit(tt,ex,1)[0];pred=harmP-np.mean(o)*harmQ
 t,px,rr=probes(name);take=t>=200;rr=rr[take];w=np.hanning(len(rr));j=list(px).index(40.);v=rr[:,j,2]+1j*rr[:,j,3];g=rr[:,j,4]+1j*rr[:,j,5];phi=rr[:,j,0]+1j*rr[:,j,1];V=np.fft.fft(v*w)/len(w);G=np.fft.fft(g*w)/len(w);C=np.fft.fft(phi*w)/len(w);P=-4/.01*np.real(np.conj(V)*G)/np.mean(w*w);Q=4/.01*np.imag(np.conj(C)*G)/np.mean(w*w);freq=-2*np.pi*np.fft.fftfreq(len(w),.1);direct=np.sum(w*w*(-4/.01*np.real(np.conj(v)*g)))/np.sum(w*w)
 bands=[]
 for n in [-2,1,2]:
  sigma=lines[n]['sigma'];band=abs(freq-sigma)<.04;bands.append({'n':n,'fft_band_power':float(P[band].sum()),'harmonic_fit_power':2*lines[n]['detectors'][2]['power_right']})
 cuts=[];i=list(a['n']).index(1);S=a['S3'][i]+a['S5'][i];proj=S*np.exp(-1j*lines[1]['k']*x)
 for cut in [5,8,12,20,30]:
  take=abs(x)<=cut;integral=np.trapezoid(proj[take],x[take]);cuts.append({'half_width':cut,'integral_magnitude':float(abs(integral))})
 z={'name':name,'energy_drift':float(np.max(abs(h['E']/h['E'][0]-1))),'charge_drift':float(np.max(abs(h['Q']/h['Q'][0]-1))),'closed_component_fraction_of_noncarrier_norm':float(lines[-1]['core_norm2']/norm),'closed_open_norm_ratio':float(lines[-1]['core_norm2']/lines[1]['core_norm2']),'closed_decay_fitted':float(decay),'closed_decay_predicted':lines[-1]['kappa'],'harmonic_energy_flux':float(harmP),'harmonic_charge_flux':float(harmQ),'mean_excess_energy':float(np.mean(ex)),'branch_omega_mean':float(np.mean(o)),'measured_excess_decay_rate':float(sd),'predicted_excess_decay_rate':float(pred),'rate_scale_measured':float(np.mean(ex)/sd),'rate_scale_predicted':float(np.mean(ex)/pred),'rate_scale_clock_cycles':float(np.mean(ex)/sd*s['carrier']/(2*np.pi)),'parseval_error':float(abs(P.sum()-direct)),'fft_bands':bands,'source_window_checks':cuts}
 out.append(z);np.savez_compressed(R/'results'/f'{name}_diagnostics.npz',spectrum_frequency=freq,spectrum_power=P,spectrum_charge=Q,ledger_t=tt,excess=ex,source_x=x,source_projected=proj,source_cumulative=cumulative_trapezoid(proj,x,initial=0))
print(json.dumps(out,indent=2));(R/'results/diagnostics.json').write_text(json.dumps(out,indent=2))
