"""Deterministic checks for Signal Space Foundations II; no empirical data."""
from pathlib import Path
import json, platform
import numpy as np
import scipy
from scipy.linalg import expm
from scipy.integrate import quad, solve_ivp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
I=np.eye(2,dtype=complex)
P=np.array([I,[[0,1],[1,0]],[[0,-1j],[1j,0]],[[1,0],[0,-1]]])
J=np.diag([1.,-1,-1,-1])
def mat(x): return np.einsum('a,aij->ij',x,P)
def vec(X): return np.array([np.trace(s@X).real/2 for s in P])
def boost(v): return expm(mat(np.r_[0,v])/2)
rng=np.random.default_rng(20260911)
err={k:0. for k in ['tomography','determinant','lorentz_metric','lorentz_action','filter_completeness','filter_probability','clock_ode','clock_identity','echo_recovery','cavity_integral','marker_fringe']}
def update(k,v): err[k]=max(err[k],float(np.max(np.abs(v))))
for _ in range(200):
    z=rng.normal(size=(2,2))+1j*rng.normal(size=(2,2))
    X=z@z.conj().T+.2*I
    x=vec(X)
    counts=[(np.trace((I+s)/2@X).real,np.trace((I-s)/2@X).real) for s in P[1:]]
    xt=np.r_[sum(counts[0])/2,[(a-b)/2 for a,b in counts]]
    update('tomography',x-xt)
    A=boost(rng.uniform(-.6,.6,3))@expm(-.5j*mat(np.r_[0,rng.uniform(-.6,.6,3)]))
    Y=A@X@A.conj().T
    L=np.column_stack([vec(A@s@A.conj().T) for s in P])
    update('determinant',(np.linalg.det(Y)-np.linalg.det(X))/max(1,abs(np.linalg.det(X))))
    update('lorentz_metric',L.T@J@L-J)
    update('lorentz_action',vec(Y)-L@x)
    k=1/np.linalg.norm(A,2); F=k*A
    ev,U=np.linalg.eigh(I-F.conj().T@F)
    G=(U*np.sqrt(np.maximum(ev,0)))@U.conj().T
    update('filter_completeness',F.conj().T@F+G.conj().T@G-I)
    rho=X/np.trace(X)
    ps=np.trace(F@rho@F.conj().T).real
    update('filter_probability',ps-k*k*np.trace(Y).real/np.trace(X).real)

# Nonlinearity witness for a normalized boost.
A=boost(np.array([0,0,.7]))
def nf(r):
    y=A@r@A.conj().T
    return y/np.trace(y)
r0=(I+P[3])/2; r1=(I-P[3])/2
nonaffinity=float(np.linalg.norm(nf((r0+r1)/2)-(nf(r0)+nf(r1))/2))

# Independent cavity null-flight integral and compatible nonstationary count model.
c=1.; gamma=1.; acc=.4; length=.2; T=5.
eps=acc*length/(2*c*c)
f=eps/np.arctanh(eps)
def b(t): return acc*t/c/np.sqrt(1+(acc*t/c)**2)
def db(t): return acc/c/(1+(acc*t/c)**2)**1.5
def eta(t): return np.arcsinh(acc*t/c)
def lag(t): return np.arcsinh(db(t)/(2*gamma*np.sqrt(1-b(t)**2)))
def h(t): return eta(t)+lag(t)
def count_rate(t): return np.cosh(h(t))-b(t)*np.sinh(h(t))
tau=c/acc*np.arcsinh(acc*T/c)
count=quad(count_rate,0,T,epsabs=1e-12,epsrel=1e-12)[0]
period=2*quad(lambda chi:1/(c*(1+acc*chi/c**2)),-length/2,length/2,epsabs=1e-13)[0]
update('cavity_integral',period-(2*length/c)/f)
grid=np.linspace(0,T,501)
for t in grid:
    update('clock_ode',db(t)-2*gamma*(np.sinh(h(t))-b(t)*np.cosh(h(t))))
    update('clock_identity',count_rate(t)-np.sqrt(1-b(t)**2)*np.cosh(lag(t)))
    # Instantaneous echo derivative from null-coordinate derivatives.
    Rp=(1+b(t))/(1-b(t))
    update('echo_recovery',.5*np.log(Rp)-eta(t))
sol=solve_ivp(lambda t,y:2*gamma*(np.sinh(h(t))-y*np.cosh(h(t))),[0,T],[0.],rtol=1e-11,atol=1e-13,dense_output=True)
ode_error=float(np.max(abs(sol.sol(grid)[0]-b(grid))))
for th in [0,.3,1.0,np.pi/2]:
    marker=np.array([np.cos(th),np.sin(th)])
    for ph in np.linspace(0,2*np.pi,31):
        psi=(np.kron([1,0],[1,0])+np.exp(-1j*ph)*np.kron([0,1],marker))/np.sqrt(2)
        rho=psi.reshape(2,2)@psi.reshape(2,2).conj().T
        p=np.trace((I+P[1])/2@rho).real
        update('marker_fringe',p-(1+np.cos(th)*np.cos(ph))/2)

# Non-collinear boosts and frame-loop closure.
A=boost(np.array([.5,0,0])); B=boost(np.array([0,.6,0]))
noncomm=float(np.linalg.norm(A@B-B@A))
frames=[I,A,B@A]
G10=frames[1]@np.linalg.inv(frames[0]); G21=frames[2]@np.linalg.inv(frames[1]); G02=frames[0]@np.linalg.inv(frames[2])
loop_error=float(np.linalg.norm(G02@G21@G10-I))

clock={"c0":c,"gamma":gamma,"proper_acceleration":acc,"cavity_length":length,"reference_duration":T,"epsilon":eps,"phase_rate_ratio":f,"proper_duration":tau,"expected_count_reading":count,"phase_reading":f*tau,"count_excess":count-tau,"phase_deficit":tau*(1-f),"initial_statistical_rapidity":h(0.),"initial_echo_rapidity":0.,"final_statistical_rapidity":h(T),"final_echo_rapidity":eta(T),"ode_max_error":ode_error}
rows=[]
for L0 in [.4,.2,.1,.05]:
    e=acc*L0/(2*c*c); ff=e/np.arctanh(e)
    rows.append({'L':L0,'epsilon':e,'phase_rate_ratio':ff,'phase_deficit':tau*(1-ff)})
result={'seed':20260911,'matrix_trials':200,'versions':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},'max_errors':err,'nonaffinity_witness':nonaffinity,'noncommuting_boost_norm':noncomm,'pure_frame_loop_error':loop_error,'clock':clock,'length_refinement':rows}
assert max(err.values())<1e-10,err
assert ode_error<1e-9
assert nonaffinity>.1 and noncomm>.1 and loop_error<1e-12
assert count>tau>f*tau and all(rows[i]['phase_deficit']>rows[i+1]['phase_deficit'] for i in range(3))
result['status']='passed'
(ROOT/'results.json').write_text(json.dumps(result,indent=2)+'\n')

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False})
fig,axs=plt.subplots(1,2,figsize=(10,3.5),layout='constrained')
axs[0].plot(grid,h(grid),label='Hazard coordinate h',color='#ab5b35')
axs[0].plot(grid,eta(grid),label='Echo rapidity',color='#214e69',linestyle='--')
axs[0].set(xlabel='Reference time t',ylabel='Rapidity',title='A. Response lag is observable'); axs[0].legend(frameon=False)
cts=np.array([quad(count_rate,0,t,epsabs=1e-11)[0] for t in grid])
taus=c/acc*np.arcsinh(acc*grid/c)
axs[1].plot(grid,cts-taus,label='Expected count minus proper time',color='#ab5b35')
axs[1].plot(grid,f*taus-taus,label='Cavity phase minus proper time',color='#214e69')
axs[1].axhline(0,color='.6',lw=.7)
axs[1].set(xlabel='Reference time t',ylabel='Reading difference',title='B. Fixed calibration, distinct errors');axs[1].legend(frameon=False,fontsize=8)
fig.savefig(ROOT/'figures/clock_comparison.pdf')
fig.savefig(ROOT/'figures/clock_comparison.png',dpi=180)
plt.close(fig)
print(json.dumps({'status':result['status'],'errors':err,'clock':clock,'refinement':rows},indent=2))
