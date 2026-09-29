"""Evidence-linked current ledger; historical prose and acceptance remain separate."""
from signal_space.workflow.plans import ROOT
from signal_space.runtime.io import read_json, sha256_file, safe_child


def current():
    value=read_json(ROOT/'docs/research/gross-progress.json')
    if value['schema_version']!='gross-progress-ledger-v1' or [r['test'] for r in value['tests']]!=list(range(1,12)):
        raise ValueError('ledger must contain Tests 1–11 exactly once in order')
    for row in value['tests']:
        for source in row['evidence']:
            if sha256_file(safe_child(ROOT,source['path']))!=source['sha256']:
                raise ValueError(f'ledger evidence changed for Test {row["test"]}; review the record before updating its hash')
    return value


def markdown(value=None):
    value=value or current()
    lines=['# Current GROSS research status','',f"Evidence snapshot: {value['as_of']}.",'',value['scope'],'',
           '| Test | Scope | Status | Evidence-supported limits |','| --- | --- | --- | --- |']
    for row in value['tests']:
        source=row['evidence'][0]['path']
        # Generated document lives in docs/research.
        link='../../'+source
        lines.append(f"| {row['test']} | {row['title']} | [{row['status']}]({link}) | {row['scope']} |")
    lines += ['', 'Generate with `signal-space ledger --markdown`; machine record: `docs/research/gross-progress.json`.',
              'Engine availability is separate: `signal-space capabilities`. Full Test 8 design: `signal-space campaign inspect test8`.','']
    return '\n'.join(lines)
