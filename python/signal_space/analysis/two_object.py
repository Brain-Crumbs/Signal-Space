"""Immutable analysis of Test 8 spatial calibration pilot (not exchange)."""
import csv
from pathlib import Path

import numpy as np

from signal_space.runtime.io import read_json, write_json


def analyze(run_path, analysis_path, config):
    attempt = next(iter(sorted((run_path/'attempts').glob('attempt-*'))))
    raw = attempt/'raw'
    scenarios = read_json(raw/'scenarios.json')
    derived = analysis_path/'derived'
    derived.mkdir(parents=True, exist_ok=True)
    rows = []
    for item in scenarios:
        with np.load(raw/f"{item['label']}.npz") as data:
            samples = data['samples']
            assert samples.shape[1] == 4 + int(item['pair'])
            for record in samples:
                rows.append({'scenario':item['label'],'t':float(record[0]),
                             'energy':float(record[1]),'charge':float(record[2]),
                             'chi_A':float(record[3]),
                             'chi_B':float(record[4]) if item['pair'] else ''})
    with (derived/'traces.csv').open('w',newline='') as stream:
        writer = csv.DictWriter(stream,fieldnames=['scenario','t','energy','charge','chi_A','chi_B'])
        writer.writeheader()
        writer.writerows(rows)
    write_json(derived/'summary.json',{'stage':'spatial-calibration-pilot',
                'scenarios':scenarios, 'full_test_8':'not-evaluated',
                'note':'Two-center initial state is an unrelaxed superposition; short mirror-box traces do not establish lifetime, recoil or reception.'})
    limits = config['analysis']
    closed = all(x['max_neutral'] == 0 for x in scenarios)
    ledgers = all(x['max_energy_drift_fraction'] < limits['max_energy_drift_fraction']
                  and x['max_charge_drift_fraction'] < limits['max_charge_drift_fraction'] for x in scenarios)
    checks = [
      {'id':'frozen-source','status':'pass','value':{'source':read_json(raw/'source.json')},'evidence':'derived/summary.json'},
      {'id':'closed-sector','status':'pass' if closed else 'fail',
       'value':{'maximum':max(x['max_neutral'] for x in scenarios)},'evidence':'derived/summary.json'},
      {'id':'short-ledgers','status':'pass' if ledgers else 'fail',
       'value':{'limits':limits,'scenarios':[{k:x[k] for k in ('label','max_energy_drift_fraction','max_charge_drift_fraction')}
                                              for x in scenarios]},'evidence':'derived/summary.json'},
      {'id':'spatial-calibration','status':'unresolved','value':{'reason':'Only 16 time units, no independent timestep/domain or 100-period longevity; pair not jointly relaxed.'},'evidence':'derived/summary.json'},
      {'id':'full-exchange','status':'not-evaluated','value':{'reason':'No packet, structural companion, measured momentum flux, or Test 9 handoff.'},'evidence':'derived/summary.json'}
    ]
    output = {'schema_version':'research-checks-v1','checks':checks}
    write_json(analysis_path/'checks.json',output)
    return {'raw_source':(attempt/'raw'/'scenarios.json').relative_to(run_path).as_posix(),'checks':output,
            'summary':read_json(derived/'summary.json')}
