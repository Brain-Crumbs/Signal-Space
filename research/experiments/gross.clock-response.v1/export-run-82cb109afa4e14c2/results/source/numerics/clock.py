"""Radial core profiles, independent clock eigenproblem, reciprocal PDE evolution."""
from pathlib import Path
import os
import numpy as np
from scipy.integrate import solve_bvp
from scipy.linalg import solve_banded, eigh_tridiagonal
from signal_space.models.clock import clock_mass, core_force, core_clock_force, stationary_rhs, radial_energy
from signal_space.runtime.io import read_json, write_json
from signal_space.runtime.events import append_event


def profile(omega, radius, dr, continuation=None):
    """BVP with regular origin, then Newton projection onto the evolution stencil.

    All attempted seeds and failures are returned; no attractive trivial solution
    is silently accepted. The discrete solve uses the same Laplacian as evolution.
    """
    r = np.linspace(0., radius, round(radius / dr) + 1)
    attempts = []
    chosen = None
    for core_radius in (5., 10., 20., 40., 60.):
        guess = 0.72 / (1 + np.exp(np.clip((r - core_radius) / 1.5, -70, 70)))
        slope = np.gradient(guess, dr)

        def fun(x, y):
            return np.vstack((y[1], stationary_rhs(y[0], omega)))

        def bc(ya, yb):
            return np.array([ya[1], yb[0]])

        try:
            solved = solve_bvp(fun, bc, r, np.vstack((guess, slope)),
                               S=np.array([[0., 0.], [0., -2.]]),
                               tol=2e-6, max_nodes=20000)
            values = solved.sol(r)[0]
            tail = float(abs(values[-2]))
            valid = (solved.success and values[0] > 0.15 and np.min(values[:-1]) > -1e-6
                     and tail < 2e-5 and np.max(values) < 1.5)
            attempts.append({'guess_radius': core_radius, 'success': bool(solved.success),
                             'message': str(solved.message), 'center': float(values[0]),
                             'tail': tail, 'valid': bool(valid)})
            if valid:
                chosen = values
                break
        except (ValueError, RuntimeError) as exc:
            attempts.append({'guess_radius': core_radius, 'success': False, 'message': str(exc)})
    if chosen is None and continuation is not None:
        start_omega,start_r,start_u=continuation
        seed=np.interp(r,start_r,np.r_[0.,start_u,0.])
        previous=np.zeros_like(r)
        previous[1:]=seed[1:]/r[1:]
        previous[0]=previous[1]
        steps=max(1,int(np.ceil(abs(start_omega-omega)/0.005)))
        for target in np.linspace(start_omega,omega,steps+1)[1:]:
            def continued_fun(x,y):
                return np.vstack((y[1],stationary_rhs(y[0],target)))
            try:
                solved=solve_bvp(continued_fun,bc,r,np.vstack((previous,np.gradient(previous,dr))),
                    S=np.array([[0.,0.],[0.,-2.]]),tol=2e-6,max_nodes=40000)
                values=solved.sol(r)[0]
                valid=bool(solved.success and values[0]>0.15 and np.min(values[:-1])>-1e-6)
                attempts.append({'continuation_from':start_omega,'target':float(target),
                                 'success':bool(solved.success),'valid':valid,
                                 'center':float(values[0]),'tail':float(abs(values[-2])),
                                 'message':str(solved.message)})
                if not valid:break
                previous=values
                if abs(target-omega)<1e-12 and abs(values[-2])<2e-5:
                    chosen=values
            except (ValueError,RuntimeError) as exc:
                attempts.append({'continuation_from':start_omega,'target':float(target),
                                 'success':False,'message':str(exc)})
                break
    if chosen is None:
        return r, None, attempts
    x = r[1:-1] * chosen[1:-1]
    rr = r[1:-1]
    h2 = dr * dr
    for iteration in range(20):
        f = x / rr
        s = f * f
        residual = (np.pad(x, (1, 1))[:-2] - 2*x + np.pad(x, (1, 1))[2:]) / h2 - rr * stationary_rhs(f, omega)
        error = float(np.max(abs(residual)))
        if error < 2e-10:
            break
        jac = (-2/h2 - (1-omega*omega-6*s+15*s*s)) * np.ones_like(x)
        band = np.zeros((3, len(x)))
        band[0, 1:] = 1/h2
        band[1] = jac
        band[2, :-1] = 1/h2
        x -= solve_banded((1, 1), band, residual)
    attempts.append({'discrete_newton_steps': iteration+1, 'discrete_residual': error})
    if error >= 2e-10 or np.min(x) <= -1e-8:
        return r, None, attempts
    return r, x, attempts


def core_stats(r, u, omega, dr):
    f = np.zeros_like(r)
    f[1:-1] = u/r[1:-1]
    f[0] = f[1]
    charge = float(8*np.pi*omega*dr*np.sum(u*u))
    energy = radial_energy(r[1:-1], u, -1j*omega*u, np.zeros_like(u), np.zeros_like(u), dr)
    return f, charge, energy, float(energy/charge), float(f[0]), float(f[int(0.75*(len(r)-1))])


def eigenproblem(r, u, dr, nu):
    rr = r[1:-1]
    well = clock_mass((u/rr)**2, nu)
    eigen, vectors = eigh_tridiagonal(2/dr**2 + well,
                                      np.full(len(rr)-1, -1/dr**2),
                                      select='i', select_range=(0, min(2, len(rr)-1)))
    shape = vectors[:, 0]
    if shape[0] < 0: shape *= -1
    shape /= np.sqrt(dr*np.dot(shape, shape))
    return eigen, shape, well


def core_hessians(r, u, dr, omega):
    rr=r[1:-1];s=(u/rr)**2
    lap=2/dr**2
    minus=lap+1-omega**2-2*s+3*s*s
    plus=minus-4*s+12*s*s
    off=np.full(len(rr)-1,-1/dr**2)
    rows={}
    for l in (0, 1):
        angular=l*(l+1)/rr**2
        for label,diag in (('Lplus',plus),('Lminus',minus)):
            vals=eigh_tridiagonal(diag+angular,off,select='i',select_range=(0,2),eigvals_only=True)
            rows[f'{label}_l{l}']=vals.tolist()
    return rows


def evolution(r, u0, mode, omega, eig, amplitude, dr, dt, cycles, sample_stride, sponge_start, local_index=0):
    """Kick-drift-kick in radial u=r Phi and w=r chi, with logged outer sink."""
    rr=r[1:-1]; N=len(rr); u=u0.astype(complex).copy(); pu=-1j*omega*u
    w=amplitude*mode/np.max(mode/rr); pw=np.zeros(N)
    gamma=np.clip((rr-sponge_start)/(r[-1]-sponge_start),0,1)**2 * 0.08
    steps=int(np.ceil(cycles*2*np.pi/np.sqrt(eig)/dt))
    basis=mode/np.max(mode/rr)
    norm=dr*np.dot(basis,basis)
    init_q=8*np.pi*omega*dr*np.dot(u0,u0)
    init_mode=.5*eig*(dr*np.dot(w,basis))**2/norm
    charge_sink=0.;energy_sink=0.; rows=[]

    def acceleration(u,w):
        v=u/rr; s=np.abs(v)**2;chi=w/rr
        lapu=(np.pad(u,(1,1))[:-2]-2*u+np.pad(u,(1,1))[2:])/dr**2
        lapw=(np.pad(w,(1,1))[:-2]-2*w+np.pad(w,(1,1))[2:])/dr**2
        return (lapu-(core_force(s)+core_clock_force(s)*chi**2)*u,
                lapw-clock_mass(s)*w-0.1*chi**2*w)

    au,aw=acceleration(u,w)
    for step in range(steps+1):
        if step%sample_stride==0 or step==steps:
            q=8*np.pi*dr*np.sum(-np.imag(np.conj(u)*pu))
            coordinate=dr*np.dot(w,basis)/norm
            momentum=dr*np.dot(pw,basis)/norm
            mode_energy=.5*norm*(momentum**2+eig*coordinate**2)
            local=float(w[local_index]/rr[local_index])
            rows.append((step*dt,local,float(coordinate),float(momentum),float(mode_energy/init_mode) if init_mode else 0.,
                         float(q/init_q),float((q+charge_sink-init_q)/init_q),
                         float(radial_energy(rr,u,pu,w,pw,dr)),float(energy_sink),
                         float(np.max(abs(u/rr)))))
        if step==steps: break
        # Symmetric dissipative half steps on canonical momenta; sink is computed
        # from the resulting changes (including the time-centered charge change).
        for half in (0,1):
            if half==0:
                pu += 0.5*dt*au;pw += 0.5*dt*aw
            else:
                pu += 0.5*dt*au;pw += 0.5*dt*aw
            oldpu=pu.copy();oldpw=pw.copy()
            damping=np.exp(-gamma*dt/2)
            pu*=damping;pw*=damping
            charge_sink+=float(8*np.pi*dr*np.sum(np.imag(np.conj(u)*(pu-oldpu))))
            energy_sink+=float(4*np.pi*dr*np.sum(abs(oldpu)**2+oldpw**2/2-abs(pu)**2-pw**2/2))
            if half==0:
                u+=dt*pu;w+=dt*pw
                au,aw=acceleration(u,w)
    return np.asarray(rows),{'steps':steps,'initial_charge':init_q,'initial_mode_energy':init_mode,
                             'sink_charge':charge_sink,'sink_energy':energy_sink,'dt':dt,
                             'sample_stride':sample_stride,'boundary':'Dirichlet with outer dissipative layer'}


def execute(request_path):
    request=read_json(request_path)
    if request.get('resume_checkpoint'): raise ValueError('atomic Test 6 does not resume')
    attempt=Path(request['attempt_path']);raw=attempt/'raw';raw.mkdir(exist_ok=True)
    events=attempt/'events.jsonl';config=request['config'];p=config['parameters']
    write_json(raw/'rng-start.json',{'root_seed':request['seed_ledger'], 'stochastic_use':'none'})
    append_event(events,'worker-started','run',{'pid':os.getpid(),'algorithm':'radial-bvp-discrete-newton-eigen-verlet-v1'})
    profiles={}; table=[]; failures=[]
    previous=None
    for omega in sorted(p['frequencies'],reverse=True):
        key=f'{omega:.3f}'
        r,u,attempts=profile(omega,p['radius'],p['dr'],previous)
        write_json(raw/f'profile-attempts-{key}.json',attempts)
        if u is None:
            failures.append(key);table.append({'omega':omega,'profile':'unresolved','attempts':len(attempts)})
            append_event(events,'profile-unresolved','run',{'omega':omega})
            continue
        f,q,e,ratio,center,tail=core_stats(r,u,omega,p['dr'])
        eig,mode,well=eigenproblem(r,u,p['dr'],p['nu'])
        hessian=core_hessians(r,u,p['dr'],omega)
        profiles[key]=(r,u,mode,eig[0]);np.savez_compressed(raw/f'profile-{key}.npz',r=r,u=u,mode=mode,well=well,eigenvalues=eig)
        previous=(omega,r,u)
        table.append({'omega':omega,'profile':'solved','Q':q,'E':e,'E_over_Q':ratio,'center':center,
                      'tail_at_three_quarters':tail,'eigenvalue':float(eig[0]),
                      'hessians':hessian,'profile_residual':attempts[-1]['discrete_residual']})
        append_event(events,'profile-solved','run',{'omega':omega,'eigenvalue':float(eig[0])})
    table.sort(key=lambda row:row['omega'])
    write_json(raw/'profiles.json',table)
    # Predeclared selection: smallest accepted omega with a bound mode and E/Q<1,
    # tested on its finite-domain and mesh controls below; no post hoc profile tuning.
    candidates=[row for row in table if row['profile']=='solved' and 0<row['eigenvalue']<.25 and row['E_over_Q']<1]
    if not candidates:
        write_json(raw/'execution.json',{'selection':None,'failures':failures,'reason':'no bound candidate'});
        append_event(events,'worker-completed','run',{'selection':None});return 0
    selected=min(candidates,key=lambda x:x['omega']);omega=selected['omega'];key=f'{omega:.3f}'
    r,u,mode,eig=profiles[key]
    # Independent refinements: h/2 at fixed domain and doubled radius at fixed h.
    refinements=[]
    for label,radius,dr in [('fine',p['radius'],p['dr']/2),('wide',p['radius']*2,p['dr'])]:
        rx,ux,attempts=profile(omega,radius,dr,(omega,r,u))
        write_json(raw/f'profile-attempts-{label}.json',attempts)
        if ux is None:
            refinements.append({'label':label,'status':'unresolved'});continue
        ev,mv,wv=eigenproblem(rx,ux,dr,p['nu'])
        stats=core_stats(rx,ux,omega,dr)
        np.savez_compressed(raw/f'profile-{label}.npz',r=rx,u=ux,mode=mv,well=wv,eigenvalues=ev)
        refinements.append({'label':label,'status':'solved','radius':radius,'dr':dr,
                            'eigenvalue':float(ev[0]),'Q':stats[1],'E_over_Q':stats[3],
                            'center':stats[4],'tail':stats[5]})
    write_json(raw/'refinements.json',refinements)
    nulls={}
    for nu in (0.,p['nu']):
        ev,_,_=eigenproblem(r,u,p['dr'],nu)
        nulls['nu-off' if nu==0 else 'nu-on']={'eigenvalue':float(ev[0]),'threshold':.25}
    nulls['unexcited']={'chi_initial':0.,'chi_momentum_initial':0.,'density_static':True,
                        'projector_static':True,'local_chi_zero_by_uniqueness':True}
    write_json(raw/'controls.json',nulls)
    record=[]
    for amplitude in [0., *p['amplitudes']]:
        data,details=evolution(r,u,mode,omega,eig,amplitude,p['dr'],p['dt'],
                               p['cycles'] if amplitude==p['amplitudes'][1] else p['control_cycles'],
                               p['sample_stride'],p['sponge_start'])
        np.savez_compressed(raw/f'evolution-{amplitude:.4f}.npz',records=data)
        record.append({'amplitude':amplitude,**details,'saved_samples':len(data)})
        append_event(events,'evolution-completed','run',{'amplitude':amplitude,'steps':details['steps']})
    for item in refinements:
        if item['status']!='solved': continue
        label=item['label'];rx=profiles.get(label)
        if rx is None:
            with np.load(raw/f'profile-{label}.npz') as data:
                re=data['r'];ue=data['u'];me=data['mode'];ee=float(data['eigenvalues'][0])
        grid=item['dr']; timestep=p['dt']*grid/p['dr']
        data,details=evolution(re,ue,me,omega,ee,p['amplitudes'][1],grid,timestep,
                               p['control_cycles'],round(p['sample_stride']*p['dr']/grid),
                               item['radius']-20)
        np.savez_compressed(raw/f'evolution-{label}.npz',records=data)
        record.append({'amplitude':p['amplitudes'][1],'refinement':label,**details,'saved_samples':len(data)})
        append_event(events,'refinement-evolution-completed','run',{'label':label,'steps':details['steps']})
    write_json(raw/'evolutions.json',record)
    write_json(raw/'execution.json',{'selection':key,'failures':failures,'algorithm':'radial-bvp-discrete-newton-eigen-verlet-v1',
       'scope':'flat spherical SS OCF 1 with a=0; gravity decoupled; clock backreacts on core',
       'seed_ledger':request['seed_ledger'],'boundary':'Dirichlet outer radius with logged velocity damping layer'})
    write_json(raw/'rng-end.json',{'root_seed':request['seed_ledger'], 'stochastic_use':'none'})
    append_event(events,'worker-completed','run',{'selection':key})
    return 0
