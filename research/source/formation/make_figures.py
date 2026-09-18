import pathlib,json,numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from analyze import snapshots,profile
ROOT=pathlib.Path(__file__).resolve().parent;OUT=ROOT/'deliverables';OUT.mkdir(exist_ok=True)
D={r['name']:r for r in json.loads((ROOT/'results/analysis.json').read_text())}
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'white','axes.titlesize':12,'axes.labelsize':10})
colors=['#22577a','#c26732','#418069']
def hist(n):return np.genfromtxt(ROOT/'results'/f'{n}.csv',names=True,delimiter=',')
n='settled_fine';h=hist(n);x,t,f=snapshots(ROOT/'results'/f'{n}_snap.bin');r=D[n]
fig,axs=plt.subplots(2,2,figsize=(12,8),layout='constrained');ax=axs[0,0];sel=abs(x)<=40
im=ax.pcolormesh(x[sel],t,f[:,0,sel]**2+f[:,1,sel]**2,shading='auto',norm=LogNorm(1e-7,.35),cmap='magma');ax.set(xlabel=r'$mx$',ylabel=r'$mt$',title='A  Gaussian → localized charged core');fig.colorbar(im,ax=ax,label=r'$|\Phi|^2$')
ax=axs[0,1]
for W,c in zip([20,30,40],colors):ax.plot(h['t'],h[f'Q{W}'],color=c,label=f'|x| ≤ {W}')
ax.set(xlabel=r'$mt$',ylabel='Charge in window',title='B  Charge leaves; a persistent core remains',ylim=(228,243));ax.legend(frameon=False)
ax=axs[1,0];sel=abs(x)<=12
ax.plot(x[sel],np.hypot(f[0,0,sel],f[0,1,sel]),color=colors[1],ls='--',label='Initial Gaussian')
ax.plot(x[sel],np.hypot(f[-1,0,sel],f[-1,1,sel]),color=colors[0],label='Evolved, t = 1600')
ax.plot(x[sel],profile(r['window20']['omega_Q'],x[sel]),color=colors[2],ls=':',lw=2,label='Exact branch at retained charge');ax.set(xlabel=r'$mx$',ylabel=r'$|\Phi|$',title='C  The evolved profile approaches the bound branch');ax.legend(frameon=False,loc='upper left',fontsize=8)
ax=axs[1,1];sel=h['t']>=800;tt=h['t'][sel];ph=np.unwrap(h['phase20'])[sel];res=ph-np.polyval(np.polyfit(tt,ph,1),tt);ax.plot(tt,res,color=colors[0],lw=.8);ax.set(xlabel=r'$mt$',ylabel='Phase residual (radians)',title='D  115 late-time cycles: 0.00484 rad RMS');ax.axhline(0,c='gray',lw=.5)
fig.suptitle('Signal Space formation milestone — conservative evolution, a = 0',fontsize=16,fontweight='bold');fig.savefig(OUT/'Signal_Space_Formation_Diagnostics.png',dpi=175);plt.close(fig)
fig,axs=plt.subplots(2,2,figsize=(10,8),layout='constrained')
for om,ax in zip([.9,.88,.95,.98],axs.flat):
 vals=np.array([[100*D[f'scan_o{om:.2f}_w{w:g}_n{nu:g}']['profile_fit']['relative_L2_mean'] for nu in [.8,.9,1]] for w in [.5,1,2,4]])
 im=ax.imshow(vals,vmin=0,vmax=18,cmap='YlOrRd',aspect='auto');ax.set_xticks(range(3),['0.8','0.9','1.0']);ax.set_yticks(range(4),['0.5','1','2','4']);ax.set(xlabel=r'Initial $\nu/m$',ylabel=r'Initial $w/R_Q$',title=f'Target ω/m = {om:.2f}')
 for i in range(4):
  for j in range(3):ax.text(j,i,f'{vals[i,j]:.1f}%',ha='center',va='center',color='white' if vals[i,j]>11 else '#1b263b')
fig.colorbar(im,ax=axs,label='Mean relative field-profile residual (%)');fig.suptitle('All 48 Gaussian preparations — residuals at t = 400–800',fontsize=15,fontweight='bold');fig.savefig(OUT/'Signal_Space_Formation_Scan.png',dpi=175);plt.close(fig)
fig=plt.figure(figsize=(12,8),layout='constrained');gs=fig.add_gridspec(2,3,height_ratios=[1,0.8]);axbot=fig.add_subplot(gs[1,:]);handles=[]
for j,(ph,label) in enumerate([(0,'0'),(1.5708,'π/2'),(3.1416,'π')]):
 n=f'readout_fine_p{ph:.4f}';x,t,f=snapshots(ROOT/'results'/f'{n}_snap.bin');sel=abs(x)<=80;ax=fig.add_subplot(gs[0,j]);im=ax.pcolormesh(x[sel],t,f[:,0,sel]**2+f[:,1,sel]**2,shading='auto',cmap='magma',vmin=0,vmax=.5);ax.set(xlabel=r'$mx$',ylabel=r'$mt$',title=f'Relative phase {label}');h=hist(n);axbot.plot(h['t'],h['midDensity'],c=colors[j],label=label,lw=1)
axbot.set(xlabel=r'$mt$',ylabel=r'Local intensity $|\Phi(t,0)|^2$',title='Local phase record produced by collision of formed cores');axbot.legend(title='Prepared phase',frameon=False,ncol=3);axbot.set_xlim(0,650);fig.suptitle('Causal classical phase readout — with collision back-action',fontsize=15,fontweight='bold');fig.savefig(OUT/'Signal_Space_Formation_Readout.png',dpi=175);plt.close(fig)
