#!/usr/bin/env python3
"""Archive a hosted transfer run, or rebuild its reader after scientific review."""
import argparse
import json
import shutil
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
FAMILY=ROOT/'research/experiments/gross.reception-transfer.v1'
POINTER=FAMILY/'hosted-latest.json'

def read(p):return json.loads(p.read_text())
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')
def command(*args):subprocess.run(list(map(str,args)),cwd=ROOT,check=True)

parser=argparse.ArgumentParser()
parser.add_argument('--mode',choices=['execute','import','package'],required=True)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
args.output.mkdir(parents=True,exist_ok=True)
if args.mode in ('execute','import'):
    status=read(args.output/'evidence/status.json')
    if status['technical_status']!='completed' and not (args.mode=='import' and status.get('stage')=='package'):
        raise RuntimeError('only a verified solver with a packaging-only failure may be imported')
    source=args.output/'evidence'/status.get('canonical_path','runs/gross.reception-transfer.v1/'+status['run_id'])
    run_id=status['run_id'];run=FAMILY/run_id
    shutil.copytree(source,run)
    provenance=FAMILY/('provenance-'+run_id);provenance.mkdir()
    for name in ['status.json','execution.json','plan.json','config.json','README.md']:
        shutil.copy2(args.output/'evidence'/name,provenance/name)
    shutil.copytree(args.output/'evidence/logs',provenance/'logs')
    command('git','update-ref','refs/heads/transfer-execution-source',status['source_commit'])
    command('git','bundle','create',provenance/'source.bundle','origin/main..transfer-execution-source')
    command('git','bundle','verify',provenance/'source.bundle')
    write(POINTER,{'run_id':run_id,'source_commit':status['source_commit'],
        'classification':status['scientific_classification'],'review':'pending',
        'local_attempt':'run-8546b880d907e0ae; completion unverified after environment loss',
        'role':'hosted reproduction of unchanged locked protocol; not a new held-out sample'})
else:
    status=read(POINTER);run_id=status['run_id'];run=FAMILY/run_id
if args.mode=='import':
    command('python3','-m','signal_space','--workspace','research/experiments','verify','--run-id',run_id)
    command('python3','-m','signal_space','--workspace','research/experiments','report','--run-id',run_id)
    if args.mode=='import':
        write(FAMILY/('provenance-'+run_id)/'reader-repair.json',{'original_pipeline_status':'failed at package after canonical verification','repair':'align figure questions with locked plan; append report and rebuild reader','solver_rerun':False})
manifest=read(run/'manifest.json');analysis=manifest['analyses'][-1]
report=next(x for x in reversed(manifest['reports']) if x['analysis_id']==analysis['analysis_id'])
summary=read(run/analysis['path']/'derived/summary.json')
doc=ROOT/'docs/research/gross-test-07-transfer-results.md'
if args.mode in ('execute','import'):
    lines=['# Test 7 discrete transfer: hosted recovery','',
        '**Scientific review and PDF inspection pending.**','',
        'Canonical run: '+run_id+'. Registered classification: '+manifest['scientific_classification']+'.',
        'This is a recovery/reproducibility run of the fixed protocol. Local partial histories were already inspected.',
        'Original Test 7 remains failed. Test 8 remains blocked pending separate acceptance.','',
        '| Spectrum | Actual cycles | Second-order error | Fourth-order error | Locked budget | Forecast-inclusive diagnostic budget |',
        '| --- | ---: | ---: | ---: | ---: | ---: |']
    for wave,b in summary['budgets'].items():
        if 'total' not in b:continue
        audit=summary['forecast_convergence_audit'][wave]
        lines.append(f"| {wave} | {b['actual']:.12e} | {b['second_error']:.6e} | {b['fourth_error']:.6e} | {b['total']:.6e} | {audit['forecast_inclusive_budget']:.6e} |")
    lines += ['', '| Registered check | Status |','| --- | --- |']
    lines += [f'| {k} | {v} |' for k,v in summary['checks'].items()]
    lines += ['', 'The forecast-inclusive and known-source transfer audits are post-lock diagnostics. They cannot promote a registered failure or establish a new held-out claim.',
        'No two-object survival/recoil, coordinate/observer invariance, gravity, angular stability or emergent spacetime is tested.',
        '', '[Protocol](gross-test-07-transfer.md) | [Interruption record](gross-test-07-transfer-interruption.md)',
        '', f'[Canonical run](../../research/experiments/gross.reception-transfer.v1/{run_id}/manifest.json) | [Reader package](../../research/experiments/gross.reception-transfer.v1/export-{run_id}/README.md)']
    doc.write_text('\n'.join(lines)+'\n')
command('python3','-m','signal_space','--workspace','research/experiments','verify','--run-id',run_id)
export=args.output/'reviewed-reader'
if export.exists():raise RuntimeError('fresh export directory required')
command('python3','.agents/scripts/package_experiment.py','--run',run,'--plan','docs/research/plans/gross-test-07-transfer.json',
    '--interpretations',run/report['path']/'interpretations.json','--mentor',doc,'--source-dir','python/signal_space',
    '--source-locator',str(run.relative_to(ROOT)),'--output',export)
target=FAMILY/('export-'+run_id)
if target.exists():shutil.rmtree(target)
shutil.copytree(export,target)
command('python3','.agents/scripts/experiment_contract.py','bundle',target)
preview=FAMILY/('provenance-'+run_id)/'pdf-preview'
if preview.exists():shutil.rmtree(preview)
preview.mkdir(parents=True)
for name in ['Experimental_Setup','Experiment_Results']:
    command('pdftoppm','-r','100','-png',target/(name+'.pdf'),preview/name)
catalog=read(ROOT/'research/catalog.json')
for item in catalog['entries']:
    if item['id']=='gross-test-07-transfer':
        item['status']='executed hosted recovery; original Test 7 status unchanged'
        item['summary']='Discrete transfer with independent profiles, two spectra, strict order budget and separately labeled convergence/inverse audits.'
entry={'id':'run-'+run_id,'date':'2026-09-26','kind':'experiment-run',
       'path':str((target/'README.md').relative_to(ROOT)),
       'status':'registered '+manifest['scientific_classification']+'; '+('scientific review pending' if args.mode in ('execute','import') else 'see reviewed limitations'),
       'summary':'Hosted recovery of fixed Test 7 transfer protocol; original failure unchanged; post-lock forecast and inverse audits retained.',
       'tags':['gross.reception-transfer.v1','reproducibility'],
       'title':'Test 7 discrete-transfer recovery - '+run_id}
catalog['entries']=[x for x in catalog['entries'] if x['id']!=entry['id']]+[entry]
write(ROOT/'research/catalog.json',catalog)
if args.mode=='package':
    status['review']='completed; see reviewed results and PDF audit';write(POINTER,status)
command('npx','prettier','--write','research/catalog.json','docs/research/gross-test-07-transfer-results.md','docs/research/gross-test-07-transfer-interruption.md','docs/research/gross-test-07-transfer.md','docs/research/gross-progress.md','.github/workflows/run-experiment.yml','.github/workflows/recover-transfer.yml')
command('node','scripts/research-archive.mjs','--write')
command('python3','scripts/check-experiment-math.py')
command('git','diff','--check')
