"""Create reproducible fictional experiments. No outside records are used."""

from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
SEED = 89
EXTRACT_AT = '2026-03-01T00:00:00Z'
EXPERIMENTS = [
    {'experiment_id': 'retargeting', 'name': 'Retargeting campaign', 'users': 100000,
     'new_effect': 0.008, 'returning_effect': 0.032, 'drop_controls': 0.0,
     'note': 'Main synthetic experiment. Effects vary by customer type.'},
    {'experiment_id': 'small_test', 'name': 'Small campaign test', 'users': 5000,
     'new_effect': 0.002, 'returning_effect': 0.002, 'drop_controls': 0.0,
     'note': 'A smaller, weak-effect scenario. An uncertain result is useful too.'},
    {'experiment_id': 'missing_controls', 'name': 'Missing control records', 'users': 18000,
     'new_effect': 0.008, 'returning_effect': 0.032, 'drop_controls': 0.55,
     'note': 'Deliberately broken extract. Some assigned control users are missing.'}
]


def make_assignments(config, rng):
    n = config['users']
    return pd.DataFrame({
        'experiment_id': config['experiment_id'],
        'user_id': [f"{config['experiment_id']}_{i:06d}" for i in range(n)],
        'assigned_at': pd.Timestamp('2026-02-01', tz='UTC') + pd.to_timedelta(
            rng.integers(0, 20 * 86400, n), unit='s'),
        'arm': rng.choice(['Control', 'Treatment'], n),
        'customer_type': rng.choice(['New', 'Returning'], n, p=[0.6, 0.4]),
        'device': rng.choice(['Desktop', 'Mobile'], n, p=[0.35, 0.65]),
        'split': rng.choice(['Development', 'Evaluation'], n, p=[0.4, 0.6])
    })


def make_events(assignments, config, rng):
    n = len(assignments)
    treated = assignments['arm'].eq('Treatment').to_numpy()
    returning = assignments['customer_type'].eq('Returning').to_numpy()
    exposure = treated & (rng.random(n) < 0.78)
    base = np.where(returning, 0.11, 0.04)
    effect = np.where(returning, config['returning_effect'], config['new_effect'])
    converted = rng.random(n) < base + effect * exposure
    assignments['exposed'] = exposure.astype(int)
    events = assignments.loc[converted, ['experiment_id', 'user_id', 'assigned_at']].copy()
    events['event_at'] = events['assigned_at'] + pd.to_timedelta(
        rng.integers(3600, 7 * 86400, len(events)), unit='s')
    events['event_id'] = [f"{config['experiment_id']}_purchase_{i:06d}" for i in range(len(events))]
    events['event_type'] = 'purchase'
    return events.drop(columns='assigned_at')


def add_event_edge_cases(events, assignments):
    # Additional purchases count once per user. These records do not add users.
    repeated = events.head(60).copy()
    repeated['event_id'] += '_second'
    repeated['event_at'] += pd.Timedelta(minutes=1)
    outside = assignments.head(70)[['experiment_id', 'user_id', 'assigned_at']].copy()
    outside['event_at'] = outside['assigned_at'] + pd.Timedelta(days=9)
    outside['event_id'] = outside['user_id'] + '_late'
    outside['event_type'] = 'purchase'
    before = outside.head(12).copy()
    before['event_at'] = assignments.head(12)['assigned_at'].to_numpy() - pd.Timedelta(hours=2)
    before['event_id'] = before['user_id'] + '_before'
    outside = outside.drop(columns='assigned_at')
    before = before.drop(columns='assigned_at')
    return pd.concat([events, repeated, outside, before, events.head(35)], ignore_index=True)


def make_data():
    rng = np.random.default_rng(SEED)
    all_assignments = []
    all_events = []
    for config in EXPERIMENTS:
        assignments = make_assignments(config, rng)
        events = make_events(assignments, config, rng)
        events = add_event_edge_cases(events, assignments)
        keep = ~(assignments['arm'].eq('Control') & (rng.random(len(assignments)) < config['drop_controls']))
        assignments = assignments.loc[keep].copy()
        all_assignments.append(pd.concat([assignments, assignments.head(25)]))
        all_events.append(events)
    raw = pd.concat(all_assignments, ignore_index=True)
    events = pd.concat(all_events, ignore_index=True)
    raw['assigned_at'] = raw['assigned_at'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    events['event_at'] = pd.to_datetime(events['event_at'], utc=True).dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    (ROOT / 'data').mkdir(exist_ok=True)
    raw.to_csv(ROOT / 'data/assignments.csv.gz', index=False, compression={'method': 'gzip', 'mtime': 0})
    events.to_csv(ROOT / 'data/conversion_events.csv', index=False)
    metadata = {'seed': SEED, 'synthetic': True, 'extract_at': EXTRACT_AT,
                'window_days': 7, 'planned_treatment_share': 0.5, 'srm_alpha': 0.001,
                'default_cost': 0.6, 'default_contribution': 90,
                'currency': 'CAD', 'experiments': EXPERIMENTS}
    (ROOT / 'data/scenario.json').write_text(json.dumps(metadata, indent=2) + '\n')
    print(f'Generated {len(raw):,} raw assignment rows and {len(events):,} event deliveries.')


if __name__ == '__main__':
    make_data()
