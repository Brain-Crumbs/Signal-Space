import pathlib,json,numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.ndimage import uniform_filter1d
R=pathlib.Path(__file__).resolve().parent;O=R/'deliverables';O.mkdir(exist_ok=True)
s=json.loads((R/'results/kick_fine_200_1000_spectrum.json').read_text());d=json.loads((R/'results/diagnostics.json').read_text())[1]
a=np.load(R/'results/kick_fine_200_1000_profiles.npz');b=np.load(R/'results/kick_fine_diagnostics.npz');x=a['x'];ns=list(a['n']);l={z['n']:z for z in s['lines']}
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'white'})
fig,axs=plt.subplots(2,2,figsize=(12,8),layout='constrained');colors={-1:'#22577a',1:'#c26732',-2:'#418069'}
ax=axs[0,0]
for n,label in [(-1,'Confined component: −0.8286 m'),(1,'First outgoing component: +2.6284 m'),(-2,'Second outgoing component: −2.5570 m')]:
 ax.semilogy(x,abs(a['A'][ns.index(n)]),c=colors[n],label=label,lw=1.6)
ax.set(xlim=(-20,20),ylim=(1e-7,.15),xlabel=r'$mx$',ylabel='Fitted field amplitude',title='A  Most of the oscillation remains confined');ax.legend(frameon=False,fontsize=8,loc='lower left')
ax=axs[0,1];sig=b['spectrum_frequency'];pw=b['spectrum_power'];order=np.argsort(sig);yy=np.where(pw>1e-14,pw,np.nan);ax.semilogy(sig[order],yy[order],c='#22577a',lw=.9)
for n,lab in [(1,'89.3%'),(-2,'10.7%')]:ax.annotate(lab,(l[n]['sigma'],2*l[n]['detectors'][2]['power_right']*.55),xytext=(l[n]['sigma']+.25,1e-5),fontsize=9,arrowprops={'arrowstyle':'-','color':'gray'})
ax.axvspan(-1,1,color='#e5e7eb',alpha=.6);ax.set(xlim=(-5,5),ylim=(1e-12,5e-5),xlabel=r'Laboratory angular frequency / $m$',ylabel=r'Outward spectral power per bin / $m^2$',title='B  Two narrow bands carry the harmonic radiation');ax.text(0,2e-12,'Below free-wave threshold',ha='center',fontsize=8)
ax=axs[1,0];cum=b['source_cumulative'];total=cum[-1];norm=l[1]['source_abs_integral'];curve=np.real(cum*np.exp(-1j*np.angle(total)))/norm;ax.plot(x,curve,c='#22577a');ax.axhline(0,c='gray',lw=.5);ax.axhline(abs(total)/norm,c='#c26732',ls='--',label=f'Net amplitude: {100*l[1]["coherence_ratio"]:.3f}%');ax.set(xlim=(-12,12),xlabel=r'Upper source-integration limit $mx$',ylabel='Cumulative contribution / sum of magnitudes',title='C  Core contributions largely cancel');ax.legend(frameon=False,fontsize=9)
ax=axs[1,1];t=b['ledger_t'];ex=b['excess'];smooth=uniform_filter1d(ex,size=21,mode='nearest');sel=(t>220)&(t<980);baseline=np.mean(ex)+d['measured_excess_decay_rate']*(np.mean(t)-200);ax.plot(t[sel]+2400,(smooth-baseline)[sel],c='#22577a',lw=1.3,label='Measured core excess energy');ax.plot(t+2400,-d['predicted_excess_decay_rate']*(t-200),c='#c26732',ls='--',label='Prediction from outgoing harmonics');ax.set(xlabel=r'Time since Gaussian preparation, $mt$',ylabel=r'Change of $E_{core}-E_{branch}(Q_{core})$, in $m$',title='D  Radiation accounts for the slow relaxation');ax.legend(frameon=False,fontsize=8)
fig.suptitle('Signal Space charged-clock radiation — weak leakage is resolved',fontsize=16,fontweight='bold');fig.savefig(O/'Signal_Space_Charged_Clock_Radiation_Diagnostics.png',dpi=175);plt.close(fig)
