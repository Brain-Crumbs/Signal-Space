"""One-shot reservations for the fixed C1 campaign, not a new scheduler.

Reservations charge full ceilings (never unmeasured/zero CPU). Separate marker
files are atomic and immutable; failed stages still consume their reservation.
The campaign is scoped to one canonical experiment workspace. Copying a campaign
elsewhere is not a continuation or a way to replenish its budget.
"""
import os
from signal_space.runtime.io import canonical_bytes

RESERVATIONS={'pilot-worker':(45,45,8),'pilot-analysis':(15,15,8),
              'confirmation-worker':(190,190,96),'confirmation-analysis':(50,50,16)}


def reserve(run_path,stage):
    if stage not in RESERVATIONS:raise ValueError('unknown C1 stage')
    root=run_path.parent/'.c1-budget-v1';root.mkdir(exist_ok=True)
    cpu,wall,output=RESERVATIONS[stage]
    record=dict(stage=stage,run_id=run_path.name,reserved_cpu_seconds=cpu,
                reserved_wall_seconds=wall,reserved_output_mb=output)
    # EXCL, rather than exists()+write, prevents concurrent duplicate launches.
    fd=os.open(root/(stage+'.json'),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'wb') as f:f.write(canonical_bytes(record))
    return record


def analyze_saved(run_path,output,config):
    """Reuse runtime supervision; failed checker bytes survive parent cleanup."""
    import subprocess,sys,shutil,time
    from signal_space.runtime.runner import _monitor_process,_terminate_process
    from signal_space.runtime.execution import ExecutionPolicy
    from signal_space.runtime.processes import ProcessTree
    from signal_space.runtime.io import write_json,read_json,sha256_file
    reservation=reserve(run_path,'pilot-analysis')
    # Parent Runtime.analyze removes its output on failure. The one-shot stage
    # lives outside that target and is copied into canonical analysis on success.
    stage=run_path.parent/'.c1-analysis-attempts'/run_path.name/output.name
    stage.mkdir(parents=True,exist_ok=False)
    request=stage/'checker-request.json'
    write_json(request,dict(run_path=str(run_path),output=str(stage),config=config,reservation=reservation))
    limits=dict(max_cpu_seconds=14,max_wall_seconds=14,max_memory_mb=1024,max_output_mb=4)
    start=time.monotonic();proc=None;tree=None
    try:
        with (stage/'checker.log').open('wb') as log:
            env=dict(os.environ);env.update(ExecutionPolicy(threads=1,case_jobs=1).environment())
            proc=subprocess.Popen([sys.executable,'-m','signal_space.analysis.local_certificate',str(request)],
                    stdout=log,stderr=subprocess.STDOUT,env=env,start_new_session=os.name=='posix',
                    creationflags=getattr(subprocess,'CREATE_NEW_PROCESS_GROUP',0) if os.name=='nt' else 0)
            tree=ProcessTree(proc)
            reason,code=_monitor_process(proc,stage,limits)
            if reason!='completed' or code!=0:
                raise RuntimeError('saved-analysis stage failed: '+reason+' exit='+str(code))
        result=read_json(stage/'result.json')
        if sum(x.stat().st_size for x in stage.rglob('*') if x.is_file())>4*1024**2:
            raise RuntimeError('analysis staging output exceeds4MiB; duplicate copy must fit8MiB')
        shutil.copytree(stage,output)
        if time.monotonic()-start>15:raise RuntimeError('analysis aggregate15-second ceiling')
        return result
    except BaseException as exc:
        if proc is not None and proc.poll() is None:_terminate_process(proc,cooperative_seconds=0)
        write_json(stage/'failure.json',dict(error=type(exc).__name__+': '+str(exc),
            reservation=reservation,files={x.relative_to(stage).as_posix():sha256_file(x)
                for x in stage.rglob('*') if x.is_file()}))
        raise
    finally:
        if proc is not None and proc.poll() is None:_terminate_process(proc,cooperative_seconds=0)
        if tree is not None:tree.close()
