"""Post-hoc decomposition; does not alter or replace preregistered acceptance."""
import argparse,json
from pathlib import Path
import numpy as np
from signal_space.analysis.reception import phase,markers,interval
p=argparse.ArgumentParser();p.add_argument('--raw',type=Path,required=True);p.add_argument('--config',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
params=json.loads(args.config.read_text())['parameters'];rec=np.load(args.raw/'receiver-finer.npz')['records'];pred=np.load(args.raw/'prediction-finer.npz')['records'];t=rec[:,0,0];omega=params['omega_chi'];rows=[]
for j in (2,5,6,9):
 c=params['cases'][j];base=rec[:,c['baseline']];q=pred[:,c['prediction']];A=c['amplitude']
 actual_events=markers(t,rec[:,j,3],params['marker_threshold']);forecast_events=markers(t,A*q[:,3],params['marker_threshold'])
 ph=phase(rec[:,j,1],rec[:,j,2],omega)-phase(base[:,1],base[:,2],omega)
 dp=A*A*(q[:,2]*q[:,9]-q[:,1]*q[:,10])/(omega*(q[:,1]**2+(q[:,2]/omega)**2))
 actual=interval(t,ph,actual_events);forecast=interval(t,dp,forecast_events);matched=interval(t,dp,actual_events)
 rows.append(dict(case=c['name'],actual=actual,standalone_prediction=forecast,diagnostic_prediction_at_actual_events=matched,response_component=actual-matched,marker_component=matched-forecast,relative_error=abs(actual-forecast)/abs(actual)))
events=markers(t,rec[:,2,3],params['marker_threshold']);q=pred[:,0];amplitudes=[]
for j in (1,2,3):
 A=params['cases'][j]['amplitude'];ph=phase(rec[:,j,1],rec[:,j,2],omega)-phase(rec[:,0,1],rec[:,0,2],omega)
 dp=A*A*(q[:,2]*q[:,9]-q[:,1]*q[:,10])/(omega*(q[:,1]**2+(q[:,2]/omega)**2));error=interval(t,ph-dp,events)
 amplitudes.append(dict(amplitude=A,error_at_fixed_nominal_events=error,error_over_A2=error/A**2,error_over_A4=error/A**4))
args.output.write_text(json.dumps({'status':'post-hoc diagnostic; never used to change locked classification','rows':rows,'fixed_nominal_marker_amplitude_diagnostic':amplitudes},indent=2)+'\n')
