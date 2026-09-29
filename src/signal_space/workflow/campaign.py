"""Persistent dependency-aware campaigns with scientific gates and bounded admission."""
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from copy import deepcopy
from pathlib import Path
import threading
import time

from signal_space.runtime.events import _locked
from signal_space.runtime.execution import ExecutionPolicy
from signal_space.runtime.io import read_json, write_json, canonical_bytes, sha256_bytes, sha256_file, now, safe_child
from signal_space.runtime.scheduler import Budget
from signal_space.runtime.package import code_identity, execution_identity
from signal_space.workflow.plans import ROOT, load_plan
from signal_space.workflow.pipeline import Pipeline
from signal_space.workflow.preflight import check, profile
from signal_space.workflow.artifacts import verify_pipeline, handoff


def _closed(value, required, optional=()):
    if not isinstance(value,dict) or not set(required).issubset(value) or set(value)-set(required)-set(optional):
        raise ValueError(f'campaign object requires {sorted(required)}; unknown/missing keys')


def lock_value(design):
    return sha256_bytes(canonical_bytes({k:v for k,v in design.items() if k!='locked_sha256'}))


def resolve_design(value):
    path=Path(value)
    if not path.is_file(): path=ROOT/'docs/research/campaigns'/f'{value}.json'
    path=path.resolve(); design=read_json(path)
    _closed(design,{'schema_version','campaign_id','question','nodes','requires_capabilities','locked_sha256'})
    if design['schema_version']!='gross-campaign-v1' or design['locked_sha256']!=lock_value(design):
        raise ValueError('campaign lock mismatch; validate and lock an explicit new design')
    if not isinstance(design['nodes'],list) or not design['nodes']: raise ValueError('campaign needs nodes')
    import re
    ids=[]; configs={}; plans={}
    for node in design['nodes']:
        _closed(node,{'id','plan','dependencies'}, {'reuse_from','cost_profile'})
        if not isinstance(node['id'],str) or not re.fullmatch(r'[a-z0-9][a-z0-9_-]*',node['id']): raise ValueError('unsafe campaign node id')
        ids.append(node['id'])
        plan_path=Path(node['plan'])
        if not plan_path.is_absolute():
            plan_path=(path.parent/plan_path) if (path.parent/plan_path).is_file() else (ROOT/plan_path)
        plans[node['id']]=plan_path.resolve()
        _,configs[node['id']],_=load_plan(plan_path)
        if not isinstance(node['dependencies'],list): raise ValueError('dependencies must be an array')
        for dep in node['dependencies']:
            _closed(dep,{'node','classifications','checks'})
            if not isinstance(dep['checks'],list) or not all(isinstance(x,str) for x in dep['checks']): raise ValueError('dependency checks must be named criteria')
            if not isinstance(dep['classifications'],list) or not set(dep['classifications'])<= {'pass','fail','unresolved','not-evaluated'}:
                raise ValueError('dependency must explicitly declare allowed scientific classifications')
    if len(ids)!=len(set(ids)): raise ValueError('duplicate campaign node id')
    visited=set(); active=set(); nodes={n['id']:n for n in design['nodes']}
    def walk(key):
        if key not in nodes: raise ValueError('unknown dependency node')
        if key in active: raise ValueError('campaign dependency cycle')
        if key in visited: return
        active.add(key)
        for dep in nodes[key]['dependencies']: walk(dep['node'])
        active.remove(key); visited.add(key)
    for key in ids: walk(key)
    from signal_space.engine.specification import capabilities
    if not isinstance(design['requires_capabilities'],list): raise ValueError('requires_capabilities must be an array')
    missing=sorted(set(design['requires_capabilities'])-set(capabilities()['supported']))
    return path,design,plans,configs,missing


def lock_design(path):
    path=Path(path).resolve(); value=read_json(path)
    value['locked_sha256']=lock_value(value)
    # Validate on a temporary sibling so invalid input is never given a new lock.
    temp=path.with_name('.'+path.name+'.validation')
    if temp.exists(): raise ValueError('campaign validation file already exists')
    write_json(temp,value)
    try: resolve_design(temp)
    finally: temp.unlink()
    write_json(path,value)
    return {'locked_sha256':value['locked_sha256'],'path':str(path)}


def inspect(value):
    path,design,plans,configs,missing=resolve_design(value)
    return {'campaign_id':design['campaign_id'],'question':design['question'],'design':str(path),
            'locked_sha256':design['locked_sha256'],'capability_ready':not missing,
            'missing_capabilities':missing,'nodes':[{'id':n['id'],'plan':str(plans[n['id']]),
                'dependencies':n['dependencies'],'model_id':configs[n['id']]['model_id']} for n in design['nodes']],
            'physics_executed':False}


def gate(dependency, upstream):
    if upstream['state']!='completed': return False,'prerequisite has not technically completed'
    status,run,_=verify_pipeline(upstream['output'])
    if upstream.get('manifest_sha256') and sha256_file(run/'manifest.json')!=upstream['manifest_sha256']:
        return False,'prerequisite manifest changed after campaign acceptance'
    allowed=dependency['classifications']
    if allowed and status['scientific_classification'] not in allowed:
        return False,f"scientific classification {status['scientific_classification']} does not satisfy {allowed}"
    checks={r['id']:r['status'] for r in status.get('checks',[])}
    missing=[key for key in dependency['checks'] if checks.get(key)!='pass']
    if missing: return False,'required checks did not pass: '+', '.join(missing)
    return True,{'manifest_sha256':sha256_file(run/'manifest.json'),'run_id':status['run_id'],
                 'analysis_id':status['analysis_id'],'report_id':status['report_id']}


def preflight(value, output, profile_name='desktop', jobs=None, case_jobs=1, threads=1):
    _,design,plans,configs,missing=resolve_design(value)
    chosen=profile(profile_name); policy=ExecutionPolicy(threads,case_jobs)
    budget=Budget(chosen['jobs'] if jobs is None else jobs,chosen['cpu_slots'],chosen['memory_mb'],None).resolve(Path(output).resolve())
    results={key:check(plan,output,policy,compile_backend=True) for key,plan in plans.items()}
    blockers=[f'engine capability missing: {name}' for name in missing]
    for key,result in results.items():
        blockers.extend(f'{key}: {b}' for b in result['blockers'])
        if configs[key]['resources']['max_memory_mb']>budget.memory_mb or policy.cpu_slots>budget.cpu_slots:
            blockers.append(f'{key}: locked run ceiling does not fit selected workstation profile')
    retained=sum(4*c['resources']['max_output_mb']+64 for c in configs.values())
    if retained>budget.output_mb: blockers.append('campaign retained output/export budget exceeds available disk')
    budget=Budget(budget.jobs,budget.cpu_slots,budget.memory_mb,retained)
    return {'schema_version':'gross-campaign-preflight-v1','execution_ready':not blockers,'physics_executed':False,
            'blockers':blockers,'profile':chosen,'budget':vars(budget),'reserved_output_mb':retained,
            'nodes':results,'design_lock':design['locked_sha256']}


class Campaign:
    def __init__(self, value, output, *, resume=False, profile_name='desktop', jobs=None, case_jobs=1, threads=1):
        self.output=Path(output).resolve(); self.resuming=resume
        if self.output.is_relative_to(ROOT): raise ValueError('campaign output must be outside source checkout')
        if resume:
            self.record=read_json(self.output/'campaign.json')
            self.design=self.record['design']
            self.plans={k:safe_child(self.output,v) for k,v in self.record['plans'].items()}
            self.configs={k:load_plan(v)[1] for k,v in self.plans.items()}
            if lock_value(self.design)!=self.record['design']['locked_sha256']: raise ValueError('campaign design changed')
            for key,path in self.plans.items():
                if sha256_file(path)!=self.record['plan_sha256'][key]: raise ValueError('campaign plan changed')
        else:
            path,self.design,plans,self.configs,missing=resolve_design(value)
            checked=preflight(value,self.output,profile_name,jobs,case_jobs,threads)
            if not checked['execution_ready']: raise ValueError('campaign blocked: '+'; '.join(checked['blockers']))
            self.output.mkdir(parents=True,exist_ok=False)
            self.plans={}
            for key,plan_path in plans.items():
                from signal_space.workflow.plans import canonical_plan,digest
                plan,config,config_path=load_plan(plan_path)
                folder=self.output/'plans'/key; folder.mkdir(parents=True)
                import shutil
                shutil.copy2(config_path,folder/'config.json')
                portable={**plan,'runtime_config':'config.json'}
                portable['locked_sha256']=digest(canonical_plan(portable))
                write_json(folder/'plan.json',portable)
                self.plans[key]=folder/'plan.json'
            self.record={'schema_version':'gross-campaign-state-v1','state':'prepared','created_at':now(),
                         'design':self.design,'design_source_sha256':sha256_file(path),
                         'plans':{k:p.relative_to(self.output).as_posix() for k,p in self.plans.items()},
                         'plan_sha256':{k:sha256_file(p) for k,p in self.plans.items()},
                         'budget':checked['budget'],'execution_policy':{'threads':threads,'case_jobs':case_jobs},
                         'source_code':code_identity(),'execution_identity':execution_identity({'threads':threads,'case_jobs':case_jobs}),
                         'preflight':checked,'sessions':[],
                         'computational_budget':{'max_cpu_seconds':sum(c['resources']['max_cpu_seconds'] for c in self.configs.values()),
                                                 'max_wall_seconds':sum(c['resources']['max_wall_seconds'] for c in self.configs.values())+1800*len(self.configs)},
                         'nodes':{n['id']:{'state':'queued','output':str(self.output/'nodes'/n['id']),'dependencies':{}} for n in self.design['nodes']}}
            self.save()
        self.policy=ExecutionPolicy.from_record(self.record['execution_policy'])
        self.cancel_event=threading.Event()

    def save(self):
        self.record['updated_at']=now(); write_json(self.output/'campaign.json',self.record)

    def _node(self, node):
        key=node['id']; output=Path(self.record['nodes'][key]['output'])
        reuse=node.get('reuse_from')
        if reuse and not output.exists():
            status,run,_=verify_pipeline(Path(reuse))
            manifest=read_json(run/'manifest.json')
            if read_json(run/'resolved-config.json')!=self.configs[key] or manifest['code_identity']!=code_identity() or manifest['execution_identity']!=execution_identity(self.policy.record()):
                raise ValueError('reused prerequisite config/code/environment differs; no silent cache substitution')
            if load_plan(Path(reuse)/'evidence/plan.json')[0]!=load_plan(self.plans[key])[0]:
                raise ValueError('reused prerequisite was bound to a different locked plan')
            # Record an immutable source reference, not a copied mutable cache.
            return {'state':'completed','output':str(Path(reuse).resolve()),'reused':True,
                    'manifest_sha256':sha256_file(run/'manifest.json'),'run_id':status['run_id']}
        pipeline=Pipeline(ROOT,output,None,self.policy.threads,self.policy.case_jobs,
                          resume=(output/'pipeline.json').exists(),plan_path=self.plans[key],cancel_event=self.cancel_event)
        code=pipeline.run()
        result={'state':'completed' if code==0 else 'interrupted' if self.cancel_event.is_set() else 'failed',
                'output':str(output),'exit_code':code}
        if pipeline.status.get('run_id'):
            run=safe_child(output/'evidence',pipeline.status['canonical_path'])
            manifest=read_json(run/'manifest.json')
            result.update(run_id=manifest['run_id'],canonical_path=str(run),
                          latest_checkpoint=manifest['attempts'][-1].get('checkpoint') if manifest['attempts'] else None,
                          analysis_id=pipeline.status.get('analysis_id'),report_id=pipeline.status.get('report_id'))
        if code==0:
            status,run,_=verify_pipeline(output)
            result.update(manifest_sha256=sha256_file(run/'manifest.json'),run_id=status['run_id'])
        return result

    def run(self):
        with _locked(self.output/'.campaign-owner'):
            if self.resuming:
                self.record=read_json(self.output/'campaign.json')
                self.policy=ExecutionPolicy.from_record(self.record['execution_policy'])
            # Preserve an immutable session history; unresolved science is never
            # converted to pass merely because a previous node finished.
            for key,row in self.record['nodes'].items():
                if row['state']=='completed':
                    _,run,_=verify_pipeline(row['output'])
                    if sha256_file(run/'manifest.json')!=row['manifest_sha256']:
                        raise ValueError('completed prerequisite identity changed')
                else: row['state']='queued'
            if all(row['state']=='completed' for row in self.record['nodes'].values()):
                return self.record
            # Persist the retained-output ceiling, then admit only remaining allocations.
            saved=self.record['budget']
            remaining=sum(4*self.configs[k]['resources']['max_output_mb']+64 for k,r in self.record['nodes'].items() if r['state']!='completed')
            budget=Budget(saved['jobs'],saved['cpu_slots'],saved['memory_mb'],max(1,remaining)).resolve(self.output)
            pending=[n for n in self.design['nodes'] if self.record['nodes'][n['id']]['state']!='completed']
            from signal_space.runtime.runner import ResearchRuntime
            costs={n['id']:ResearchRuntime().estimate(self.configs[n['id']],policy=self.policy)['estimate']['wall_seconds'] for n in pending}
            for n in pending:
                if n.get('cost_profile'):
                    from signal_space.runtime.costs import match
                    matched=match(n['cost_profile'],self.configs[n['id']],self.policy.record())
                    self.record['nodes'][n['id']]['cost_status']=matched['status']
                    if matched['matched']: costs[n['id']]=matched['profile']['wall_seconds']
            pending.sort(key=lambda n:(-costs[n['id']],n['id']))
            self.record['state']='running'
            self.record['sessions'].append({'started_at':now(),'node_states':deepcopy(self.record['nodes'])})
            self.save()
            active={}; memory=cpu=0; started=time.monotonic()
            # Aggregate computational ceilings remain separate from scheduling.
            max_wall=self.record['computational_budget']['max_wall_seconds']
            prior_wall=sum(s.get('elapsed_seconds',0) for s in self.record['sessions'][:-1])
            last_saved=-1.
            with ThreadPoolExecutor(max_workers=budget.jobs,thread_name_prefix='gross-campaign') as pool:
                try:
                    while pending or active:
                        try:
                            elapsed=time.monotonic()-started
                            if elapsed-last_saved>=1:
                                self.record['usage']=usage(self.record,self.policy)
                                self.record['usage']['retained_bytes']=sum(p.stat().st_size for p in self.output.rglob('*') if p.is_file())
                                self.record['sessions'][-1]['elapsed_seconds']=elapsed
                                self.save();last_saved=elapsed
                            exhausted=(elapsed+prior_wall>max_wall or self.record.get('usage',{}).get('cpu_seconds_charged',0)>=self.record['computational_budget']['max_cpu_seconds'] or self.record.get('usage',{}).get('retained_bytes',0)>saved['output_mb']*1048576)
                            if exhausted: self.record['stop_reason']='aggregate computational ceiling reached'
                            if (self.output/'stop.request').exists() or exhausted: self.cancel_event.set()
                            if self.cancel_event.is_set():
                                for n in pending: self.record['nodes'][n['id']]['state']='cancelled-before-start'
                                pending=[]
                            for n in list(pending):
                                row=self.record['nodes'][n['id']]; deps=n['dependencies']
                                if any(self.record['nodes'][d['node']]['state'] in {'queued','running'} for d in deps): continue
                                denied=[]; refs={}
                                for dep in deps:
                                    upstream=self.record['nodes'][dep['node']]
                                    good,reason=gate(dep,upstream)
                                    if good: refs[dep['node']]=reason
                                    else: denied.append(str(reason))
                                if denied:
                                    row.update(state='blocked',blockers=denied);pending.remove(n);self.save();continue
                                need=self.configs[n['id']]['resources']['max_memory_mb']
                                if len(active)>=budget.jobs or memory+need>budget.memory_mb or cpu+self.policy.cpu_slots>budget.cpu_slots: continue
                                row.update(state='running',dependencies=refs);self.save()
                                row.pop('error',None);row.pop('blockers',None)
                                future=pool.submit(self._node,n);active[future]=n
                                pending.remove(n);memory+=need;cpu+=self.policy.cpu_slots
                            if not active:
                                if pending: raise ValueError('campaign cannot admit any ready node')
                                break
                            done,_=wait(active,timeout=.2,return_when=FIRST_COMPLETED)
                            for future in done:
                                n=active.pop(future); memory-=self.configs[n['id']]['resources']['max_memory_mb'];cpu-=self.policy.cpu_slots
                                try: result=future.result()
                                except Exception as error: result={'state':'failed','error':f'{type(error).__name__}: {error}'}
                                self.record['nodes'][n['id']].update(result);self.save()
                        except KeyboardInterrupt: self.cancel_event.set()
                except BaseException as error:
                    self.record['state']='interrupted'
                    self.record['sessions'][-1].update(finished_at=now(),elapsed_seconds=time.monotonic()-started,error=str(error))
                    self.save()
                    raise
                finally:
                    self.cancel_event.set()
            states={r['state'] for r in self.record['nodes'].values()}
            self.record['state']='completed' if states=={'completed'} else 'blocked' if states<= {'completed','blocked'} else 'interrupted' if states & {'interrupted','cancelled-before-start'} else 'failed'
            self.record['sessions'][-1].update(finished_at=now(),elapsed_seconds=time.monotonic()-started,state=self.record['state'])
            (self.output/'stop.request').unlink(missing_ok=True)
            self.save();return self.record


def stop(output):
    output=Path(output).resolve()
    record=read_json(output/'campaign.json')
    if record['state']!='running': raise ValueError('campaign is not running')
    (output/'stop.request').touch()
    return {'state':'checkpoint-stop-requested','path':str(output)}


def export_campaign(output):
    output=Path(output).resolve(); record=read_json(output/'campaign.json')
    exports=[]
    for key,row in record['nodes'].items():
        if row['state']=='completed': exports.append({'node':key,**handoff(row['output'],output/'handoff'/key)})
    write_json(output/'handoff/campaign-index.json',{'campaign_lock':record['design']['locked_sha256'],
                                                   'state':record['state'],'nodes':exports})
    return {'state':record['state'],'exported_nodes':len(exports),'path':str(output/'handoff/campaign-index.json')}


def usage(record, policy):
    seconds=0.; unavailable=[]
    for key,row in record['nodes'].items():
        if row.get('reused'): continue  # exact external evidence incurs no new solve
        evidence=Path(row['output'])/'evidence'
        for run in (evidence/'runs').glob('*/*'):
            if not (run/'manifest.json').exists(): continue
            manifest=read_json(run/'manifest.json')
            for attempt in manifest['attempts']:
                folder=run/attempt['path']
                path=folder/'resource-usage.json'
                if not path.exists(): path=folder/'telemetry.json'
                if not path.exists(): continue
                measured=read_json(path)
                if measured.get('process_metrics_available',True): seconds+=measured.get('cpu_seconds',0.)
                else:
                    unavailable.append(f"{key}/{attempt['attempt_id']}")
                    seconds+=measured.get('wall_seconds',0.)*policy.cpu_slots
    return {'cpu_seconds_charged':seconds,'unavailable_cpu_measurements':unavailable,
            'accounting':'solver process trees across all attempts; wall times CPU slots charged conservatively when CPU metrics unavailable; report/export wall time included in campaign wall ceiling'}


def human_status(record):
    from signal_space.runtime.progress import snapshot, human_status as run_status
    lines=[f"{record['design']['campaign_id']}: {record['state']}"]
    for key,row in record['nodes'].items():
        lines.append(f"  {key}: {row['state']}"+(f" ({row['error']})" if row.get('error') else ''))
        path=Path(row['output'])/'evidence/status.json'
        if path.exists():
            status=read_json(path)
            lines.append(f"    stage={status['stage']} science={status['scientific_classification']}")
            if status.get('canonical_path'):
                run=safe_child(path.parent,status['canonical_path'])
                if (run/'manifest.json').exists(): lines.extend('    '+line for line in run_status(snapshot(run)).splitlines())
    return '\n'.join(lines)
