"""Independent audit of immutable Test 5 local jets and controls."""
import csv
import numpy as np
from signal_space.models.continuum import lagrangian
from signal_space.runtime.io import read_json, write_json


def analyze(run_path,output,config):
    paths=sorted((run_path/'attempts').glob('*/raw/continuum.npz'))
    if len(paths)!=1: raise ValueError('expected exactly one saved local-jet attempt')
    raw=paths[0].parent
    with np.load(paths[0],allow_pickle=False) as d: arrays={k:d[k] for k in d.files}
    e=arrays['coframes'];f=arrays['fields'];grad=arrays['gradients'];jets=arrays['second_jets'];h=arrays['derivative_hessians'];roots=arrays['roots'];dirs=arrays['directions']
    n=config['parameters']['samples'];nd=config['parameters']['directions'];limit=config['analysis']['max_residual']
    if not (e.shape==(n,4,4) and f.shape==(n,6) and grad.shape==(n,6,4) and jets.shape==(n,6,4,4) and h.shape==(n,6,4,6,4) and roots.shape==(n,nd,6,2) and dirs.shape==(nd,3)):
        raise ValueError('saved sample dimensions incomplete')
    if not all(np.all(np.isfinite(a)) for a in arrays.values()): raise ValueError('nonfinite raw arrays')
    rows=[];characteristics=[];min_kinetic=np.inf;max_hessian=max_eq=max_root=max_det=0.
    sigma=np.array([np.eye(2),[[0,1],[1,0]],[[0,-1j],[1j,0]],[[1,0],[0,-1]]],complex)
    for i in range(n):
        # Independent inverse and determinant-polarized Hermitian coframe check.
        inverse=np.linalg.solve(e[i],np.eye(4))
        eta=np.diag([1.,-1.,-1.,-1.]);g_inv=inverse@eta@inverse.T
        op=np.einsum('am,aij->mij',e[i],sigma)
        g_op=np.empty((4,4))
        for mu in range(4):
            for nu in range(4):
                g_op[mu,nu]=(np.linalg.det(op[mu]+op[nu])-np.linalg.det(op[mu])-np.linalg.det(op[nu])).real/2
        max_det=max(max_det,float(np.max(abs(g_op-e[i].T@eta@e[i]))))
        s=np.dot(f[i,:4],f[i,:4])/2;z=1+.1*s
        field=np.array([1.,1.,1.,1.,z,1.]);min_kinetic=min(min_kinetic,z,1.)
        expected=np.einsum('ab,mn->ambn',np.diag(field),g_inv)
        h_error=float(np.max(abs(h[i]-expected))/max(1,float(np.max(abs(expected)))))
        max_hessian=max(max_hessian,h_error)
        lap=np.einsum('mn,amn->a',g_inv,jets[i]);agrad=grad[i,4]@g_inv@grad[i,4]
        grad_s=np.einsum('a,am->m',f[i,:4],grad[i,:4])
        zs=.1
        # Euler-Lagrange force from a complex-step derivative of the *action*.
        force=[]
        for a in range(6):
            shifted=f[i].astype(complex);shifted[a]+=1e-25j
            force.append(-np.imag(lagrangian(shifted,grad[i],g_inv))/1e-25)
        measured=np.r_[lap[:4]+np.array(force[:4]),z*lap[4]+zs*(grad_s@g_inv@grad[i,4]),lap[5]+force[5]]
        us=1-s+.75*s*s;v=1-.5*s+.25*s*s;vs=-.5+.5*s
        expected_eq=np.r_[lap[:4]+f[i,:4]*(us+.5*vs*f[i,5]**2-.5*zs*agrad),
                          z*lap[4]+zs*(grad_s@g_inv@grad[i,4]),lap[5]+v*f[i,5]+.1*f[i,5]**3]
        eq_error=float(np.max(abs(measured-expected_eq))/max(1,float(np.max(abs(expected_eq)))))
        max_eq=max(max_eq,eq_error)
        for j,k in enumerate(dirs):
            for a in range(6):
                for sign in range(2):
                    omega=roots[i,j,a,sign];x=np.r_[omega,k]
                    polynomial=float(x@g_inv@x)
                    root_error=max(abs(omega-roots[i,j,0,sign]),abs(polynomial))
                    max_root=max(max_root,root_error)
                    if i in (0,1,2,3):
                        characteristics.append({'sample':i,'direction':j,'field':a,'branch':sign,'omega':omega,'null_polynomial':polynomial,'z':z})
        rows.append({'sample':i,'condition_coframe':float(np.linalg.cond(e[i])),'z':z,'hessian_error':h_error,'equation_error':eq_error,
                     'lapse':e[i,0,0],'shift_x':float(-g_inv[0,1]/g_inv[0,0])})
    controls=read_json(raw/'controls.json')
    speed=controls['orientation_speed'];kt=controls['orientation_kt'];kx=controls['orientation_kx']
    control_error=abs(speed-np.sqrt(1/(1+.4*.6**2)))
    summary={'samples':n,'directions':nd,'sectors':6,'max_hessian_residual':max_hessian,'max_equation_residual':max_eq,
        'max_root_residual':max_root,'max_operator_metric_residual':max_det,'min_valid_field_kinetic_eigenvalue':min_kinetic,
        'negative_z_control_eigenvalue':controls['negative_z'],'orientation_control_speed':speed,
        'orientation_control_time_coefficient':kt,'orientation_control_space_coefficient':kx,
        'orientation_control_reference_error':control_error,'gravity_symbol_constraint_residual':controls['gravity_symbol_constraint_residual'],
        'gravity_scope':'flat linearized harmonic gauge TT symbol and constraints; nonlinear Einstein evolution/constraints not evaluated',
        'physical_scope':'common characteristic is chosen in SS OCF 1; local algebra is implementation evidence, not emergence'}
    values={'coverage':(True,n*nd*6*2),'hessian':(max(max_hessian,max_det)<limit,max(max_hessian,max_det)),
        'equations':(max_eq<limit,max_eq),'characteristics':(max_root<limit,max_root),
        'positive-kinetic':(min_kinetic>0 and controls['negative_z']<0,min_kinetic),
        'orientation-control':(speed<1-1e-3 and control_error<limit and kt>0 and kx>0,1-speed),
        'gravity-symbol':(controls['gravity_symbol_constraint_residual']<limit,controls['gravity_symbol_constraint_residual'])}
    derived=output/'derived';derived.mkdir(parents=True)
    for name,data in [('samples.csv',rows),('characteristics.csv',characteristics)]:
        with (derived/name).open('w',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(data[0]));writer.writeheader();writer.writerows(data)
    write_json(derived/'controls.json',controls);write_json(derived/'summary.json',summary)
    checks={'schema_version':'research-checks-v1','checks':[{'id':key,'status':'pass' if ok else 'fail','value':value,'evidence':'derived/summary.json'} for key,(ok,value) in values.items()]}
    write_json(output/'checks.json',checks)
    return {'raw_source':paths[0].relative_to(run_path).as_posix(),'checks':checks,'summary':summary}
