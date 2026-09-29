"""Recursive event cursors and terminal-friendly status, without a UI service."""
from datetime import datetime
import json
from pathlib import Path

from signal_space.runtime.io import read_json, write_json


class EventStream:
    def __init__(self, run_path, cursor_file=None):
        self.root = Path(run_path).resolve()
        self.cursor_file = Path(cursor_file).resolve() if cursor_file else None
        if self.cursor_file and self.cursor_file.is_relative_to(self.root):
            raise ValueError('event cursor must be outside immutable run evidence')
        self.cursors = {}
        if self.cursor_file and self.cursor_file.exists():
            record = read_json(self.cursor_file)
            if record.get('run_path') != str(self.root):
                raise ValueError('cursor belongs to a different run')
            self.cursors = record['streams']

    def poll(self, after=0):
        rows = []
        for path in sorted((self.root / 'attempts').glob('attempt-*/**/events.jsonl')):
            name = path.relative_to(self.root).as_posix()
            cursor = self.cursors.get(name, {'offset': 0, 'sequence': 0})
            if path.stat().st_size < cursor['offset']:
                raise ValueError(f'event stream was truncated: {name}')
            with path.open('rb') as stream:
                stream.seek(cursor['offset'])
                while True:
                    offset = stream.tell()
                    line = stream.readline()
                    if not line or not line.endswith(b'\n'):
                        stream.seek(offset)
                        break
                    event = json.loads(line)
                    if event['sequence'] != cursor['sequence'] + 1:
                        raise ValueError(f'event sequence discontinuity: {name}')
                    cursor = {'offset': stream.tell(), 'sequence': event['sequence']}
                    parts = path.relative_to(self.root).parts
                    case = parts[3] if len(parts) > 4 and parts[2] == 'cases' else None
                    if event['sequence'] > after:
                        rows.append({**event, 'run_id': self.root.name, 'attempt_id': parts[1],
                                     'case': case, 'stream': name})
            self.cursors[name] = cursor
        return sorted(rows, key=lambda row: (row['timestamp'], row['stream'], row['sequence']))

    def acknowledge(self):
        if self.cursor_file:
            write_json(self.cursor_file, {'schema_version': 'gross-event-cursor-v1',
                                         'run_path': str(self.root), 'streams': self.cursors})


def snapshot(run_path):
    root = Path(run_path)
    manifest = read_json(root / 'manifest.json')
    config = read_json(root / 'resolved-config.json')
    cases = {row['label']: {'label': row['label'], 'state': 'queued'}
             for row in config.get('parameters', {}).get('scenarios', []) if 'label' in row}
    latest = manifest['attempts'][-1] if manifest['attempts'] else None
    for event in EventStream(root).poll():
        if latest and event['attempt_id'] != latest['attempt_id']:
            continue
        data = event['payload']
        label = data.get('label') or event['case']
        if not label:
            continue
        row = cases.setdefault(label, {'label': label, 'state': 'running'})
        if event['type'].startswith('scenario-'):
            row.update({key: data[key] for key in ('step', 'total_steps', 'elapsed_seconds', 'steps_per_second') if key in data})
            if event['type'] in {'scenario-started', 'scenario-completed', 'scenario-failed', 'scenario-cancelled'}:
                row['state'] = event['type'].removeprefix('scenario-')
        if event['type'] == 'checkpoint-written':
            row['checkpoint_at'] = event['timestamp']
        if event['type'] == 'scenario-progress':
            row['updated_at'] = event['timestamp']
            row['state'] = 'running'
    telemetry = {}
    if latest:
        for filename in ('telemetry.json', 'resource-usage.json'):
            path = root / latest['path'] / filename
            if path.exists():
                telemetry = read_json(path)
    return {'run_id': manifest['run_id'], 'technical_state': manifest['technical_state'],
            'scientific_classification': manifest['scientific_classification'],
            'attempt_id': latest['attempt_id'] if latest else None,
            'cases': list(cases.values()), 'resources': telemetry,
            'resumable': bool(latest and latest.get('checkpoint') and latest['state'] in {'interrupted', 'cancelled', 'failed'})}


def human_status(value):
    lines = [f"{value['run_id']}  {value['technical_state']}  science={value['scientific_classification']}"]
    for row in value['cases']:
        total, step = row.get('total_steps'), row.get('step', 0)
        progress = f'{step}/{total} ({100*step/total:.1f}%)' if total else str(step)
        rate = row.get('steps_per_second')
        eta = f' ETA {(total-step)/rate:.0f}s' if total and rate and step < total else ''
        checkpoint = ''
        if row.get('checkpoint_at'):
            stamp = datetime.fromisoformat(row['checkpoint_at'].replace('Z', '+00:00'))
            checkpoint = f' checkpoint age={(datetime.now(stamp.tzinfo)-stamp).total_seconds():.0f}s'
        lines.append(f"  {row['label']}: {row['state']} {progress}{eta}{checkpoint}")
    resources = value['resources']
    if resources:
        lines.append(f"  RSS peak={resources.get('peak_rss_bytes', 0)/1048576:.0f} MiB; output={resources.get('output_bytes', 0)/1048576:.0f} MiB; CPU={resources.get('cpu_seconds', 0):.1f}s")
        if resources.get('process_metrics_available') is False:
            lines.append('  Process CPU/RSS unavailable on this host; displayed zeros are not measurements.')
    return '\n'.join(lines)
