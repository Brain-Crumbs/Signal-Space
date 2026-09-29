"""Measured cost profiles keyed to producer code, environment and exact work."""
import os
import platform
from pathlib import Path
import statistics

from signal_space.runtime.io import read_json, write_json, canonical_bytes, sha256_bytes, sha256_file
from signal_space.runtime.package import code_identity, execution_identity
from signal_space.runtime.execution import cpu_capacity


def hardware():
    processor=platform.processor()
    cpuinfo=Path('/proc/cpuinfo')
    if not processor and cpuinfo.is_file():
        processor=next((line.split(':',1)[1].strip() for line in cpuinfo.read_text().splitlines() if line.startswith('model name')), '')
    return {'machine':platform.machine(),'processor':processor,
            'logical_cpus':os.cpu_count(),'available_cpu_slots':cpu_capacity()}


def work_key(config, policy, code=None, environment=None):
    return sha256_bytes(canonical_bytes({'config':config,'policy':policy,
        'code':code if code is not None else code_identity(),
        'execution':environment if environment is not None else execution_identity(policy)}))


def collect(run_path, output):
    from signal_space.runtime.verify import verify_package
    run_path=Path(run_path).resolve(); output=Path(output).resolve()
    if output.exists(): raise ValueError('cost observations are immutable; choose a new output file')
    if output.is_relative_to(run_path): raise ValueError('profile must be outside the run package')
    verified=verify_package(run_path)
    if not verified['valid']: raise ValueError('cost source did not verify')
    manifest=read_json(run_path/'manifest.json')
    config=read_json(run_path/'resolved-config.json')
    policy=manifest['execution_identity']['environment'].get('execution_policy',{'threads':1,'case_jobs':1})
    cases=[]; resources=[]; full_resources=[]
    for attempt in manifest['attempts']:
        if attempt['state']!='completed': continue
        folder=run_path/attempt['path']
        for path in sorted(folder.rglob('performance.json')):
            observed=read_json(path)
            for row in observed['cases']:
                if row['complete_case']:
                    cases.append({**row,'source':path.relative_to(run_path).as_posix(),'sha256':sha256_file(path)})
        if (folder/'resource-usage.json').exists():
            measured=read_json(folder/'resource-usage.json')
            resources.append(measured)
            if attempt.get('parent_attempt_id') is None: full_resources.append(measured)
    if not resources: raise ValueError('no completed attempt resource measurement')
    record={'schema_version':'gross-cost-profile-v1',
            'work_key':work_key(config,policy,manifest['code_identity'],manifest['execution_identity']),
            'hardware':read_json(run_path/'provenance/hardware.json') if (run_path/'provenance/hardware.json').exists() else None,
            'run_id':manifest['run_id'],'manifest_sha256':sha256_file(run_path/'manifest.json'),
            'source_code':manifest['code_identity'],'execution_identity':manifest['execution_identity'],
            'cases':cases,'attempts':resources,'whole_work_measured':bool(full_resources),
            'wall_seconds':statistics.median(r['wall_seconds'] for r in full_resources) if full_resources else None,
            'sample_count':len(resources),'uncertainty':'observed range only; no statistical confidence interval',
            'wall_range_seconds':[min(r['wall_seconds'] for r in resources),max(r['wall_seconds'] for r in resources)]}
    write_json(output,record)
    return record


def match(path, config, policy):
    value=read_json(Path(path))
    if value.get('schema_version')!='gross-cost-profile-v1': raise ValueError('unsupported cost profile')
    matching=value.get('whole_work_measured') is True and value['work_key']==work_key(config,policy) and value.get('hardware')==hardware()
    return {'matched':matching,'status':'measured-on-matching-work-and-host' if matching else 'stale-or-incompatible',
            'profile_sha256':sha256_file(Path(path)),'profile':value}


def case_cost(case):
    """Uncalibrated work proxy, used only for ordering independent ready cases."""
    cells=round(case['radius']/case['h'])*round(2*case['half_length']/case['h'])
    return cells*case['periods']/case['dt']


def longest_first(indexes, costs):
    return sorted(indexes,key=lambda i:(-costs[i],i))


def collect_pipeline(pipeline, output):
    from signal_space.workflow.artifacts import verify_pipeline
    pipeline=Path(pipeline).resolve()
    _,run,_=verify_pipeline(pipeline)
    # Build once in a temporary location, then publish the complete observation.
    import tempfile
    with tempfile.TemporaryDirectory() as folder:
        result=collect(run,Path(folder)/'cost.json')
    if Path(output).exists(): raise ValueError('cost observations are immutable; choose a new output file')
    journal=read_json(pipeline/'pipeline.json')
    result['pipeline_stages']=journal['stages']
    result['pipeline_journal_sha256']=sha256_file(pipeline/'pipeline.json')
    index=pipeline/'handoff/pr-evidence-index.json'
    result['handoff']=read_json(index) if index.exists() else None
    result['missing_phases']=[] if index.exists() else ['paired ZIP compression and archive verification']
    write_json(Path(output),result)
    return result
