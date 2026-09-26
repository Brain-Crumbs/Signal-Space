"""Evaluate the locked absolute discrimination budget without a fitted term."""
import json
import numpy as np
from scipy.interpolate import CubicSpline
from signal_space.analysis.reception_order4 import hermite_markers
from signal_space.analysis.clock import save_csv
from signal_space.numerics.prereception import digest, ROOT
from signal_space.runtime.io import read_json, write_json


def interval(t,phase,events):
    if events is None:return None
    s=CubicSpline(t,phase);return float(s(events[1])-s(events[0]))


def evaluate(jet,rec,A,p,stride=1):
    jet=jet[::stride];rec=rec[::stride];t=jet[:,0];omega=p['omega_chi']
    z0=jet[:,1]-1j*jet[:,2]/omega;z2=jet[:,3]-1j*jet[:,4]/omega;z4=jet[:,5]-1j*jet[:,6]/omega
    second=A*A*np.imag(z2/z0)/(2*np.pi)
    fourth=second+A**4*np.imag(z4/z0-.5*(z2/z0)**2)/(2*np.pi)
    z=rec[:,:,1]-1j*rec[:,:,2]/omega
    actual=np.unwrap(np.angle(z[:,1]/z[:,0]))/(2*np.pi)
    neutral=A*jet[:,7]+A**3*jet[:,9];velocity=A*jet[:,8]+A**3*jet[:,10]
    pred=hermite_markers(t,neutral,velocity,p['marker_threshold'])
    measured=hermite_markers(t,rec[:,1,3],rec[:,1,4],p['marker_threshold'])
    data={'amplitude':A,'actual':interval(t,actual,measured),'second':interval(t,second,pred),'fourth':interval(t,fourth,pred),
          'marker_actual':measured,'marker_prediction':pred,
          'trace2_relative':float(np.linalg.norm(actual-second)/np.linalg.norm(actual)),
          'trace4_relative':float(np.linalg.norm(actual-fourth)/np.linalg.norm(actual))}
    return data,{'time':t,'actual_cycles':actual,'second_cycles':second,'fourth_cycles':fourth,'actual_a':rec[:,1,3],'predicted_a':neutral}



def transfer_audit(raw,p):
    """Post-lock known-source audit, never a new response prediction."""
    from signal_space.numerics.prereception import RadialSystem
    from signal_space.numerics.reception_transfer import incident, acquire_surface
    summary={};rows=[]
    for name,wave_name in [('finest','broad'),('finest','carrier'),('time','carrier')]:
        variant=next(x for x in p['variants'] if x['name']==name)
        wave=next(x for x in p['waveforms'] if x['name']==wave_name);tag=name+'-'+wave_name
        with np.load(raw/f'profile-{name}.npz') as d:r=d['r'];u=d['u']
        system=RadialSystem(r,p['epsilon']);b,v=incident(system.r,wave,variant['h'])
        with np.load(raw/f'input-{tag}.npz') as d:rb=d['b'];rv=d['v']
        original=acquire_surface(system,u,b,v,variant['dt'],p['duration'],p['sample_interval'],p['local_radius'])
        inverse=acquire_surface(system,u,rb,rv,variant['dt'],p['duration'],p['sample_interval'],p['local_radius'])
        A=p['nominal_amplitude'];scale=A/p['local_radius'];t=original[:,0]
        true_markers=hermite_markers(t,scale*original[:,1],scale*original[:,2],p['marker_threshold'])
        inverse_markers=hermite_markers(t,scale*inverse[:,1],scale*inverse[:,2],p['marker_threshold'])
        summary[tag]={'max_local_a_error':float(np.max(abs(scale*(original[:,1]-inverse[:,1])))),
            'relative_local_l2':float(np.linalg.norm(original[:,1]-inverse[:,1])/np.linalg.norm(original[:,1])),
            'source_markers':true_markers,'inverse_markers':inverse_markers,
            'marker_difference':(np.asarray(inverse_markers)-true_markers).tolist() if true_markers and inverse_markers else None}
        rows.extend({'case':tag,'time':float(ti),'source_a':float(scale*x),'inverse_a':float(scale*y)} for ti,x,y in zip(t,original[:,1],inverse[:,1]))
    return {'role':'post-hoc diagnostic using known source; no acceptance reclassification','cases':summary},rows


def analyze(run_path,output,config):
    p=config['parameters'];raw=next((run_path/'attempts').glob('*/raw'));derived=output/'derived';derived.mkdir(parents=True)
    events=[json.loads(x) for x in (raw.parent/'events.jsonl').read_text().splitlines()]
    locks=read_json(raw/'prediction-lock.json');index=next(i for i,x in enumerate(events) if x['type']=='all-predictions-locked')
    valid=index<min(i for i,x in enumerate(events) if x['type']=='receiver-started')
    valid=valid and digest(raw/'forecast-markers-and-intervals.json')==locks['forecast_sha256']
    for item in locks['files']:
        valid=valid and all(digest(raw/f'{k}-{item["case"]}.npz')==item[k] for k in ('surface','input','prediction'))
        valid=valid and digest(raw/f'profile-{item["case"].split("-")[0]}.npz')==item['profile']
    valid=valid and all(digest(ROOT/s['path'])==s['sha256'] for s in p['frozen_inputs'])
    checks=[]
    def check(key,ok,value,unresolved=False):
        checks.append({'id':key,'status':'unresolved' if unresolved else ('pass' if ok else 'fail'),'value':value,'evidence':'derived/summary.json'})
    check('prediction-first',valid,{'hashes_and_order':valid})
    profiles={};profile_rows=[]
    for v in p['variants']:
        name=v['name'];info=read_json(raw/f'profile-{name}.json');profiles[name]=info
        with np.load(raw/f'profile-{name}.npz') as d:
            r=d['r'][1:-1];u=d['u'];mode=d['mode'];Z=d['Z']
            for i in range(0,len(r),max(1,round(.05/v['h']))):
                if r[i]<=20:profile_rows.append({'grid':name,'r':float(r[i]),'phi':float(u[i]/r[i]),'Z':float(Z[i]),'mode':float(mode[i]/r[i])})
    primary=('base','fine','finer','finest')
    eig=[profiles[k]['eigenvalues'][0] for k in primary]
    residuals={k:profiles[k]['attempts'][-1]['discrete_residual'] for k in primary}
    check('profile-refinement',max(residuals.values())<2e-10 and abs(eig[3]-eig[2])<=.6*abs(eig[2]-eig[1]),{'residuals':residuals,'eigenvalues':eig})
    metrics={};traces=[];surfaces=[];inversion={}
    for variant in p['variants']:
        for wave in p['waveforms']:
            tag=variant['name']+'-'+wave['name'];jet=np.load(raw/f'prediction-{tag}.npz')['records'];rec=np.load(raw/f'receiver-{tag}.npz')['records']
            inverse=read_json(raw/f'inverse-{tag}.json');inversion[tag]={k:v for k,v in inverse.items() if k!='singular_values'}
            inversion[tag]['source_audit']=read_json(raw/f'input-audit-{tag}.json')
            metrics[tag]=[]
            for j,A in enumerate(p['amplitudes'],1):
                row,trace=evaluate(jet,rec[:,[0,j]],A,p)
                down,_=evaluate(jet,rec[:,[0,j]],A,p,2)
                row['sampling']=down
                row['charge_relative']=float(np.max(abs(rec[:,j,6]-rec[0,j,6]))/abs(rec[0,j,6]))
                row['energy_relative']=float(np.max(abs(rec[:,j,5]-rec[0,j,5]))/abs(rec[0,j,5]-rec[0,0,5]))
                metrics[tag].append(row)
                if A==p['nominal_amplitude']:
                    for k in range(len(jet)):traces.append({'case':tag,**{key:float(val[k]) for key,val in trace.items()}})
            if variant['name']=='finest':
                surface=np.load(raw/f'surface-{tag}.npz')['records']
                for t,b,bt in surface:surfaces.append({'waveform':wave['name'],'time':float(t),'a':float(p['nominal_amplitude']*b/p['upstream_radius']),'a_dot':float(p['nominal_amplitude']*bt/p['upstream_radius'])})
    check('surface-inverse',all(x['relative_surface_residual']<1e-7 for x in inversion.values()),inversion)
    j=p['amplitudes'].index(p['nominal_amplitude']);budgets={};converged=[];resolved=[];accepted=[];timings={}
    def distance(a,b):return float(np.max(abs(np.asarray(a)-np.asarray(b))))
    present=all(x['marker_actual'] is not None and x['marker_prediction'] is not None for rows in metrics.values() for x in rows)
    all_timing=[]
    if present:
        for rows in metrics.values():
            all_timing.extend(distance(x['marker_actual'],x['marker_prediction']) for x in rows)
    for wave in p['waveforms']:
        name=wave['name'];get=lambda grid:metrics[grid+'-'+name][j]
        if not present:
            budgets[name]={'missing_markers':True};converged.append(False);resolved.append(False);accepted.append(False);continue
        x=get('finest');f=get('finer');g=get('fine');t=get('time');w=get('wide');inv=get('inverse')
        parts={'mesh':abs(x['actual']-f['actual']),'time':abs(x['actual']-t['actual']),
            'domain':abs(w['actual']-f['actual']),'inverse':abs(x['fourth']-inv['fourth']),
            'sampling':max(abs(x['actual']-x['sampling']['actual']),abs(x['fourth']-x['sampling']['fourth'])),
            'floor':p['cycle_noise_floor']}
        B=sum(parts.values());gap=abs(x['fourth']-x['second']);previous=abs(f['actual']-g['actual'])
        convergence=parts['mesh']<=.6*previous+B-parts['mesh'];resolution=B<=gap/4 and abs(x['actual'])>5*B
        e2=abs(x['actual']-x['second']);e4=abs(x['actual']-x['fourth'])
        budgets[name]={'components':parts,'total':B,'order_separation':gap,'maximum_discrimination_budget':gap/4,
            'previous_mesh_change':previous,'converged':convergence,'resolved':resolution,
            'actual':x['actual'],'second':x['second'],'fourth':x['fourth'],'second_error':e2,'fourth_error':e4,
            'fourth_error_over_budget':e4/B,'correction_snr':gap/B}
        converged.append(convergence);resolved.append(resolution);accepted.append(e4<=B and e2>3*B)
        mparts={'mesh':distance(x['marker_actual'],f['marker_actual']),'time':distance(x['marker_actual'],t['marker_actual']),
            'domain':distance(w['marker_actual'],f['marker_actual']),'inverse':distance(x['marker_prediction'],inv['marker_prediction']),
            'sampling':max(distance(x['marker_actual'],x['sampling']['marker_actual']),distance(x['marker_prediction'],x['sampling']['marker_prediction'])),
            'floor':p['marker_noise_floor']}
        mb=sum(mparts.values());error=distance(x['marker_actual'],x['marker_prediction']);earlier=distance(g['marker_actual'],g['marker_prediction'])
        timings[name]={'components':mparts,'budget':mb,'finest_error':error,'fine_error':earlier,'within_budget':error<=mb,'decreased_or_below_budget':error<=.8*earlier or error<=mb}
    check('continuum-convergence',all(converged),budgets,not all(converged))
    check('order-resolution',all(resolved),budgets,not all(resolved))
    eligible=all(converged) and all(resolved)
    # A resolved failure in either spectrum rejects the extended approximation,
    # even if the other spectrum lacks resolution.
    resolved_failure=any(c and r and not a for c,r,a in zip(converged,resolved,accepted))
    check('fourth-order-prediction',all(accepted),budgets,not eligible and not resolved_failure)
    timing_ok=present and max(all_timing)<=p['marker_time_tolerance'] and all(x['within_budget'] and x['decreased_or_below_budget'] for x in timings.values())
    check('marker-transfer',timing_ok,{'all_case_max':max(all_timing) if all_timing else None,'nominal':timings},not present)
    signs=[]
    for wave in p['waveforms']:
        rows=metrics['finest-'+wave['name']];plus=rows[1];minus=rows[2]
        signs.append(present and distance(plus['marker_actual'],minus['marker_actual'])<1e-9 and abs(plus['actual']-minus['actual'])<1e-10)
    check('sign-even',all(signs),{'by_spectrum':signs},not present)
    energy=max(x['energy_relative'] for rows in metrics.values() for x in rows);charge=max(x['charge_relative'] for rows in metrics.values() for x in rows)
    check('conservation',energy<.01 and charge<1e-5,{'energy_relative':energy,'charge_relative':charge})
    summary={'metrics':metrics,'budgets':budgets,'timing_budgets':timings,'profiles':profiles,'inversion':inversion,'checks':{x['id']:x['status'] for x in checks},
        'claim_scope':'discrete incoming preparation, known support, synthetic linear surface; original Test 7 unchanged'}
    # These post-lock diagnostics preserve all nine original check outcomes.
    forecast_audit={}
    for wave in p['waveforms']:
        name=wave['name'];get=lambda grid:metrics[grid+'-'+name][j]
        if not present:continue
        x=get('finest');f=get('finer');g=get('fine');t=get('time');w=get('wide')
        prediction_changes={'mesh':abs(x['fourth']-f['fourth']),
            'previous_mesh':abs(f['fourth']-g['fourth']),'time':abs(x['fourth']-t['fourth']),
            'domain':abs(w['fourth']-f['fourth'])}
        old=budgets[name]['components'];augmented=dict(old)
        for key in ('mesh','time','domain'):augmented[key]=max(old[key],prediction_changes[key])
        forecast_audit[name]={'role':'post-hoc diagnostic; cannot promote a locked result',
            'prediction_changes':prediction_changes,'forecast_inclusive_components':augmented,
            'forecast_inclusive_budget':sum(augmented.values()),
            'quarter_order_separation':budgets[name]['maximum_discrimination_budget'],
            'discrimination_resolved':sum(augmented.values())<=budgets[name]['maximum_discrimination_budget']}
    summary['forecast_convergence_audit']=forecast_audit
    summary['transfer_oracle_audit'],audit_rows=transfer_audit(raw,p)
    save_csv(derived/'transfer-audit.csv',audit_rows)
    save_csv(derived/'traces.csv',traces);save_csv(derived/'surface.csv',surfaces);save_csv(derived/'profiles.csv',profile_rows)
    write_json(derived/'summary.json',summary);out={'schema_version':'research-checks-v1','checks':checks};write_json(output/'checks.json',out)
    return {'raw_source':str(raw.relative_to(run_path)/'execution.json'),'checks':out,'summary':summary}
