"""Verified paired exports and safe portable import; evidence stays outside Git."""
import shutil
import time
from pathlib import Path, PurePosixPath
import zipfile

from signal_space.runtime.io import read_json, write_json, sha256_file, safe_child
from signal_space.runtime.runner import ResearchRuntime
from signal_space.runtime.execution import disk_capacity_mb
from signal_space.workflow.plans import ROOT, load_plan
from signal_space.workflow.assessment import assessment
from experiment_contract import validate_bundle
from package_experiment import package as package_reader


def pack(folder, output):
    folder, output = Path(folder), Path(output)
    if output.exists():
        with zipfile.ZipFile(output) as existing:
            if existing.testzip(): raise ValueError('existing archive CRC failure')
        return {'name':output.name,'size_bytes':output.stat().st_size,'sha256':sha256_file(output)}
    started=time.perf_counter()
    temporary=output.with_suffix('.zip.tmp')
    if temporary.exists(): raise ValueError(f'partial archive exists; preserve and inspect {temporary}')
    # Store already compressed formats directly to avoid repeated compression.
    with zipfile.ZipFile(temporary,'x',allowZip64=True) as bundle:
        for path in sorted(folder.rglob('*')):
            if not path.is_file() or path.name.startswith('.') or path.name.endswith('.jsonl.lock'): continue
            compression=zipfile.ZIP_STORED if path.suffix.lower() in {'.npz','.zip','.png','.gz','.pdf'} else zipfile.ZIP_DEFLATED
            bundle.write(path,(Path(folder.name)/path.relative_to(folder)).as_posix(),compress_type=compression,compresslevel=6)
    packed=time.perf_counter()
    with zipfile.ZipFile(temporary) as bundle:
        if bundle.testzip(): raise ValueError('new archive CRC validation failed')
    temporary.rename(output)
    checked=time.perf_counter(); digest=sha256_file(output)
    return {'name':output.name,'size_bytes':output.stat().st_size,'sha256':digest,
            'timings_seconds':{'archive_write':packed-started,'crc_verify':checked-packed,'sha256':time.perf_counter()-checked}}


def verify_pipeline(output):
    output=Path(output).resolve(); evidence=output/'evidence'
    status=read_json(evidence/'status.json')
    if status['technical_status']!='completed':
        raise ValueError('pipeline incomplete; use pipeline --resume before exporting')
    run=safe_child(evidence,status['canonical_path'])
    reader=safe_child(output,status.get('reader_path','reader'))
    for row in read_json(evidence/'evidence-index.json')['files']:
        path=safe_child(evidence,row['path'])
        if not path.is_file() or sha256_file(path)!=row['sha256']:
            raise ValueError(f'outer evidence checksum mismatch: {row["path"]}')
    result=ResearchRuntime().verify(evidence/'runs',status['run_id'])
    if not result['valid']: raise ValueError('canonical verification failed')
    validate_bundle(reader,run)
    identity=read_json(reader/'export.json')['source_run']
    for key in ('run_id','analysis_id','report_id'):
        if identity[key]!=status[key]: raise ValueError(f'reader pipeline {key} mismatch')
    return status,run,reader


def handoff(pipeline, output=None, locator=None):
    pipeline=Path(pipeline).resolve(); output=Path(output).resolve() if output else pipeline/'handoff'
    if output.is_relative_to(ROOT): raise ValueError('handoff must be outside the source checkout')
    status,run,reader=verify_pipeline(pipeline)
    output.mkdir(parents=True,exist_ok=True)
    index_path=output/'pr-evidence-index.json'
    if index_path.exists():
        record=read_json(index_path)
        if record['canonical_manifest_sha256']!=sha256_file(run/'manifest.json') or record.get('evidence_index_sha256')!=sha256_file(pipeline/'evidence/evidence-index.json'):
            raise ValueError('handoff belongs to an earlier manifest; choose a new output directory')
        for row in record['archives']:
            if sha256_file(safe_child(output,row['name']))!=row['sha256']: raise ValueError('handoff archive changed')
        return record
    estimated=sum(p.stat().st_size for folder in (pipeline/'evidence',reader) for p in folder.rglob('*') if p.is_file())
    if estimated*2 > disk_capacity_mb(output)*1048576: raise ValueError('insufficient temporary/export disk headroom')
    archives=[]
    for folder,label in ((pipeline/'evidence','evidence'),(reader,'reader')):
        target=output/f'{label}-{status["run_id"]}.zip'
        # Existing archives without a committed handoff index are untrusted;
        # compare their entire inventory against source rather than overwrite.
        if target.exists():
            with zipfile.ZipFile(target) as bundle:
                expected={str(Path(folder.name)/p.relative_to(folder)).replace('\\','/'):p for p in folder.rglob('*')
                          if p.is_file() and not p.name.startswith('.') and not p.name.endswith('.jsonl.lock')}
                if set(bundle.namelist())!=set(expected): raise ValueError('partial handoff archive inventory differs')
                import hashlib
                for name,path in expected.items():
                    if hashlib.sha256(bundle.read(name)).hexdigest()!=sha256_file(path): raise ValueError('partial handoff archive bytes differ')
        archives.append(pack(folder,target))
    manifest=read_json(run/'manifest.json')
    record={'schema_version':'gross-handoff-v1','experiment_id':manifest['experiment_id'],
            'run_id':status['run_id'],'analysis_id':status['analysis_id'],'report_id':status['report_id'],
            'technical_status':status['technical_status'],'scientific_classification':status['scientific_classification'],
            'source_commit':status['source_commit'],'plan_lock':read_json(pipeline/'evidence/plan.json')['locked_sha256'],
            'canonical_manifest_sha256':sha256_file(run/'manifest.json'),
            'evidence_index_sha256':sha256_file(pipeline/'evidence/evidence-index.json'),
            'canonical_path':status['canonical_path'],'reader_root':reader.name,
            'archives':archives,'durable_locator':locator,
            'scope':'registered plan only; scientific review and dependency acceptance remain separate',
            'checks':{row['id']:row['status'] for row in status.get('checks',[])}}
    write_json(index_path,record)
    return record


def import_handoff(index_path, output):
    index_path=Path(index_path).resolve(); record=read_json(index_path)
    if record.get('schema_version')!='gross-handoff-v1': raise ValueError('unsupported handoff schema')
    output=Path(output).resolve()
    if output.exists() or output.is_relative_to(ROOT): raise ValueError('import needs a new directory outside the checkout')
    archives=[]; total=0; all_names=set()
    if len(record['archives'])!=2 or len({r['name'] for r in record['archives']})!=2:
        raise ValueError('handoff requires exactly two distinct archives')
    reader_root=PurePosixPath(record['reader_root'])
    if len(reader_root.parts)!=1 or reader_root.name in {'.','..','evidence'}: raise ValueError('unsafe reader root')
    for row in record['archives']:
        path=safe_child(index_path.parent,row['name'])
        if not path.is_file() or path.stat().st_size!=row['size_bytes'] or sha256_file(path)!=row['sha256']:
            raise ValueError('archive identity mismatch')
        with zipfile.ZipFile(path) as bundle:
            names=set()
            for item in bundle.infolist():
                name=PurePosixPath(item.filename)
                if name.is_absolute() or '\\' in item.filename or ':' in item.filename or '..' in name.parts or item.filename in names or (item.external_attr>>16)&0o170000 == 0o120000:
                    raise ValueError('unsafe archive member')
                if not name.parts or name.parts[0] not in {'evidence',record['reader_root']} or item.filename in all_names:
                    raise ValueError('overlapping or unexpected archive member')
                names.add(item.filename);all_names.add(item.filename);total+=item.file_size
        archives.append(path)
    if total*2 > disk_capacity_mb(output)*1048576: raise ValueError('insufficient import disk headroom')
    output.mkdir(parents=True)
    try:
        for path in archives:
            with zipfile.ZipFile(path) as bundle: bundle.extractall(output)
        status,_,_=verify_pipeline(output)
        if sha256_file(output/'evidence/evidence-index.json')!=record['evidence_index_sha256']:
            raise ValueError('imported outer index mismatch')
        for key in ('run_id','analysis_id','report_id','scientific_classification','source_commit'):
            if status[key]!=record[key]: raise ValueError(f'imported {key} identity mismatch')
        if read_json(output/'evidence/plan.json')['locked_sha256']!=record['plan_lock']: raise ValueError('imported plan lock mismatch')
        run=safe_child(output/'evidence',record['canonical_path'])
        if sha256_file(run/'manifest.json')!=record['canonical_manifest_sha256']: raise ValueError('imported manifest mismatch')
        result=ResearchRuntime().verify(output/'evidence/runs',record['run_id'])
        if not result['valid']: raise ValueError('imported evidence is invalid')
        validate_bundle(safe_child(output,record['reader_root']),run)
        shutil.copy2(index_path,output/'pr-evidence-index.json')
    except BaseException:
        # Preserve failed imports for diagnosis; they are never called verified.
        write_json(output/'import-status.json',{'verified':False})
        raise
    write_json(output/'import-status.json',{'verified':True,'run_id':record['run_id']})
    return {'verified':True,'path':str(output),'run_id':record['run_id']}


def export_run(workspace, run_id, plan_path, output):
    runtime=ResearchRuntime(); run=runtime._package(Path(workspace).resolve(),run_id).path
    if not runtime.verify(Path(workspace).resolve(),run_id)['valid']: raise ValueError('canonical verification failed')
    plan,config,_=load_plan(plan_path)
    if read_json(run/'resolved-config.json')!=config: raise ValueError('plan differs from run')
    manifest=read_json(run/'manifest.json')
    if not manifest['analyses']: raise ValueError('analyze saved data before export')
    analysis=manifest['analyses'][-1]
    reports=[r for r in manifest['reports'] if r['analysis_id']==analysis['analysis_id']]
    if not reports: raise ValueError('create the selected analysis report before export')
    output=Path(output).resolve()
    if output.exists() or output.is_relative_to(ROOT): raise ValueError('reader export requires new external output')
    output.mkdir(parents=True)
    evidence=output/'evidence'; evidence.mkdir()
    canonical=Path('runs')/manifest['experiment_id']/run_id
    copied=evidence/canonical
    shutil.copytree(run,copied,ignore=shutil.ignore_patterns('.package.lock','*.jsonl.lock'))
    # Existing provenance is copied byte-for-byte. Source availability is stated
    # explicitly rather than substituting the current checkout for its producer.
    from signal_space.workflow.plans import canonical_plan, digest
    portable={**plan,'runtime_config':'config.json'}
    portable['locked_sha256']=digest(canonical_plan(portable))
    shutil.copy2(load_plan(plan_path)[2],evidence/'config.json')
    write_json(evidence/'plan.json',portable)
    shutil.copy2(plan_path,evidence/'registered-plan.json')
    mentor=evidence/'assessment.md'
    checks=read_json(copied/analysis['path']/'checks.json')
    mentor.write_text(assessment(manifest,analysis,checks),encoding='utf-8')
    package_reader(copied,evidence/'plan.json',copied/reports[-1]['path']/'interpretations.json',mentor,output/'reader',None,canonical.as_posix())
    validate_bundle(output/'reader',copied)
    status={'experiment':manifest['experiment_id'],'technical_status':'completed',
            'scientific_classification':analysis['classification'],'source_commit':manifest['code_identity']['revision'],
            'run_id':run_id,'analysis_id':analysis['analysis_id'],'report_id':reports[-1]['report_id'],
            'canonical_path':canonical.as_posix(),'reader_path':'reader','stage':'complete','checks':checks['checks']}
    write_json(evidence/'status.json',status)
    (evidence/'README.md').write_text('Existing canonical run exported without evolution. Producer source is identified by provenance; no complete source archive was supplied. Restore that revision/environment to resume numerical work.\n',encoding='utf-8')
    files=[{'path':p.relative_to(evidence).as_posix(),'sha256':sha256_file(p)} for p in sorted(evidence.rglob('*')) if p.is_file()]
    write_json(evidence/'evidence-index.json',{'files':files})
    return handoff(output)


def smoke_report(run, plan_path, output):
    """Exercise any registered renderer and reader against copied saved inputs."""
    from signal_space.runtime.verify import verify_package
    run=Path(run).resolve();output=Path(output).resolve()
    verify_package(run)
    _,config,_=load_plan(plan_path)
    if config!=read_json(run/'resolved-config.json'): raise ValueError('smoke plan does not bind saved run')
    manifest=read_json(run/'manifest.json')
    if not manifest['analyses']: raise ValueError('report smoke requires saved analysis')
    if output.exists() or output.is_relative_to(ROOT) or output.is_relative_to(run):
        raise ValueError('report smoke requires a new external output directory')
    size=sum(p.stat().st_size for p in run.rglob('*') if p.is_file())
    if 4*size+64*1048576>disk_capacity_mb(output)*1048576: raise ValueError('insufficient report smoke copy/export headroom')
    workspace=output/'source-copy'
    copied=workspace/manifest['experiment_id']/manifest['run_id']
    shutil.copytree(run,copied,ignore=shutil.ignore_patterns('.package.lock','*.jsonl.lock'))
    runtime=ResearchRuntime()
    try:
        runtime.report(workspace,manifest['run_id'],plan=plan_path)
        runtime.verify(workspace,manifest['run_id'])
        result=export_run(workspace,manifest['run_id'],plan_path,output/'export')
        write_json(output/'smoke-status.json',{'verified':True,'physics_executed':False,'source_manifest_sha256':sha256_file(run/'manifest.json')})
        return {'verified':True,'physics_executed':False,'output':str(output),'handoff':result}
    except BaseException as error:
        write_json(output/'smoke-status.json',{'verified':False,'physics_executed':False,'error':str(error)})
        raise
