"""Engineering contract/negative controls; not the locked scientific pilot."""
import copy
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from signal_space.experiments.registry import get_experiment
from signal_space.runtime.certificate_budget import reserve,RESERVATIONS
from signal_space.numerics.certificate_controls import evaluate_controls

ROOT=Path(__file__).resolve().parents[1]


class PilotContracts(unittest.TestCase):
    def test_closed_registration_rejects_scientific_changes(self):
        p=get_experiment('gross.local-record-certificate.v1');c=p.schema()['default']
        self.assertEqual(p.validate(c),c)
        edits=[lambda x:x['parameters'].__setitem__('physical_directions',15),
               lambda x:x['parameters'].__setitem__('seeds',['active-plus']),
               lambda x:x['parameters'].__setitem__('word',[1,0]),
               lambda x:x['parameters'].__setitem__('coupling','machine-pi/2'),
               lambda x:x['parameters'].__setitem__('stage','confirmation'),
               lambda x:x['parameters'].__setitem__('cycles',32),
               lambda x:x['resources'].__setitem__('max_wall_seconds',300),
               lambda x:x['parameters']['source_sha256'].__setitem__('src/signal_space/numerics/dyadic.py','0'*64),
               lambda x:x.__setitem__('rounding','nearest')]
        for edit in edits:
            bad=copy.deepcopy(c);edit(bad)
            with self.assertRaises(ValueError):p.validate(bad)
        with patch('signal_space.numerics.validated_linked_memory.PYTHON',()):
            with self.assertRaises(ValueError):p.validate(c)
        e=p.estimate(c)
        self.assertGreater(e['cpu_seconds'],0)
        self.assertLessEqual(e['wall_seconds'],c['resources']['max_wall_seconds'])

    def test_budget_reservation_is_atomic_and_no_retry_replenishes_it(self):
        self.assertEqual(sum(x[0] for x in RESERVATIONS.values()),300)
        self.assertEqual(sum(x[2] for x in RESERVATIONS.values()),128)
        with tempfile.TemporaryDirectory() as d:
            run=Path(d)/'run-1'
            def attempt(_):
                try:return reserve(run,'pilot-worker')
                except FileExistsError:return None
            with ThreadPoolExecutor(2) as pool:results=list(pool.map(attempt,range(2)))
            self.assertEqual(sum(x is not None for x in results),1)
            with self.assertRaises(FileExistsError):reserve(Path(d)/'run-changed-source','pilot-worker')
            reserve(run,'pilot-analysis')
            self.assertEqual(len(list((Path(d)/'.c1-budget-v1').glob('*.json'))),2)

    def test_failed_analysis_preserves_context_and_bounded_threads(self):
        import subprocess,sys,shutil
        from signal_space.runtime.certificate_budget import analyze_saved
        original=subprocess.Popen;seen=[]
        def fail(command,**kwargs):
            seen.append(kwargs['env'])
            return original([sys.executable,'-c','print("retained failure");raise SystemExit(1)'],**kwargs)
        with tempfile.TemporaryDirectory() as d:
            run=Path(d)/'run-1';output=run/'analyses'/'analysis-1'
            with patch('subprocess.Popen',fail):
                with self.assertRaises(RuntimeError):analyze_saved(run,output,{})
            shutil.rmtree(output,ignore_errors=True)
            saved=Path(d)/'.c1-analysis-attempts'/'run-1'/'analysis-1'
            for f in ('checker.log','checker-request.json','resource-usage.json','failure.json'):
                self.assertTrue((saved/f).is_file(),f)
            self.assertIn('retained failure',(saved/'checker.log').read_text())
            for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
                self.assertEqual(seen[0][name],'1')

    def test_dirty_sources_reject_before_reserving_scientific_budget(self):
        plugin=get_experiment('gross.local-record-certificate.v1')
        with tempfile.TemporaryDirectory() as d:
            with patch('signal_space.runtime.package.code_identity',return_value={'tree_state':'dirty'}):
                with self.assertRaises(ValueError):plugin.prepare(plugin.schema()['default'],Path(d)/'run',Path(d)/'attempt',None)
            self.assertFalse((Path(d)/'.c1-budget-v1').exists())

    def test_unresolved_not_promoted_from_technical_success(self):
        p=get_experiment('gross.local-record-certificate.v1');c=p.schema()['default']
        checks={'checks':[dict(id=x['id'],status='pass') for x in p.acceptance_criteria(c)]}
        self.assertEqual(p.classify(checks,c),'pass')
        checks['checks'][2]['status']='unresolved'
        self.assertEqual(p.classify(checks,c),'unresolved')
        checks['checks'].pop()
        self.assertEqual(p.classify(checks,c),'unresolved')

    def test_zero_prefix_preserves_unresolved_scientific_handoff(self):
        import os
        from signal_space.numerics import record_tubes
        from signal_space.numerics.local_certificate import execute
        from signal_space.analysis.local_certificate import analyze
        original=record_tubes.produce
        def no_prefix(*args,**kwargs):
            with patch('signal_space.numerics.validated_linked_memory.evaluate',return_value={'status':'unresolved','reason':'injected enclosure obstruction'}):
                return original(*args,**kwargs)
        c=get_experiment('gross.local-record-certificate.v1').schema()['default']
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);attempt=root/'attempts'/'attempt-1';attempt.mkdir(parents=True)
            request=root/'request.json';request.write_text(json.dumps(dict(attempt_path=str(attempt),config=c)))
            env={k:'1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS')}
            with patch.dict(os.environ,env),patch.object(record_tubes,'produce',no_prefix):
                self.assertEqual(execute(request),0)
            out=root/'analysis';out.mkdir()
            result=analyze(root,out,c)
            statuses={x['id']:x['status'] for x in result['checks']['checks']}
            self.assertEqual(statuses['coverage'],'unresolved')
            self.assertEqual(statuses['one-cycle-budgets'],'unresolved')
            self.assertFalse(result['summary']['launch_allowed'])
            self.assertEqual((out/'derived'/'record-budgets.csv').read_text().count('\n'),1)

    def test_complete_controls_and_saved_replay_without_an_ode_rerun(self):
        proofs=[json.loads((ROOT/f'tests/fixtures/record-tube-proof-{s}.json').read_text())
                for s in ('active-plus','active-minus')]
        with tempfile.TemporaryDirectory() as d:
            raw,out=Path(d)/'raw',Path(d)/'replay'
            results=evaluate_controls(proofs,raw)
            self.assertTrue(all(r['status']=='pass' for r in results),results)
            with patch('scipy.integrate.solve_ivp',side_effect=AssertionError('ODE rerun')):
                replay=evaluate_controls(proofs,out,saved=raw)
            self.assertEqual(results,replay)
            calls=json.loads((raw/'local-controls.json').read_text())
            calls[0]['gate']['values'][0]['hi']='0'
            (raw/'local-controls.json').write_text(json.dumps(calls))
            with self.assertRaises(ValueError):evaluate_controls(proofs,Path(d)/'corrupt',saved=raw)


if __name__=='__main__':unittest.main()
