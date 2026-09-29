"""Engineering controls for GROSS-only execution; no new physical acceptance."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from signal_space.runtime.events import append_event, read_events
from signal_space.runtime.execution import ExecutionPolicy, cpu_capacity
from signal_space.runtime.errors import ResourceRejected, IntegrityError
from signal_space.runtime.io import read_json, sha256_file
from signal_space.runtime.runner import ResearchRuntime, _monitor_process, _terminate_process
from signal_space.runtime.scheduler import Budget, run_batch

ROOT = Path(__file__).resolve().parents[1]


def config(seed=1):
    value = read_json(ROOT / 'fixtures/research/gross-test-01.json')
    value['parameters']['samples'] = 20
    value['seeds']['root'] = seed
    return value


class GrossRuntimeTests(unittest.TestCase):
    def test_registry_is_gross_only_and_lazy(self):
        result = subprocess.run([sys.executable, '-c',
            "import sys; from signal_space.experiments.registry import get_experiment; get_experiment('gross.operator-identities.v1'); assert 'numpy' not in sys.modules"], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        runtime = ResearchRuntime()
        self.assertTrue(all(x['experiment_id'].startswith('gross.') for x in runtime.list()))
        with self.assertRaisesRegex(ValueError, 'unregistered GROSS'):
            runtime.validate({'experiment_id': 'e01-charged-branch'})

    def test_event_concurrency_and_truncated_tail(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'events.jsonl'
            def emit(i):
                append_event(path, 'test', 'test', {'value': i, 'large': 'a'*5000})
            with ThreadPoolExecutor(max_workers=6) as pool:
                list(pool.map(emit, range(80)))
            events = read_events(path)
            self.assertEqual([x['sequence'] for x in events], list(range(1, 81)))
            self.assertEqual(len(read_events(path, after=70)), 10)
            with path.open('ab') as stream:
                stream.write(b'{"unfinished":')
            with self.assertRaisesRegex(ValueError, 'truncated'):
                emit(81)

    def test_serial_parallel_raw_equivalence_and_verification(self):
        runtime = ResearchRuntime()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            serial = run_batch(runtime, [config(1), config(2)], root/'serial', Budget(jobs=1))
            parallel = run_batch(runtime, [config(1), config(2)], root/'parallel', Budget(jobs=min(2, cpu_capacity())))
            self.assertEqual(serial['state'], 'completed')
            self.assertEqual(parallel['state'], 'completed')
            for a, b in zip(serial['members'], parallel['members']):
                self.assertEqual(a['config_sha256'], b['config_sha256'])
                for name in ('measurements.csv', 'controls.json', 'conditioning.json', 'rng-start.json', 'rng-end.json'):
                    self.assertEqual((Path(a['result']['path'])/'attempts/attempt-0001/raw'/name).read_bytes(),
                                     (Path(b['result']['path'])/'attempts/attempt-0001/raw'/name).read_bytes())
                self.assertTrue(runtime.verify(root/'parallel', b['result']['run_id'])['valid'])
                self.assertEqual(read_json(Path(b['result']['path'])/'provenance/environment.json')['execution_policy'],
                                 {'threads': 1, 'case_jobs': 1})

    def test_admission_before_launch_duplicate_and_unfit(self):
        runtime = ResearchRuntime()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with self.assertRaisesRegex(ValueError, 'duplicate'):
                run_batch(runtime, [config(), config()], root)
            with self.assertRaises(ResourceRejected):
                run_batch(runtime, [config()], root, Budget(memory_mb=1))
            with self.assertRaises(ResourceRejected):
                run_batch(runtime, [config()], root, Budget(output_mb=1))
            self.assertFalse(list(root.rglob('manifest.json')))

    def test_scheduler_reserves_memory_and_keeps_member_failure(self):
        class Runtime:
            active = peak = 0
            lock = threading.Lock()
            def validate(self, c): return c
            def estimate(self, c, **kwargs): return {'accepted': True}
            def run(self, c, workspace, **kwargs):
                with self.lock:
                    self.active += 1
                    self.peak = max(self.peak, self.active)
                time.sleep(.02)
                with self.lock: self.active -= 1
                return {'state': 'failed' if c['seeds']['root'] == 2 else 'completed'}
        runtime = Runtime()
        with tempfile.TemporaryDirectory() as folder:
            record = run_batch(runtime, [config(1), config(2), config(3)], Path(folder), Budget(jobs=3, memory_mb=512))
            self.assertEqual(runtime.peak, 1)
            self.assertEqual(record['state'], 'failed')
            self.assertEqual([x['status'] for x in record['members']], ['completed', 'failed', 'completed'])
            self.assertEqual(read_json(Path(record['path'])), record)

    def test_queued_cancellation_never_launches(self):
        event = threading.Event(); event.set()
        with tempfile.TemporaryDirectory() as folder:
            result = run_batch(ResearchRuntime(), [config()], Path(folder), cancel_event=event)
            self.assertEqual(result['state'], 'cancelled')
            self.assertEqual(result['executed'], 0)

    def test_immutable_analysis_report_and_tamper_detection(self):
        runtime = ResearchRuntime()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            run = runtime.run(config(), root)
            self.assertEqual(run['state'], 'completed')
            raw = Path(run['path'])/'attempts/attempt-0001/raw/measurements.csv'
            before = sha256_file(raw)
            a = runtime.analyze(root, run['run_id'])
            b = runtime.analyze(root, run['run_id'])
            self.assertEqual(b['supersedes'], a['analysis_id'])
            runtime.report(root, run['run_id'], b['analysis_id'])
            self.assertTrue(runtime.verify(root, run['run_id'])['valid'])
            self.assertEqual(sha256_file(raw), before)
            raw.write_text('tampered', encoding="utf-8")
            with self.assertRaises(IntegrityError):
                runtime.analyze(root, run['run_id'])

    def test_aggregate_output_limit(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for i in range(3): (root/f'{i}.bin').write_bytes(b'x'*500000)
            process = subprocess.Popen([sys.executable, '-c', 'import time;time.sleep(30)'], start_new_session=os.name=='posix')
            try:
                reason, _ = _monitor_process(process, root, {'max_wall_seconds': 2, 'max_output_mb': 1, 'max_memory_mb': 512, 'max_cpu_seconds': 5})
                self.assertEqual(reason, 'output')
            finally:
                _terminate_process(process, cooperative_seconds=0)
            self.assertIsNotNone(process.poll())

    def test_process_tree_owns_descendant_after_parent_exit(self):
        from signal_space.runtime.processes import ProcessTree
        with tempfile.TemporaryDirectory() as folder:
            ready, late = Path(folder)/'ready', Path(folder)/'late'
            child = "import time; from pathlib import Path; time.sleep(1); Path("+repr(str(late))+").touch()"
            parent = "import subprocess,sys; from pathlib import Path; subprocess.Popen([sys.executable,'-c',"+repr(child)+"]); Path("+repr(str(ready))+").touch()"
            # The Job Object must be assigned before the parent exits on Windows.
            parent = "import time; time.sleep(.2); " + parent
            process = subprocess.Popen([sys.executable, '-c', parent], start_new_session=os.name=='posix')
            tree = ProcessTree(process)
            try:
                process.wait(timeout=5)
                self.assertTrue(ready.exists())
            finally:
                tree.close()
            time.sleep(1.1)
            self.assertFalse(late.exists(), 'orphaned child survived worker exit')

    def test_worker_thread_policy_replaces_inherited_oversubscription(self):
        environment = ExecutionPolicy(threads=1).environment()
        self.assertEqual(environment['OPENBLAS_NUM_THREADS'], '1')
        self.assertEqual(environment['NUMBA_NUM_THREADS'], '1')
        with self.assertRaises(ValueError): ExecutionPolicy(threads=0)


if __name__ == '__main__': unittest.main()
