"""Independent audit of saved full physical Floquet maps; no solver rerun."""
import numpy as np
from scipy.optimize import linear_sum_assignment
from signal_space.runtime.io import write_json
from signal_space.analysis.router import write_csv

LABELS=('vacuum','equal','counter')
SIGMA=np.array([[[0,1],[1,0]],[[0,-1j],[1j,0]],[[1,0],[0,-1]]])


def paired_error(a,b):
    costs=abs(a[:,None]-b[None,:]); i,j=linear_sum_assignment(costs); return float(costs[i,j].max())


def physical_reference(q):
    # Independent projector swap Fourier matrices in complex wave coordinates.
    u=np.eye(4,dtype=complex); ident=np.eye(2)
    for axis in range(3):
        p=(ident+SIGMA[axis])/2; c=ident-p
        onsite=np.block([[c,p],[p,c]])
        bond=np.block([[c,np.exp(1j*q[axis])*p],[np.exp(-1j*q[axis])*p,c]])
        u=bond@onsite@u
    # Realification must transform q and -q, not simply take real of U(q).
    um=np.eye(4,dtype=complex)
    for axis in range(3):
        p=(ident+SIGMA[axis])/2; c=ident-p
        um=np.block([[c,np.exp(-1j*q[axis])*p],[np.exp(1j*q[axis])*p,c]])@np.block([[c,p],[p,c]])@um
    a=(u+um.conj())/2; b=(u-um.conj())/(2j)
    real=np.zeros((8,8),complex); real[0::2,0::2]=a; real[0::2,1::2]=-b; real[1::2,0::2]=b; real[1::2,1::2]=a
    out=np.eye(20,dtype=complex); out[:8,:8]=real; return out


def analyze(run_path,output,config):
    raw=sorted((run_path/'attempts').glob('*/raw/floquet.npz'))[-1]
    with np.load(raw,allow_pickle=False) as f: d={k:f[k] for k in f.files}
    if any(not np.all(np.isfinite(v)) for v in d.values()): raise ValueError('nonfinite evidence')
    p=config['parameters']; target=output/'derived'; target.mkdir(parents=True)
    dirs=np.array(p['directions'],float); dirs/=np.linalg.norm(dirs,axis=1)[:,None]
    expected=np.concatenate([r*dirs for r in p['radii']])
    if not np.array_equal(expected,d['q']): raise ValueError('wavevector coverage mismatch')
    q=d['q']; spectrum=[]; diagnostics=[]; responses=[]; directional=[]; summaries={}
    periodic=conservation=refinement=ode_error=reference=phase_error=causal=domain=fft_error=0.; probe=1.
    for label in LABELS:
        inputs=d[f'{label}_inputs']; outputs=d[f'{label}_outputs']; maps=d[f'{label}_maps_1']; coarse=d[f'{label}_maps_0']
        if maps.shape!=(104,20,20) or inputs.shape!=(6,3,2): raise ValueError('physical dimensions missing')
        periodic=max(periodic,float(abs(outputs[-1,:2]-inputs[0,:2]).max()))
        for a,b in zip(inputs[:,2],outputs[:,2]): periodic=max(periodic,float(abs(np.outer(a,a.conj())-np.outer(b,b.conj())).max()))
        for pair in d[f'{label}_conservation']:
            values=[]
            for state in pair:
                z1,z2,w=state; delta=z1-z2; pr=np.outer(w,w.conj()); norm=np.vdot(z1,z1).real+np.vdot(z2,z2).real
                j=np.outer(z1,z1.conj())+np.outer(z2,z2.conj())+pr
                h=np.pi/2*abs(np.vdot(w,delta))**2
                values.append(np.r_[norm,np.vdot(w,w).real,h,j.ravel()])
            conservation=max(conservation,float(np.max(abs(values[0]-values[1])/(1+abs(values[0])))))
        ref=float(abs(maps-coarse).max()); refinement=max(refinement,ref)
        ode=float(abs(d[f'{label}_blocks_1']-d[f'{label}_ode_blocks']).max()); ode_error=max(ode_error,ode)
        a,b=d[f'{label}_phase_control']; phase_error=max(phase_error,float(abs(a[:2]-b[:2]).max()),float(abs(np.outer(a[2],a[2].conj())-np.outer(b[2],b[2].conj())).max()))
        a,b=d[f'{label}_physical_probe']; probe=min(probe,float(1-abs(np.vdot(a,b))**2))
        frozen=d[f'{label}_frozen_maps']; back=float(abs(maps-frozen).max())
        eigerr=0.; maxgrowth=0.; maxcondition=0.; mingap=1.; flat_min=20; pathgrowth=0.
        for kind,points,blocks in [('low',q,maps),('path',d['path'],d[f'{label}_path_maps'])]:
            for qi,(point,matrix) in enumerate(zip(points,blocks)):
                eig,vec=np.linalg.eig(matrix); growth=np.log(np.abs(eig)); phase=-np.angle(eig)
                part=np.sum(abs(vec[8:])**2,axis=0)/np.sum(abs(vec)**2,axis=0)
                order=np.argsort(phase)
                maxcondition=max(maxcondition,float(np.linalg.cond(vec)))
                if kind=='low':
                    eigerr=max(eigerr,paired_error(eig,np.linalg.eigvals(coarse[qi])))
                    maxgrowth=max(maxgrowth,float(growth.max())); flat_min=min(flat_min,int(np.sum(abs(eig-1)<2e-6)))
                else: pathgrowth=max(pathgrowth,float(growth.max()))
                for rank,j in enumerate(order): spectrum.append({'background':label,'set':kind,'point':qi,'branch_sorted':rank,'qx':point[0],'qy':point[1],'qz':point[2],'phase':phase[j],'growth':growth[j],'memory_participation':part[j]})
        # Two finite boxes independently restrict the same local causal history.
        small,large=p['box_sizes']; hs=d[f'{label}_impulse_{small}']; hl=d[f'{label}_impulse_{large}']; pad=(large-small)//2
        domain=max(domain,float(abs(hs-hl[:,pad:pad+small,pad:pad+small,pad:pad+small]).max()))
        grid=np.indices((small,small,small))-small//2; distance=np.max(abs(grid),axis=0)
        for t,field in enumerate(hs):
            causal=max(causal,float(abs(field[distance>t]).max(initial=0)))
            density=np.sum(field**2,axis=-1)
            for x in range(small): responses.append({'background':label,'cycle':t,'x':x-small//2,'wave_norm2':float(np.sum(field[x,:,:,:8]**2)),'memory_norm2':float(np.sum(field[x,:,:,8:]**2))})
        fq=2*np.pi*np.fft.fftfreq(small); points=np.array(np.meshgrid(fq,fq,fq,indexing='ij')).reshape(3,-1).T
        # Independent direct DFT of the saved one-cycle impulse at 26 probe q on box grid.
        center=small//2; axes=np.indices((small,small,small)).reshape(3,-1).T-center
        for k in points[::max(1,len(points)//26)]:
            measured=np.einsum('n,nj->j',np.exp(-1j*axes@k),hs[1].reshape(-1,20))
            # Construct full map from saved local Jacobians without invoking solver model.
            total=np.eye(20,dtype=complex)
            for i,block in enumerate(d[f'{label}_blocks_1']):
                indices=list(range(8))+[8+2*i,9+2*i]; tr=np.ones(20,complex)
                if i%2: tr[4:8]=np.exp(1j*k[i//2])
                layer=np.eye(20,dtype=complex); layer[np.ix_(indices,indices)]=block
                total=(layer*tr[None,:]/tr[:,None])@total
            fft_error=max(fft_error,float(abs(measured-total[:,8]).max()))
        summaries[label]={'step_map_error':ref,'ode_jacobian_error':ode,'backreaction_difference':back,'max_low_q_growth':maxgrowth,'max_path_growth':pathgrowth,'eigenvalue_refinement':eigerr,'minimum_unit_multiplicity':flat_min,'max_eigenvector_condition':maxcondition,
          'stability':'fail' if maxgrowth>max(1e-5,5*eigerr) else 'unresolved'}
        diagnostics.append({'background':label,**{k:v for k,v in summaries[label].items() if k!='stability'}})
    reference=max(float(abs(m-physical_reference(k)).max()) for k,m in zip(q,d['vacuum_maps_1']))
    memory=float(abs(d['vacuum_maps_1'][:,8:,8:]-np.eye(12)).max())
    wave=float(abs(d['vacuum_maps_1'][:,:8,:8]-np.eye(8)).max())
    # Test 11: invariant port sector A has U_A=product exp(+i q_i P_i).
    # Pair its upper unwrapped near-origin phase continuously via exact trace factor;
    # no switching among full-system eigenvalues to fit a preferred cone.
    for r in p['radii']:
        for i,direction in enumerate(dirs):
            plus=r*direction; minus=-plus
            phases=[]
            for point in [plus,minus]:
                u=np.eye(2,dtype=complex)
                for axis in range(3):
                    pr=(np.eye(2)+SIGMA[axis])/2
                    u=(np.eye(2)+(np.exp(1j*point[axis])-1)*pr)@u
                phases.append(float(np.max(-np.angle(np.linalg.eigvals(u)))))
            odd=(phases[0]-phases[1])/2; even=(phases[0]+phases[1])/2
            directional.append({'radius':r,'direction':i,'odd_over_radius':odd/r,'predicted_drift':-np.sum(direction)/2,'even_over_radius':even/r,'predicted_speed':.5})
    residuals={'periodicity':periodic,'conservation':conservation,'map_refinement':refinement,'ode_jacobian':ode_error,'vacuum_reference':reference,'phase_null':phase_error,'physical_overlap_change':probe,'outside_causal_support':causal,'box_difference':domain,'impulse_fourier':fft_error,'memory_identity':memory,'wave_nonidentity':wave}
    vals={'coverage':('pass',len(spectrum)), 'periodicity':('pass' if periodic<1e-10 else 'fail',periodic),'conservation':('pass' if conservation<1e-10 else 'fail',conservation),'linearization':('pass' if max(refinement,ode_error)<2e-6 else 'fail',max(refinement,ode_error)), 'vacuum-reference':('pass' if max(reference,memory)<2e-6 else 'fail',max(reference,memory)), 'phase-quotient':('pass' if phase_error<1e-10 and probe>1e-6 else 'fail',phase_error),'causal-domain':('pass' if max(causal,domain)<1e-10 and fft_error<2e-6 else 'fail',max(causal,domain,fft_error)), 'backreaction':('pass' if summaries['counter']['backreaction_difference']>1e-3 and max(summaries[k]['backreaction_difference'] for k in ['vacuum','equal'])<2e-6 else 'fail',summaries['counter']['backreaction_difference']), 'vacuum-common-cone':('fail' if memory<2e-6 and wave>1e-3 else 'unresolved',memory),'counter-stability':(summaries['counter']['stability'],summaries['counter']['max_low_q_growth'])}
    summary={'backgrounds':summaries,'residuals':residuals,'physical_dimensions':20,'memory_dimensions':12,'spectrum_rows':len(spectrum),'scope':'Strong all-sector vacuum/equal-background geometry rejected only when numerical controls pass. Counter background sampled stability distinct. Material/clock explanation and unsampled backgrounds unresolved.'}
    for name,rows in [('spectrum',spectrum),('diagnostics',diagnostics),('impulses',responses),('directional',directional)]: write_csv(target/f'{name}.csv',rows)
    write_json(target/'summary.json',summary)
    checks={'schema_version':'research-checks-v1','checks':[{'id':k,'status':status,'value':v,'evidence':'derived/summary.json'} for k,(status,v) in vals.items()]}; write_json(output/'checks.json',checks)
    return {'raw_source':raw.relative_to(run_path).as_posix(),'checks':checks,'summary':summary}
