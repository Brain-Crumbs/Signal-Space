"""Campaign engineering controls. Tiny manufactured fields are not research evidence."""
import copy
import csv
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from signal_space.runtime.execution import ExecutionPolicy
from signal_space.runtime.io import read_json, write_json, sha256_file, pretty_bytes
from signal_space.runtime.runner import ResearchRuntime
from signal_space.workflow.plans import ROOT, load_plan, derive, canonical_plan, digest
from signal_space.workflow.pipeline import Pipeline
from signal_space.workflow.recipes import RECIPES, recipe_path


def portable(plan_path, folder, config=None):
    plan,original,_=load_plan(plan_path)
    config=original if config is None else config
    folder.mkdir(parents=True,exist_ok=True)
    plan={**plan,'runtime_config':'config.json','runtime_config_sha256':digest(pretty_bytes(config)),
          'resources':config['resources']}
    plan['locked_sha256']=digest(canonical_plan(plan))
    write_json(folder/'config.json',config);write_json(folder/'plan.json',plan)
    return folder/'plan.json'


def fixture_initialize(self):
    # Bypass only the clean-source/snapshot gate for a temporary engineering
    # fixture; exercise real numerical worker, manifests and all later stages.
    plan=portable(self.plan_path,self.evidence)
    self.plan_path=plan
    self.journal.update(initialized=True,plan_sha256=sha256_file(plan),config_sha256=sha256_file(plan.parent/'config.json'))
    self.status['source_commit']='engineering-fixture'
    self._save()


class WorkbenchControls(unittest.TestCase):
    def test_closed_resource_derivation_preserves_physics_and_parent(self):
        with tempfile.TemporaryDirectory() as folder:
            source=recipe_path('gross-test-08-quiet-optimized');before=sha256_file(source)
            _,config,_=load_plan(source)
            result=derive(source,Path(folder)/'derived',{'max_wall_seconds':config['resources']['max_wall_seconds']+1})
            plan,new,_=load_plan(result['plan'])
            self.assertEqual(config['parameters'],new['parameters'])
            self.assertEqual(config['analysis'],new['analysis'])
            self.assertEqual(before,sha256_file(source))
            self.assertNotEqual(plan['locked_sha256'],load_plan(source)[0]['locked_sha256'])
            with self.assertRaises(ValueError): derive(source,Path(folder)/'invalid',{'h':.1})
            with self.assertRaises(ValueError): derive(source,Path(folder)/'invalid',{'max_wall_seconds':True})

    def test_every_recipe_declares_exact_locked_visual_questions(self):
        from signal_space.workflow.preflight import visual_contract
        for name in RECIPES:
            with self.subTest(recipe=name):
                result=visual_contract(load_plan(recipe_path(name))[0]);self.assertTrue(result['required_figures'])
        plan=copy.deepcopy(load_plan(recipe_path('gross-test-01'))[0])
        plan['visualization_plan'][0]['question']='wrong'
        with self.assertRaisesRegex(ValueError,'questions differ'): visual_contract(plan)

    def test_direct_host_admission_before_identity_or_launch(self):
        from signal_space.runtime.errors import ResourceRejected
        config=load_plan(recipe_path('gross-test-01'))[1]
        with tempfile.TemporaryDirectory() as folder, patch('signal_space.runtime.execution.memory_capacity_mb',return_value=1):
            with self.assertRaises(ResourceRejected): ResearchRuntime().create_run(config,Path(folder))
            self.assertFalse(any(Path(folder).iterdir()))

    def test_recursive_event_cursor_reconnect_and_partial_line(self):
        from signal_space.runtime.progress import EventStream
        from signal_space.runtime.events import append_event
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);run=root/'run-fixture';child=run/'attempts/attempt-0001/cases/case-0000/events.jsonl'
            child.parent.mkdir(parents=True)
            append_event(child,'scenario-progress','run',{'label':'pair-fine','step':1000,'total_steps':2000})
            reader=EventStream(run,root/'cursor.json');events=reader.poll()
            self.assertEqual(len(events),1);self.assertEqual(events[0]['case'],'case-0000')
            # No acknowledgement means reconnect replays the event.
            self.assertEqual(len(EventStream(run,root/'cursor.json').poll()),1)
            reader.acknowledge();self.assertEqual(EventStream(run,root/'cursor.json').poll(),[])
            with child.open('ab') as stream:stream.write(b'{')
            self.assertEqual(EventStream(run,root/'cursor.json').poll(),[])

    def test_engine_owns_snapshots_and_rejects_unsupported_physics(self):
        from signal_space.engine import GeometrySpec,SimulationSpec,ModelSpec
        from signal_space.engine.simulation import Simulation,checkpoint_fields,restore_fields
        from signal_space.engine.state import FieldState
        from signal_space.engine.axisymmetric import AbsorbingGrid,step
        geometry=GeometrySpec(.5,3,4,1,.12);grid=AbsorbingGrid(.5,3,4,1,.12)
        rng=np.random.default_rng(8);shape=(grid.nr,grid.nz)
        fields=tuple((rng.normal(size=shape)+1j*rng.normal(size=shape)).astype('complex128')*.001 if i<2 else rng.normal(size=shape)*.001 for i in range(6))+(0.,0.)
        original=FieldState.from_tuple(fields,copy=True)
        simulation=Simulation(SimulationSpec(geometry),original)
        frozen=simulation.snapshot();expected=step(grid,fields,.002)
        simulation.advance(.002)
        for observed,reference in zip(simulation.state.as_tuple(),expected): np.testing.assert_array_equal(observed,reference)
        for observed,reference in zip(frozen.as_tuple(),original.as_tuple()): np.testing.assert_array_equal(observed,reference)
        restored=restore_fields(checkpoint_fields(simulation.state))
        for observed,reference in zip(restored.as_tuple(),expected):np.testing.assert_array_equal(observed,reference)
        with self.assertRaises(ValueError): SimulationSpec(geometry,ModelSpec(gravity='dynamic')).validate()
        with self.assertRaises(ValueError): SimulationSpec(geometry,detectors=('momentum-worldtube-flux',)).validate()

    def test_campaign_graph_locks_cycles_and_scientific_gates(self):
        from signal_space.workflow.campaign import inspect,lock_design,resolve_design,gate
        self.assertFalse(inspect('test8')['capability_ready'])
        self.assertTrue(inspect('test8-quiet')['capability_ready'])
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);path=root/'campaign.json';design=read_json(ROOT/'docs/research/campaigns/operator-chain.json')
            design['nodes'][0]['dependencies']=[{'node':'events','classifications':['pass'],'checks':[]}]
            write_json(path,design)
            with self.assertRaisesRegex(ValueError,'cycle'):lock_design(path)
            manifest=root/'manifest.json';write_json(manifest,{'fixture':True})
            status={'scientific_classification':'unresolved','checks':[{'id':'short','status':'pass'}],'run_id':'fixture','analysis_id':'a','report_id':'r'}
            with patch('signal_space.workflow.campaign.verify_pipeline',return_value=(status,root,root)):
                self.assertFalse(gate({'classifications':['pass'],'checks':['short']},{'state':'completed','output':str(root)})[0])
                self.assertTrue(gate({'classifications':['unresolved'],'checks':['short']},{'state':'completed','output':str(root)})[0])
                self.assertFalse(gate({'classifications':[],'checks':['absent']},{'state':'completed','output':str(root)})[0])

    def test_stale_cost_profiles_never_drive_predictions(self):
        from signal_space.runtime.costs import match,hardware,work_key,longest_first
        config=load_plan(recipe_path('gross-test-01'))[1];policy=ExecutionPolicy().record()
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'profile.json'
            value={'schema_version':'gross-cost-profile-v1','whole_work_measured':True,'hardware':hardware(),'work_key':work_key(config,policy),'wall_seconds':1}
            write_json(path,value);self.assertTrue(match(path,config,policy)['matched'])
            value['whole_work_measured']=False;write_json(path,value);self.assertFalse(match(path,config,policy)['matched'])
            value['whole_work_measured']=True;value['hardware']['processor']='different';write_json(path,value)
            self.assertFalse(match(path,config,policy)['matched'])
            self.assertEqual(longest_first([0,1,2],{0:2,1:8,2:3}),[1,2,0])

    def test_pipeline_analysis_report_export_failures_resume_without_rerun(self):
        from signal_space.workflow import pipeline as module
        from signal_space.workflow.artifacts import handoff,import_handoff,verify_pipeline
        with tempfile.TemporaryDirectory() as folder, patch.object(Pipeline,'_initialize',fixture_initialize):
            root=Path(folder);output=root/'pipeline';p=Pipeline(ROOT,output,'gross-test-01')
            with patch.object(p.runtime_api,'analyze',side_effect=RuntimeError('injected analysis failure')):
                self.assertEqual(p.run(),1)
            status=read_json(output/'evidence/status.json');run=output/'evidence'/status['canonical_path']
            original={p.relative_to(run).as_posix():sha256_file(p) for p in (run/'attempts').rglob('*') if p.is_file()}
            p=Pipeline(ROOT,output,resume=True)
            with patch.object(p.runtime_api,'report',side_effect=RuntimeError('injected report failure')):
                self.assertEqual(p.run(),1)
            p=Pipeline(ROOT,output,resume=True)
            def broken_package(*args):
                args[4].mkdir();(args[4]/'partial.txt').write_text('partial');raise RuntimeError('injected package failure')
            with patch.object(module,'package_reader',side_effect=broken_package): self.assertEqual(p.run(),1)
            self.assertEqual(Pipeline(ROOT,output,resume=True).run(),0)
            self.assertEqual(original,{p.relative_to(run).as_posix():sha256_file(p) for p in (run/'attempts').rglob('*') if p.is_file()})
            self.assertEqual(len(read_json(run/'manifest.json')['attempts']),1)
            self.assertEqual(len(read_json(run/'manifest.json')['reports']),1)
            status,_,_=verify_pipeline(output)
            self.assertEqual(status['reader_path'],'reader-0002')
            self.assertTrue((output/'reader/partial.txt').exists())
            index=handoff(output);self.assertEqual(index,handoff(output))
            imported=import_handoff(output/'handoff/pr-evidence-index.json',root/'imported')
            self.assertTrue(imported['verified'])
            # Cross-archive identity and checksum validation must fail on tamper.
            zip_path=output/'handoff'/index['archives'][0]['name']
            with zip_path.open('ab') as stream:stream.write(b'changed')
            with self.assertRaisesRegex(ValueError,'identity mismatch'):
                import_handoff(output/'handoff/pr-evidence-index.json',root/'bad')

    def test_failed_initialization_can_resume(self):
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/'pipeline';p=Pipeline(ROOT,output,'gross-test-01')
            with patch.object(p,'_initialize',side_effect=ValueError('injected preflight failure')):self.assertEqual(p.run(),1)
            with patch.object(Pipeline,'_initialize',fixture_initialize):self.assertEqual(Pipeline(ROOT,output,resume=True).run(),0)

    def test_campaign_runs_dependencies_and_reuses_completed_nodes(self):
        from signal_space.workflow.campaign import Campaign,export_campaign
        from signal_space.workflow.preflight import check as preflight
        from signal_space.runtime.costs import collect_pipeline
        from signal_space.workflow.compare import compare
        def local_preflight(*args,**kwargs):
            return preflight(*args,**kwargs,require_clean=False)
        with tempfile.TemporaryDirectory() as folder, patch.object(Pipeline,'_initialize',fixture_initialize), patch('signal_space.workflow.campaign.check',side_effect=local_preflight):
            root=Path(folder);output=root/'campaign'
            record=Campaign('operator-chain',output,jobs=2).run()
            self.assertEqual(record['state'],'completed')
            self.assertEqual(set(record['nodes']['events']['dependencies']),{'algebra'})
            original=sha256_file(output/'campaign.json')
            self.assertEqual(Campaign(None,output,resume=True).run()['state'],'completed')
            self.assertEqual(original,sha256_file(output/'campaign.json'))
            self.assertEqual(export_campaign(output)['exported_nodes'],2)
            measured=collect_pipeline(output/'nodes/algebra',root/'cost.json')
            self.assertTrue(measured['whole_work_measured'])
            run=Path(record['nodes']['algebra']['canonical_path'])
            comparison=compare(run,run,root/'compare')
            self.assertTrue(comparison['compatible'])
            self.assertTrue(all(q['difference']==0 for row in comparison['checks'] for q in row['quantities']))

    def test_quiet_original_and_resumed_saved_data_render_and_package(self):
        from signal_space.experiments.two_object_quiet import TwoObjectQuietExperiment
        from signal_space.runtime.package import RunPackage
        from signal_space.workflow.artifacts import export_run,import_handoff
        for resumed in (False,True):
            with self.subTest(resumed=resumed),tempfile.TemporaryDirectory() as folder:
                root=Path(folder);runtime=ResearchRuntime();config=load_plan(recipe_path('gross-test-08-quiet-optimized'))[1]
                r=np.linspace(0,8,81);source=root/'profile.npz'
                np.savez(source,r=r,u=r[1:-1]*.1*np.exp(-r[1:-1]**2),mode=r[1:-1]*np.exp(-r[1:-1]**2))
                config['parameters']['profile']={'path':str(source),'sha256':sha256_file(source)}
                config['parameters']['separation']=2.
                config['parameters']['execution']={'backend':'numpy','neutral_mode':'full','checkpoint_stride':10}
                for case in config['parameters']['scenarios']:
                    case.update(h=.5,dt=.02,radius=3,half_length=4,absorber_width=1,periods=.03,sample_stride=2)
                plan=portable(recipe_path('gross-test-08-quiet-optimized'),root/'locked',config)
                with patch.object(TwoObjectQuietExperiment,'validate',lambda self,value:value):
                    created=runtime.create_run(config,root/'work');run=Path(created['path']);rid=created['run_id']
                    if resumed:
                        result=runtime.execute(root/'work',rid,on_started=lambda _:runtime.cancel(root/'work',rid))
                        self.assertEqual(result['state'],'cancelled')
                        self.assertEqual(runtime.resume(root/'work',rid)['state'],'completed')
                    else:self.assertEqual(runtime.execute(root/'work',rid)['state'],'completed')
                    analysis=runtime.analyze(root/'work',rid);report=runtime.report(root/'work',rid,plan=plan)
                    attempt='attempt-0002' if resumed else 'attempt-0001'
                    self.assertTrue(all(attempt in p for p in report['required_inputs'] if p.endswith('-traces.json')))
                    self.assertTrue(runtime.verify(root/'work',rid)['valid'])
                    self.assertNotEqual(analysis['classification'],'pass')
                    exported=export_run(root/'work',rid,plan,root/'export')
                    self.assertEqual(exported['run_id'],rid)
                    self.assertTrue(import_handoff(root/'export/handoff/pr-evidence-index.json',root/'imported')['verified'])

    def test_comparison_blocks_changed_physics(self):
        from signal_space.workflow.compare import differences,numerical_change
        a={'parameters':{'profile':{'sha256':'old'},'scenarios':[{'dt':.1}]}}
        b={'parameters':{'profile':{'sha256':'new'},'scenarios':[{'dt':.05}]}}
        delta=differences(a,b)
        self.assertEqual([r['path'] for r in delta if not numerical_change(r['path'])],['/parameters/profile/sha256'])

    def test_ledger_evidence_and_saved_panel(self):
        from signal_space.workflow.ledger import current
        from signal_space.reporting.panels import render_panel
        self.assertEqual(len(current()['tests']),11)
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);data=root/'trace.csv';data.write_text('series,x,y\nA,0,1\nA,1,.99\n')
            spec={'schema_version':'gross-panel-v1','kind':'clock-record','data':'trace.csv','sha256':sha256_file(data),'x_unit':'t / period','y_unit':'E_mode / E_initial','transformations':['saved ratio; no additional transformations'],
                  'interpretation':{'question':'Does the saved clock energy change?','reading':'Two manufactured points.','significance':'Engineering render test.','limitation':'No physical acceptance.'}}
            write_json(root/'spec.json',spec);render_panel(root/'spec.json',root/'panel')
            self.assertTrue((root/'panel/panel.pdf').is_file())
            self.assertEqual(sha256_file(data),sha256_file(root/'panel/plot-data.csv'))
            data.write_text('changed')
            with self.assertRaisesRegex(ValueError,'hash differs'):render_panel(root/'spec.json',root/'bad')


if __name__=='__main__':unittest.main()
