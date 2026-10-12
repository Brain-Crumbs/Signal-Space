"""Test 8's doublet preparation/evolution implementation qualification."""
from copy import deepcopy
from math import ceil
from pathlib import Path

from signal_space.contracts.schema import check
from signal_space.experiments.base import ExperimentPlugin
from signal_space.runtime.io import read_json, write_json

ROOT = Path(__file__).resolve().parents[3]
CRITERIA = {
    'source-identity': 'Frozen radial profile matches its exact byte identity.',
    'neutral-null': 'All unseeded neutral fields and momenta remain exactly zero.',
    'global-ledgers': 'Energy plus absorber work and charge plus sink meet the locked short-pilot limits.',
    'residual-reduction': 'Bounded corrections strictly reduce the actual unprojected discrete quiet residual.',
    'local-records': 'Both components and local timelike detector records are retained with valid envelopes.',
    'independent-controls': 'Fixed-dt spatial, fixed-grid temporal and fixed-grid/time domain comparisons are retained.',
    'source-controls': 'Compact neutral and structural initial data have matched quiet and sign controls.',
    'long-clocks': '100-period and postinteraction survival qualification is available.',
    'exchange-recoil': 'Full held-out G0-G9 reception, stress-recoil closure and Test 9 readiness.'
}


class TwoObjectEvolutionExperiment(ExperimentPlugin):
    experiment_id = 'gross.two-object-evolution.v1'
    model_id = 'signal-space.ss-ocf-1.flat-axisymmetric-doublet.v1'
    version = '0.1.0'

    def describe(self):
        return {'experiment_id': self.experiment_id, 'model_id': self.model_id,
                'version': self.version, 'name': 'Test 8 doublet pair preparation/evolution pilot',
                'equations': ['SS OCF 1 §§7-10, 15.8; both complex doublet components'],
                'capabilities': ['free-evolution', 'doublet', 'residual-reduction', 'local-records',
                                 'compact-initial-sources', 'flux-diagnostics', 'checkpoint', 'resume', 'report'],
                'unavailable_capabilities': ['full-exchange-acceptance', 'Test-9-reconstruction', 'generic-3D-stability']}

    def schema(self):
        schema = read_json(ROOT / 'contracts/research/two-object-evolution.schema.json')
        schema['default'] = read_json(ROOT / 'fixtures/research/gross-test-08-evolution-pilot.json')
        return schema

    def validate(self, config):
        check(config, self.schema())
        cases = config['parameters']['scenarios']
        by_label = {c['label']: c for c in cases}
        if len(by_label) != len(cases):
            raise ValueError('duplicate doublet scenario label')
        required = {'pair-base', 'pair-space', 'pair-time', 'pair-wide', 'pair-reduced',
                    'isolated-base', 'isolated-reduced', 'pair-quadrature', 'pair-orthogonal',
                    'neutral-plus', 'neutral-minus', 'structural-plus', 'structural-minus'}
        if set(by_label) != required:
            raise ValueError('doublet pilot requires its complete 13-case control matrix')
        base = by_label['pair-base']
        changed = {'pair-space': {'label', 'h'}, 'pair-time': {'label', 'dt', 'sample_stride'},
                   'pair-wide': {'label', 'radius', 'half_length'},
                   'pair-reduced': {'label', 'preparation'},
                   'isolated-base': {'label', 'pair'}, 'isolated-reduced': {'label', 'pair', 'preparation'},
                   'pair-quadrature': {'label', 'matter_phase'}, 'pair-orthogonal': {'label', 'orientation'},
                   'neutral-plus': {'label', 'source'}, 'neutral-minus': {'label', 'source'},
                   'structural-plus': {'label', 'source'}, 'structural-minus': {'label', 'source'}}
        for c in cases:
            for key in base:
                if key not in changed.get(c['label'], set()) and key != 'label' and c[key] != base[key]:
                    raise ValueError(f"{c['label']}: unintended control change in {key}")
            if any(abs(round(x / c['h']) * c['h'] - x) > 1e-9
                   for x in (c['radius'], 2*c['half_length'])):
                raise ValueError('domain must contain an integer number of cells')
            if c['dt'] > .25 * c['h'] / 2**.5:
                raise ValueError('doublet RK4 safety factor exceeded')
            if abs(round(c['duration'] / c['dt']) * c['dt'] - c['duration']) > 1e-9:
                raise ValueError('duration must contain an integer number of steps')
            if c['absorber_width'] < 4*c['h'] or c['absorber_width'] >= c['radius'] - c['tube_radius']:
                raise ValueError('absorber overlaps tracking tube or is underresolved')
            if c['half_length'] - c['absorber_width'] <= c['separation']/2 + c['tube_radius']:
                raise ValueError('axial absorber overlaps a detector tube')
            if c['pair'] and 2*c['tube_radius'] >= c['separation']:
                raise ValueError('detector tubes overlap')
            if c['sample_stride'] * c['dt'] > .2:
                raise ValueError('local clock records are undersampled')
            if c['source']['radius'] + c['h'] >= c['separation'] - c['tube_radius']:
                raise ValueError('initial source stencil touches the receiver tube')
            if c['source']['channel'] == 'none' and c['source']['amplitude'] != 0:
                raise ValueError('quiet source must be exactly zero')
        if by_label['pair-space']['h'] >= base['h'] or by_label['pair-time']['dt'] != base['dt']/2:
            raise ValueError('missing independent space/time refinement')
        if (by_label['pair-wide']['radius'] <= base['radius']
                or by_label['pair-wide']['half_length'] <= base['half_length']):
            raise ValueError('domain control must enlarge both extents')
        if any(by_label[k]['preparation'] != 'residual-reduced' for k in ('pair-reduced', 'isolated-reduced')):
            raise ValueError('missing matched residual-reduced preparations')
        if any(by_label[k]['pair'] for k in ('isolated-base', 'isolated-reduced')):
            raise ValueError('isolated control contains a pair')
        if any(not c['pair'] for c in cases if not c['label'].startswith('isolated-')):
            raise ValueError('pair control contains only one object')
        for channel in ('neutral', 'structural'):
            plus, minus = by_label[f'{channel}-plus']['source'], by_label[f'{channel}-minus']['source']
            if plus['channel'] != channel or minus['channel'] != channel or plus['amplitude'] <= 0:
                raise ValueError('source control has wrong channel/sign')
            if minus != {**plus, 'amplitude': -plus['amplitude']}:
                raise ValueError('source reversal must preserve every other preparation input')
        if base['source']['channel'] != 'none' or base['preparation'] != 'naive':
            raise ValueError('reference must be an unforced naive quiet pair')
        if abs(by_label['pair-quadrature']['matter_phase'] - 1.5707963267948966) > 1e-14:
            raise ValueError('quadrature control requires pi/2 matter phase')
        if abs(by_label['pair-orthogonal']['orientation'] - 1.5707963267948966) > 1e-14:
            raise ValueError('orthogonal control requires pi/2 internal angle')
        return deepcopy(config)

    def acceptance_criteria(self, config):
        return [{'id': k, 'description': v, 'evidence': None} for k, v in CRITERIA.items()]

    def known_gaps(self, config):
        return ['Short implementation pilot, not the full issue #82 G0-G9 campaign.',
                'Residual-reduced initial data are not an unconstrained stationary pair.',
                'Nominal Test 6 profile/stencil, not a continuum error enclosure.',
                'Fixed control-volume stress is a continuum diagnostic, not exact discrete momentum closure.',
                'Sources are compact initial excitations, not spontaneous neutral emission.',
                '100-period survival, held-out source selection, amplitude ladders and Test 9 history remain pending.']

    def estimate(self, config):
        cases = config['parameters']['scenarios']
        work = sum(round(c['radius']/c['h']) * round(2*c['half_length']/c['h'])
                   * round(c['duration']/c['dt']) for c in cases)
        cells = max(round(c['radius']/c['h']) * round(2*c['half_length']/c['h']) for c in cases)
        checkpoints = sum(ceil(round(c['duration']/c['dt']) / config['parameters']['checkpoint_stride'])
                          * round(c['radius']/c['h']) * round(2*c['half_length']/c['h']) * 96 for c in cases)
        # Conservative initial admission estimate; actual timings are retained.
        return {'cpu_seconds': max(120, ceil(work/90000)), 'wall_seconds': max(150, ceil(work/80000)),
                'memory_mb': max(256, ceil(cells * .008) + 180),
                'disk_mb': ceil(checkpoints/1048576) + ceil(sum(round(c['radius']/c['h'])
                           * round(2*c['half_length']/c['h']) * 192 for c in cases)/1048576) + 80,
                'wall_time_class': 'bounded'}

    def prepare(self, config, run_path, attempt_path, resume):
        if resume and resume.get('kind') != 'signal-space-doublet-pair-rk4-v1':
            raise ValueError('unsupported doublet resume')
        result = {'protocol': 'docs/research/gross-test-08-evolution.md',
                  'scope': 'preparation/evolution implementation qualification'}
        write_json(attempt_path / 'preparation.json', result)
        return result

    def run(self, request_path):
        from signal_space.numerics.two_object_evolution_worker import execute
        return execute(request_path)

    def analyze(self, run_path, analysis_path, config):
        from signal_space.analysis.two_object_evolution import analyze
        return analyze(run_path, analysis_path, config)

    def classify(self, checks, config):
        return 'fail' if any(c['status'] == 'fail' for c in checks['checks']) else 'unresolved'

    def report(self, run_path, report_path, manifest, analysis, render_provenance):
        from signal_space.reporting.two_object_evolution import render_report
        return render_report(run_path, report_path, manifest, analysis, render_provenance)
