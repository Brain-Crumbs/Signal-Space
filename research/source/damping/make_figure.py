import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import numpy as np,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
s=json.loads((ROOT/'results/summary.json').read_text());lin=s['linear'];rows=s['rows']
plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'#f8fafb','axes.facecolor':'white','axes.titleweight':'bold'})
fig,axs=plt.subplots(2,2,figsize=(12.5,9.2));blue='#21618c';orange='#d77e31';green='#29826c'
a=axs[0,0]
for n,col,label in [('1',blue,'Dominant +1 channel'),('-2',orange,'Secondary −2 channel')]:
 d=s['slopes'][n];b=np.array(d['b']);p=np.array(d['power']);a.loglog(b,p,'o-',color=col,label=f"{label}: slope {d['exponent']:.3f}");power=2 if n=='1' else 4;a.loglog(b,p[0]*(b/b[0])**power,'--',color=col,alpha=.4)
a.set(title='A  Radiation has a nonzero quadratic channel',xlabel='Measured confined amplitude b',ylabel='Outgoing power, both sides / m²');a.legend(fontsize=9);a.grid(alpha=.15,which='both')
a=axs[0,1];rr=sorted([r for r in rows if r['dx']==.025 and r['dt']==.005],key=lambda r:r['b_measured']);b=np.array([r['b_measured'] for r in rr]);gamma=np.array([r['amplitude_gamma_fit'] for r in rr]);a.plot(b,1e6*gamma,'o-',color=blue,label='Measured amplitude decay');a.axhline(-lin['Omega_imag']*1e6,color=green,ls='--',label='Continuum outgoing pole');a.set(title='B  Finite amplitude changes the damping rate',xlabel='Measured confined amplitude b',ylabel='Amplitude decay rate γ / (10⁻⁶ m)');a.set_ylim(1.14,1.46);a.legend(fontsize=9);a.grid(alpha=.15)
a=axs[1,0];ds=json.loads((ROOT/'results/discrete_resonance.json').read_text());rr=[next(r for r in rows if r['tag']==tag) for tag in ['b0.01_coarse','b0.01_fine','b0.01_superfine']];h=np.array([r['dx'] for r in rr]);g=np.array([r['amplitude_gamma_fit'] for r in rr]);gd=np.array([-next(d for d in ds if d['dx']==r['dx'] and d['dt']==r['dt'])['Omega_imag'] for r in rr]);a.plot(h*h,1e6*g,'o',color=blue,ms=7,label='Time evolution, prepared b = 0.01');a.plot(h*h,1e6*gd,'x--',color=orange,ms=7,label='Pole of the same discrete update');a.axhline(-lin['Omega_imag']*1e6,color=green,ls=':',label='Continuum pole');a.set(title='C  Independent methods converge together',xlabel='Spatial step squared (m Δx)²',ylabel='Amplitude decay rate γ / (10⁻⁶ m)');a.legend(fontsize=8.5);a.grid(alpha=.15);a.ticklabel_format(axis='x',style='sci',scilimits=(0,0))
a=axs[1,1];z=np.load(ROOT/'results/resonance_mode.npz');p=np.load(ROOT/'inputs/parent_radiation_profiles.npz');xp=p['x'];take=(xp>=0)&(xp<=12);xr=xp[take];aa=abs(p['A'][3,take]);a.plot(z['x'],abs(z['v']),color=blue,lw=2,label='Linear resonance: confined component');a.plot(xr[::12],(aa/aa[0])[::12],'o',mfc='none',color=orange,ms=5,label='Previously formed remnant');a.plot(z['x'],abs(z['u']),color=green,label='Linear resonance: open component');a.set_yscale('log');a.set_xlim(0,12);a.set_ylim(6e-4,1.4);a.set(title='D  The resonance matches the remnant’s shape',xlabel='Distance from center / m⁻¹',ylabel='Component magnitude (confined center = 1)');a.legend(fontsize=8.5);a.grid(alpha=.15)
fig.suptitle('Signal Space charged clock: weak linear leakage survives as amplitude → 0',fontsize=17,fontweight='bold',y=.985)
fig.text(.5,.017,'Original classical field equations • fixed initial charge Q = 231.832884 • no damping or absorbing layer\nThe pole predicts decay of the tracked oscillation; it does not establish the ultimate fate of every excitation.',ha='center',fontsize=10,color='#465463')
fig.tight_layout(rect=[0,.065,1,.955],h_pad=2.7,w_pad=2)
fig.savefig(ROOT/'deliverables/Signal_Space_Charged_Clock_Damping_Diagnostics.png',dpi=180)
