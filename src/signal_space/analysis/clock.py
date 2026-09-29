"""Read saved Test 6 bytes; never rerun the profile or evolution solver."""
import csv
import numpy as np
from signal_space.runtime.io import read_json, write_json

RECORD_COLUMNS=('time','local_chi','mode_coordinate','mode_momentum','mode_energy_fraction',
                'charge_fraction','charge_balance_fraction','total_energy','outer_energy_sink','core_peak')


def oscillation(data):
    t=data[:,0];y=data[:,1]
    indices=np.flatnonzero((y[:-1]<0)&(y[1:]>=0))
    if len(indices)<2:return {'signed_cycles':0.,'frequency':None,'crossings':int(len(indices))}
    crossings=t[indices]-y[indices]*(t[indices+1]-t[indices])/(y[indices+1]-y[indices])
    gaps=np.diff(crossings)
    return {'signed_cycles':float((t[-1]-t[0])/np.median(gaps)),
            'measured_intervals':int(len(gaps)), 'crossings':int(len(indices)),
            'frequency':float(2*np.pi/np.median(gaps)),
            'early_frequency':float(2*np.pi/np.median(gaps[:max(1,len(gaps)//4)])),
            'late_frequency':float(2*np.pi/np.median(gaps[-max(1,len(gaps)//4):])),
            'last_crossing':float(crossings[-1])}


def save_csv(path, rows):
    if not rows: return
    with path.open('w',newline='') as stream:
        keys=list(dict.fromkeys(key for row in rows for key in row))
        writer=csv.DictWriter(stream,fieldnames=keys);writer.writeheader();writer.writerows(rows)


def analyze(run_path,output,config):
    attempts=sorted((run_path/'attempts').glob('*/raw/execution.json'))
    if len(attempts)!=1:raise ValueError('expected one terminal Test 6 attempt')
    raw=attempts[0].parent; execution=read_json(attempts[0]);profiles=read_json(raw/'profiles.json')
    derived=output/'derived';derived.mkdir(parents=True)
    selected=execution['selection'];p=config['parameters'];limits=config['analysis'];checks=[]
    def check(key,pass_condition,value,status=None):
        checks.append({'id':key,'status':status or ('pass' if pass_condition else 'fail'),
                       'value':value,'evidence':'derived/summary.json'})
    solved=[row for row in profiles if row['profile']=='solved']
    summary={'trial_profiles':profiles,'selection':selected,'scope':'flat spherical matter, a=0; no Einstein evolution',
             'unresolved_profile_samples':execution['failures']}
    save_csv(derived/'profiles.csv',[{k:v for k,v in row.items() if k!='hessians'} for row in profiles])
    if selected is None:
        check('profiles',False,len(solved),status='unresolved' if execution['failures'] else 'fail')
        for key in ('core-energetics','bound-spectrum','trapping-control','grid-domain','branch-screen',
                    'local-record','lifetime','amplitude','charge-ledger'):
            check(key,False,None,status='unresolved')
        write_json(derived/'summary.json',summary)
        out={'schema_version':'research-checks-v1','checks':checks};write_json(output/'checks.json',out)
        return {'raw_source':attempts[0].relative_to(run_path).as_posix(),'checks':out,'summary':summary}
    row=next(x for x in solved if f"{x['omega']:.3f}"==selected)
    with np.load(raw/f'profile-{selected}.npz',allow_pickle=False) as d:
        r,u,mode,well=(d[x] for x in ('r','u','mode','well'))
    eig=row['eigenvalue'];omega=row['omega']
    radial=[{'radius':float(rr),'core':float(u[i-1]/rr) if 0<i<len(r)-1 else 0.,
             'well':float(well[i-1]) if 0<i<len(r)-1 else .25,
             'mode':float(mode[i-1]/rr) if 0<i<len(r)-1 else 0.}
            for i,rr in enumerate(r)]
    radial[0]['core']=radial[1]['core'];radial[0]['mode']=radial[1]['mode']
    save_csv(derived/'radial.csv',radial)
    refinements=read_json(raw/'refinements.json');nulls=read_json(raw/'controls.json')
    save_csv(derived/'refinements.csv',refinements)
    fine=next((x for x in refinements if x['label']=='fine' and x['status']=='solved'),None)
    wide=next((x for x in refinements if x['label']=='wide' and x['status']=='solved'),None)
    eigen_error=(max(abs(eig-fine['eigenvalue'])/3,abs(eig-wide['eigenvalue']))
                 if fine and wide else None)
    rows=[];observations={}
    evolutions=read_json(raw/'evolutions.json')
    for item in evolutions:
        label=item.get('refinement',f"{item['amplitude']:.4f}")
        path=raw/f'evolution-{label}.npz'
        with np.load(path,allow_pickle=False) as d: trace=d['records']
        if not np.isfinite(trace).all():raise ValueError('nonfinite evolution trace')
        observations[label]={**oscillation(trace),'duration':float(trace[-1,0]),
          'last_mode_energy_fraction':float(trace[-1,4]),
          'max_charge_balance_error':float(np.max(abs(trace[:,6]))),
          'last_charge_balance_error':float(trace[-1,6]),
          'max_core_peak_shift':float(np.max(abs(trace[:,9]-trace[0,9]))/trace[0,9]),
          'outer_energy_sink':float(trace[-1,8]),'total_energy_start':float(trace[0,7]),
          'total_energy_end':float(trace[-1,7]),'max_local_chi':float(np.max(abs(trace[:,1])))}
        # Exact downsampled display data; the full unsmoothed sampled trace stays raw.
        for values in trace:
            rows.append({'preparation':label,**dict(zip(RECORD_COLUMNS,map(float,values)))})
    save_csv(derived/'evolutions.csv',rows)
    base=observations['0.0010'];zero=observations['0.0000'];half=observations['0.0005'];double=observations['0.0020']
    spectral=np.sqrt(eig)
    relative_error=abs(base['frequency']-spectral)/spectral
    frequency_shift=max(abs(half['frequency']-base['frequency']),abs(double['frequency']-base['frequency']))/base['frequency']
    convergence=(max(abs(observations['fine']['frequency']-base['frequency']),
                     abs(observations['wide']['frequency']-base['frequency']))/base['frequency']
                 if fine and wide else None)
    mode_loss=1-base['last_mode_energy_fraction']
    nominal_mode_start=next(item['initial_mode_energy'] for item in evolutions
                            if item['amplitude']==p['amplitudes'][1] and 'refinement' not in item)
    energy_balance=(base['total_energy_end']+base['outer_energy_sink']-base['total_energy_start'])
    core_slope=None
    ordered=sorted(solved,key=lambda x:x['omega'])
    adjacent=next((x for x in ordered if x['omega']>omega),None)
    if adjacent:core_slope=(adjacent['Q']-row['Q'])/(adjacent['omega']-omega)
    lplus0=row['hessians']['Lplus_l0'];lminus0=row['hessians']['Lminus_l0'];lplus1=row['hessians']['Lplus_l1']
    screen=(core_slope is not None and core_slope<0 and lplus0[0]<0 and lplus0[1]>0
            and abs(lminus0[0])<0.03 and abs(lplus1[0])<0.03
            and base['max_core_peak_shift']<.01)
    summary.update({'selected_profile':row,'refinements':refinements,'controls':nulls,
                    'observations':observations,'omega_chi':spectral,
                    'eigen_error_estimate':eigen_error,'relative_frequency_error':relative_error,
                    'frequency_shift_fraction':frequency_shift,
                    'frequency_convergence_fraction':convergence,'mode_energy_loss_fraction':mode_loss,
                    'nominal_mode_initial_energy':nominal_mode_start,
                    'total_energy_plus_sink_residual':energy_balance,
                    'energy_residual_over_clock_mode':energy_balance/nominal_mode_start,
                    'outer_sink_over_clock_mode':base['outer_energy_sink']/nominal_mode_start,
                    'charge_slope_estimate':core_slope,'radial_branch_screen':screen,
                    'unassessed_stability':'l>=2, nonspherical and nonlinear fragmentation not tested'})
    check('profiles',len(profiles)==4 and row['profile_residual']<limits['profile_residual_max']
          and row['tail_at_three_quarters']<limits['tail_max'] and row['center']>0,{
          'attempted':len(profiles),'solved':len(solved),'selected_residual':row['profile_residual'],
          'tail':row['tail_at_three_quarters']})
    check('core-energetics',row['E_over_Q']<1,{'E_over_Q':row['E_over_Q'],'Q':row['Q']})
    check('bound-spectrum',eigen_error is not None and 0<eig<.25 and
          min(eig,.25-eig)>limits['bound_margin_factor']*eigen_error,
          {'eigenvalue':eig,'omega':spectral,'error_estimate':eigen_error,'threshold':.25},
          status='unresolved' if eigen_error is None else None)
    check('trapping-control',nulls['nu-off']['eigenvalue']>=.25 and
          zero['max_local_chi']==0 and zero['crossings']==0,
          {'nu_off_eigenvalue':nulls['nu-off']['eigenvalue'],'zero_field':zero['max_local_chi']})
    check('grid-domain',convergence is not None and convergence<limits['convergence_relative_max'] and
          abs(eig-fine['eigenvalue'])/eig<limits['convergence_relative_max'] and
          abs(eig-wide['eigenvalue'])/eig<limits['convergence_relative_max'],
          {'frequency_difference':convergence,'eigen_error':eigen_error},
          status='unresolved' if convergence is None else None)
    check('branch-screen',screen,{'Q_slope':core_slope,'Lplus_l0':lplus0,
          'Lminus_l0':lminus0,'Lplus_l1':lplus1,'core_peak_shift':base['max_core_peak_shift']},
          status='unresolved' if core_slope is None else None)
    check('local-record',base['signed_cycles']>=99.3 and relative_error<limits['frequency_relative_max']
          and base['crossings']>=99,
          {'cycles':base['signed_cycles'],'local_frequency':base['frequency'],
           'eigen_frequency':spectral,'relative_error':relative_error})
    check('lifetime',mode_loss<limits['mode_energy_loss_max'] and mode_loss>-limits['mode_energy_loss_max'],
          {'mode_energy_loss':mode_loss,'outer_sink':base['outer_energy_sink']})
    check('amplitude',frequency_shift<limits['amplitude_shift_max'],
          {'half':half['frequency'],'nominal':base['frequency'],'double':double['frequency'],
           'max_fractional_shift':frequency_shift})
    check('charge-ledger',base['max_charge_balance_error']<limits['charge_drift_max'],
          {'max_charge_drift_after_sink':base['max_charge_balance_error'],
           'last_drift':base['last_charge_balance_error']})
    write_json(derived/'summary.json',summary)
    out={'schema_version':'research-checks-v1','checks':checks};write_json(output/'checks.json',out)
    return {'raw_source':attempts[0].relative_to(run_path).as_posix(),'checks':out,'summary':summary}
