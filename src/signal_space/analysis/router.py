"""Independent quaternion/exponential audit of immutable stencil measurements."""
import csv
import itertools
import numpy as np
from scipy.linalg import expm
from signal_space.runtime.io import read_json, write_json

PAULI = np.array([[[0, 1], [1, 0]], [[0, -1j], [1j, 0]], [[1, 0], [0, -1]]])


def multiply(x, y):
    a, b = x; c, d = y
    return a*c - np.sum(b*d, axis=-1), a[..., None]*d + c[..., None]*b + np.cross(b, d)


def quaternion(q, triad, order, derivative=None):
    a, b = np.ones(q.shape[:-1]), np.zeros(q.shape)
    for axis in order:
        angle = q[..., axis]
        c, s = np.cos(angle), np.sin(angle)
        if axis == derivative:
            c, s = -s, c
        a, b = multiply((c, s[...,None]*triad[axis]), (a,b))
    return a,b


def reference_phase(q, triad, order):
    a,b = quaternion(q,triad,order)
    return np.arctan2(np.linalg.norm(b,axis=-1),a)


def reference_matrix(q, triad, order):
    a,b = quaternion(q,triad,order)
    return a[...,None,None]*np.eye(2) - 1j*np.einsum('...a,aij->...ij', b, PAULI)


def measured_phase(u):
    # Eigenvalues independently expose both bands; the positive magnitude is used.
    return np.max(np.abs(np.angle(np.linalg.eigvals(u))),axis=-1)


def write_csv(path, rows):
    with path.open('w', newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def analyze(run_path, output, config):
    paths=sorted((run_path/'attempts').glob('*/raw/router.npz'))
    if not paths: raise ValueError('missing router data')
    raw=paths[-1]
    with np.load(raw,allow_pickle=False) as f: data={k:f[k] for k in f.files}
    if any(not np.all(np.isfinite(v)) for v in data.values()): raise ValueError('nonfinite measurements')
    p=config['parameters']; limits=config['analysis']
    directions=np.array(p['directions'],float); directions/=np.linalg.norm(directions,axis=1)[:,None]
    expected_q=(np.array(p['radii'])[:,None,None]*directions[None,:,:]).reshape(-1,3)
    q=data['q']; radius=np.linalg.norm(q,axis=1)
    if not np.array_equal(q,expected_q): raise ValueError('wavevector coverage mismatch')
    target=output/'derived'; target.mkdir(parents=True,exist_ok=True)
    residuals={k:0. for k in ['fourier','unitarity','rotation','finite_band','field_fourier','norm','group_reference','group_refinement','zone_reference','zone_nested','node']}
    dispersion=[]; convergence=[]; group_rows=[]; node_rows=[]; field_rows=[]; zone_rows=[]; geometry=[]
    zone_data={'surface_q': data['surface_q']}
    worst_ratio=0.; worst_fine=0.; min_order_signal=float('inf')
    phases={}
    expected_keys={'q','directions','nodes','circle','rotation','surface_q'}
    for size in p['zone_sizes']: expected_keys.add(f'zone_q_{size}')
    for label in ['orthogonal', 'oblique', 'collinear']:
        n=np.array(p['triads'][label]); gram=n@n.T
        eigen=np.linalg.eigvalsh(gram)
        geometry.append({'triad':label,'gram':gram.tolist(),'eigenvalues':eigen.tolist(),'rank':int(np.linalg.matrix_rank(gram,tol=1e-10))})
        for order_label, order in p['orders'].items():
            key=f'{label}_{order_label}'
            expected_keys.update(f'{key}_{suffix}' for suffix in ['u','nodes','rotated','surface_phase'])
            u=data[f'{key}_u']
            if u.shape != (len(q),2,2): raise ValueError('matrix coverage mismatch')
            ref=[]
            for point in q:
                block=np.eye(2,dtype=complex)
                for axis in order: block=expm(-1j*point[axis]*np.einsum('a,aij->ij',n[axis],PAULI))@block
                ref.append(block)
            residuals['fourier']=max(residuals['fourier'],float(np.max(np.abs(u-ref))))
            residuals['unitarity']=max(residuals['unitarity'],float(np.max(np.abs(u.conj().swapaxes(-2,-1)@u-np.eye(2)))),float(np.max(np.abs(np.linalg.det(u)-1))))
            v=data['rotation']; residuals['rotation']=max(residuals['rotation'],float(np.max(np.abs(data[f'{key}_rotated']-v@u@v.conj().T))))
            omega=measured_phase(u); phases[key]=omega
            predicted=np.sqrt(np.maximum(0,np.einsum('...i,ij,...j->...',q,gram,q)))
            error=np.abs(omega**2-predicted**2)/radius**2
            envelope=[]
            for r in p['radii']:
                select=np.isclose(radius,r); e=float(max(error[select])); envelope.append(e)
                convergence.append({'triad':label,'order':order_label,'radius':r,'max_cone_error':e})
            worst_fine=max(worst_fine,envelope[0])
            for fine,coarse in zip(envelope[:-1],envelope[1:]):
                if coarse>1e-10: worst_ratio=max(worst_ratio,fine/coarse)
            a,b=quaternion(q,n,order); bnorm=np.linalg.norm(b,axis=-1)
            regular=bnorm>1e-6
            analytic_gradient=np.zeros_like(q)
            for axis in range(3):
                da,db=quaternion(q,n,order,axis)
                analytic_gradient[regular,axis]=(a[regular]*np.sum(b[regular]*db[regular],axis=-1)/bnorm[regular]-bnorm[regular]*da[regular])/(a[regular]**2+bnorm[regular]**2)
            grads=[]
            for h in p['derivative_steps']:
                expected_keys.add(f'{key}_gradient_{h}'); grad=data[f'{key}_gradient_{h}']; grads.append(grad)
                residuals['group_reference']=max(residuals['group_reference'],float(np.max(np.abs(grad[regular]-analytic_gradient[regular]))))
            residuals['group_refinement']=max(residuals['group_refinement'],float(np.max(np.abs(grads[0][regular]-grads[1][regular]))))
            for j,point in enumerate(q):
                dispersion.append({'triad':label,'order':order_label,'radius':float(radius[j]),'direction':j%len(directions),
                                   'qx':point[0],'qy':point[1],'qz':point[2],'phase':omega[j],'continuum':predicted[j],'cone_error':error[j]})
                if regular[j]:
                    continuum=gram@point/predicted[j] if predicted[j]>1e-12 else np.zeros(3)
                    group_rows.append({'triad':label,'order':order_label,'radius':radius[j],'direction':j%len(directions),
                        **{f'group_{axis}':grads[-1][j,k] for k,axis in enumerate('xyz')},
                        **{f'cone_{axis}':continuum[k] for k,axis in enumerate('xyz')}})
            if label=='orthogonal':
                sign=1 if order_label=='forward' else -1
                expected=np.prod(np.cos(q),axis=1)+sign*np.prod(np.sin(q),axis=1)
                residuals['finite_band']=max(residuals['finite_band'],float(np.max(np.abs(np.trace(u,axis1=-2,axis2=-1).real/2-expected))))
            for size in p['box_sizes']:
                for suffix in ['initial','final']: expected_keys.add(f'{key}_field_{size}_{suffix}')
                initial=data[f'{key}_field_{size}_initial']; final=data[f'{key}_field_{size}_final']
                if initial.shape!=(size,size,size,2) or final.shape!=initial.shape: raise ValueError('box shape mismatch')
                fq=2*np.pi*np.fft.fftfreq(size)
                grid=np.array(np.meshgrid(fq,fq,fq,indexing='ij')).transpose(1,2,3,0)
                block=reference_matrix(grid,n,order)
                reference=np.fft.ifftn(np.einsum('...ab,...b->...a',block,np.fft.fftn(initial,axes=(0,1,2))),axes=(0,1,2))
                ferr=float(np.linalg.norm(final-reference)); normerr=float(abs(np.vdot(final,final)-np.vdot(initial,initial)))
                residuals['field_fourier']=max(residuals['field_fourier'],ferr); residuals['norm']=max(residuals['norm'],normerr)
                field_rows.append({'triad':label,'order':order_label,'box_size':size,'norm_error':normerr,'fourier_error':ferr})
            for size in p['zone_sizes']:
                expected_keys.add(f'{key}_zone_{size}')
                grid=data[f'zone_q_{size}']; z=data[f'{key}_zone_{size}']
                ax=np.linspace(-np.pi,np.pi,size,endpoint=False)
                expected_grid=np.array(np.meshgrid(ax,ax,ax,indexing='ij')).reshape(3,-1).T
                if not np.array_equal(grid,expected_grid) or z.shape!=(size**3,): raise ValueError('zone coverage mismatch')
                residuals['zone_reference']=max(residuals['zone_reference'],float(np.max(np.abs(z-reference_phase(grid,n,order)))))
                zone_rows.append({'triad':label,'order':order_label,'size':size,'zero_nodes':int(np.sum(z<1e-10)),'pi_nodes':int(np.sum(np.pi-z<1e-10)), 'minimum':float(z.min()),'maximum':float(z.max())})
                zone_data[f'{key}_zone_{size}']=z
                zone_data[f'zone_q_{size}']=grid
            small,large=p['zone_sizes']
            residuals['zone_nested']=max(residuals['zone_nested'],float(np.max(np.abs(data[f'{key}_zone_{small}'].reshape(small,small,small)-data[f'{key}_zone_{large}'].reshape(large,large,large)[::2,::2,::2]))))
            measured=measured_phase(data[f'{key}_nodes']); refnodes=reference_phase(data['nodes'],n,order)
            residuals['node']=max(residuals['node'],float(np.max(np.abs(measured-refnodes))))
            for point,z in zip(data['nodes'],measured): node_rows.append({'triad':label,'order':order_label,'qx':point[0],'qy':point[1],'qz':point[2],'phase':z})
            surface=data[f'{key}_surface_phase']
            if surface.shape!=(101**2,): raise ValueError('surface coverage mismatch')
            residuals['zone_reference']=max(residuals['zone_reference'],float(np.max(np.abs(surface-reference_phase(data['surface_q'],n,order)))))
            zone_data[f'{key}_surface_phase']=surface
    if set(data)!=expected_keys: raise ValueError(f'array coverage mismatch: {set(data)^expected_keys}')
    for label in ['orthogonal','oblique']:
        delta=np.abs(phases[f'{label}_forward']-phases[f'{label}_reverse'])
        min_order_signal=min(min_order_signal,float(np.max(delta)))
    ranks=[g['rank'] for g in geometry]
    # Zone detections report sampled nodes only; no completeness/topological-charge claim.
    orth=[r for r in zone_rows if r['triad']=='orthogonal']
    extra=all(r['zero_nodes']>1 and r['pi_nodes']>0 for r in orth)
    vals={
        'coverage':(True,len(dispersion)),
        'fourier-circuit':(max(residuals['fourier'],residuals['field_fourier'])<limits['matrix_tolerance'],max(residuals['fourier'],residuals['field_fourier'])),
        'conservation':(max(residuals['norm'],residuals['unitarity'])<limits['matrix_tolerance'],max(residuals['norm'],residuals['unitarity'])),
        'continuum':(worst_fine<limits['fine_cone_error'] and worst_ratio<limits['convergence_ratio'],worst_fine),
        'triad-rank':(ranks==[3,3,1],ranks),
        'order-control':(residuals['finite_band']<limits['matrix_tolerance'] and min_order_signal>limits['min_order_signal'],min_order_signal),
        'rotation':(residuals['rotation']<limits['matrix_tolerance'],residuals['rotation']),
        'group-refinement':(max(residuals['group_reference'],residuals['group_refinement'])<limits['gradient_tolerance'],max(residuals['group_reference'],residuals['group_refinement'])),
        'full-zone':(max(residuals['zone_reference'],residuals['zone_nested'],residuals['node'])<limits['matrix_tolerance'] and extra, max(residuals['zone_reference'],residuals['zone_nested'],residuals['node']))}
    for name,rows in [('dispersion',dispersion),('convergence',convergence),('groups',group_rows),('nodes',node_rows),('fields',field_rows),('zones',zone_rows)]: write_csv(target/f'{name}.csv',rows)
    write_json(target/'geometry.json',geometry)
    np.savez_compressed(target/'surfaces.npz',**zone_data)
    summary={'residuals':residuals,'worst_cone_error_fine':worst_fine,'worst_convergence_ratio':worst_ratio,'minimum_order_signal':min_order_signal,'samples':len(dispersion),'geometry':geometry,'zone_counts':zone_rows,
             'group_exclusions':'Analytic and numerical group velocity undefined at band touchings; points with quaternion vector norm <=1e-6 excluded explicitly.',
             'scope':'Wave sector only; stationary physical memory modes belong to Test 4. No clock or detector record.'}
    write_json(target/'summary.json',summary)
    checks={'schema_version':'research-checks-v1','checks':[{'id':k,'status':'pass' if bool(ok) else 'fail','value':value,'evidence':'derived/summary.json'} for k,(ok,value) in vals.items()]}
    write_json(output/'checks.json',checks)
    return {'raw_source':raw.relative_to(run_path).as_posix(),'checks':checks,'summary':summary}
