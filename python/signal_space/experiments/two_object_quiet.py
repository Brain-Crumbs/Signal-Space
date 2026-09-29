"""Prospective, short spatial/quiet calibration prerequisite for Test 8."""

from copy import deepcopy
from pathlib import Path

from signal_space.contracts.schema import check
from signal_space.experiments.base import ExperimentPlugin
from signal_space.runtime.io import read_json, write_json

ROOT = Path(__file__).resolve().parents[3]
CRITERIA = {
    'source-identity': 'The frozen Test 6 source has the registered byte hash.',
    'neutral-null': 'The unseeded neutral canonical sector remains exactly zero.',
    'sink-ledger': 'Energy including damping work closes on the weak mode scale, and charge including the sink closes.',
    'distinct-pair': 'Two measurable, separated quiet cores remain through this short observation.',
    'short-clocks': 'Measured mode projection and local ticks remain usable during six signed-field periods.',
    'independent-controls': 'The pair has separately varied spatial grid, time step and outer boundary.',
    'joint-preparation': 'A solved or physically settled joint quiet pair is established without pins or post-source re-relaxation.',
    'long-clocks': 'Isolated and quiet clocks survive 100 periods with mode, flux and domain controls.',
    'full-exchange': 'Issue #82 G0–G9 including both source channels, recoil and Test 9 data.'
}


class TwoObjectQuietExperiment(ExperimentPlugin):
    experiment_id = 'gross.two-object-quiet-calibration.v1'
    model_id = 'signal-space.ss-ocf-1.flat-axisymmetric-neutral-clock.v1'
    version = '0.2.0'

    def describe(self):
        return {'experiment_id': self.experiment_id, 'model_id': self.model_id,
                'version': self.version, 'name': 'Signal Space Test 8 outgoing-layer quiet calibration',
                'equations': ['Operator Program v0.2 sections 7–10, 15.8'],
                'equation_sources': [{'label': 'Test 8 protocol', 'path': 'docs/research/gross-test-08.md',
                                      'catalog_id': 'gross-test-08'}],
                'capabilities': ['axisymmetric', 'outgoing-layer', 'short-clock', 'quiet-pair', 'checkpoint', 'resume', 'analysis', 'report'],
                'unavailable_capabilities': ['joint-relaxed pair', '100-period result',
                                               'source exchange', 'recoil', 'Test 9 readiness']}

    def schema(self):
        schema = read_json(ROOT / 'contracts/research/two-object-quiet.schema.json')
        schema['default'] = read_json(ROOT / 'fixtures/research/gross-test-08-quiet.json')
        return schema

    def validate(self, config):
        check(config, self.schema())
        p = config['parameters']
        options = p.get('execution', {})
        if options.get('neutral_mode') == 'exact-zero' and options.get('backend') != 'numba':
            raise ValueError('exact-zero specialization requires the compiled backend')
        scenarios = {s['label']: s for s in p['scenarios']}
        required = {'isolated-base', 'isolated-fine', 'pair-base', 'pair-fine', 'pair-time', 'pair-wide'}
        if set(scenarios) != required:
            raise ValueError(f'quiet qualification requires exact controls: {sorted(required)}')
        base = scenarios['pair-base']
        for label, scenario in scenarios.items():
            h = scenario['h']
            if abs(round(scenario['radius'] / h) * h - scenario['radius']) > 1e-8:
                raise ValueError(f'{label}: radius must be an integer number of cells')
            if abs(round(2 * scenario['half_length'] / h) * h - 2 * scenario['half_length']) > 1e-8:
                raise ValueError(f'{label}: length must be an integer number of cells')
            if scenario['dt'] > .25 * h / 2**.5:
                raise ValueError(f'{label}: time step exceeds the 2D safety factor')
            if scenario['absorber_width'] < 4 * h or scenario['absorber_width'] >= scenario['radius'] - 18:
                raise ValueError(f'{label}: absorber must occupy a resolved outer annulus beyond mode containment')
            if scenario['pair'] and scenario['half_length'] < p['separation'] / 2 + 22:
                raise ValueError(f'{label}: axial boundary cuts the separated core region')
            if scenario['periods'] != 6:
                raise ValueError('this locked qualification requires six frozen periods')
        if scenarios['pair-time']['h'] != base['h'] or scenarios['pair-time']['dt'] != base['dt'] / 2:
            raise ValueError('independent time control must keep the base spatial mesh')
        if scenarios['pair-wide']['h'] != base['h'] or scenarios['pair-wide']['dt'] != base['dt']:
            raise ValueError('domain control must keep base mesh and time step')
        if scenarios['pair-wide']['radius'] <= base['radius'] or scenarios['pair-wide']['half_length'] <= base['half_length']:
            raise ValueError('domain control must enlarge both extents')
        if scenarios['pair-fine']['h'] >= base['h'] or scenarios['pair-fine']['dt'] >= base['dt']:
            raise ValueError('fine control must resolve both space and time')
        if any(not scenarios[n]['pair'] for n in required if n.startswith('pair-')):
            raise ValueError('pair controls require two physical objects')
        if any(scenarios[n]['pair'] for n in ('isolated-base', 'isolated-fine')):
            raise ValueError('isolated controls must contain one object')
        return deepcopy(config)

    def acceptance_criteria(self, config):
        return [{'id': name, 'description': description, 'evidence': None}
                for name, description in CRITERIA.items()]

    def known_gaps(self, config):
        return ['Six frozen periods, not the hundred-period longevity gate.',
                'Pair begins as a naive superposition and evolves freely; no stationary joint solve.',
                'Damped outer layer is an explicit numerical intervention requiring independent domain checks.',
                'No signal, measured axial recoil or postinteraction Test 9 record.']

    def estimate(self, config):
        scenarios = config['parameters']['scenarios']
        cells_steps = sum(round(s['radius'] / s['h']) * round(2 * s['half_length'] / s['h'])
                          * round(s['periods'] * 2 * 3.141592653589793 / (.41274991 * s['dt']))
                          for s in scenarios)
        biggest = max(round(s['radius'] / s['h']) * round(2 * s['half_length'] / s['h'])
                      for s in scenarios)
        stride = config['parameters'].get('execution', {}).get('checkpoint_stride', 1000)
        # Include every retained checkpoint, final state, geometry and a trace/
        # metadata allowance. Compression is not credited before measurement.
        checkpoint_bytes = sum(
            round(s['radius']/s['h']) * round(2*s['half_length']/s['h']) * 72
            * ((round(s['periods']*2*3.141592653589793/(.41274991*s['dt'])) - 1)//stride + 1)
            for s in scenarios)
        # Legacy CPU/wall projection, not measured optimized throughput. The
        # separate campaign preflight remains blocked pending full-case costs.
        return {'cpu_seconds': max(300, int(cells_steps / 2500000)),
                'wall_seconds': max(330, int(cells_steps / 2200000)),
                'memory_mb': max(300, int(biggest * .004) + 150),
                'disk_mb': max(40, int(sum(round(s['radius']/s['h']) * round(2*s['half_length']/s['h'])
                                           for s in scenarios) * .00015) + 25) + (checkpoint_bytes + 1048575)//1048576,
                'wall_time_class': 'long'}

    def prepare(self, config, run_path, attempt_path, resume):
        if resume and resume.get('kind') != 'signal-space-quiet-fv-rk4-v1':
            raise ValueError('unsupported quiet checkpoint')
        if config['parameters'].get('execution', {}).get('backend') == 'numba':
            try:
                from signal_space.numerics.two_object_compiled import CompiledStepper
            except ImportError as error:
                raise ValueError('numba backend requires python/requirements-performance-lock.txt in an isolated environment') from error
        preparation = {'source': 'docs/research/gross-test-08-quiet.md',
                       'status': 'short outgoing-layer qualification; no exchange'}
        write_json(attempt_path / 'preparation.json', preparation)
        return preparation

    def run(self, request_path):
        from signal_space.numerics.two_object_quiet import execute
        return execute(request_path)

    def analyze(self, run_path, analysis_path, config):
        from signal_space.analysis.two_object_quiet import analyze
        return analyze(run_path, analysis_path, config)

    def classify(self, checks, config):
        statuses = {row['id']: row['status'] for row in checks['checks']}
        if set(statuses) != set(CRITERIA):
            return 'unresolved'
        if any(status == 'fail' for status in statuses.values()):
            return 'fail'
        return 'pass' if all(status == 'pass' for status in statuses.values()) else 'unresolved'

    def report(self, run_path, report_path, manifest, analysis, render_provenance):
        from signal_space.reporting.two_object_quiet import render_report
        return render_report(run_path, report_path, manifest, analysis, render_provenance)
