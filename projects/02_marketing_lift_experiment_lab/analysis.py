"""User-level experiment analysis and the checked data used by the dashboard."""

from pathlib import Path
from itertools import product
import json
import math
import sqlite3
import numpy as np
import pandas as pd
from scipy.stats import chi2
from scipy.stats import norm

ROOT = Path(__file__).resolve().parent


def load_sources():
    raw = pd.read_csv(ROOT / 'data/assignments.csv.gz')
    events = pd.read_csv(ROOT / 'data/conversion_events.csv')
    metadata = json.loads((ROOT / 'data/scenario.json').read_text())
    return raw, events, metadata


def user_outcomes(raw, events, extract_at):
    users = raw.drop_duplicates('user_id').copy()
    purchases = events.drop_duplicates('event_id').copy()
    joined = purchases.merge(users[['user_id', 'experiment_id', 'assigned_at']],
                             on=['user_id', 'experiment_id'], validate='many_to_one')
    elapsed = pd.to_datetime(joined['event_at'], utc=True) - pd.to_datetime(joined['assigned_at'], utc=True)
    before_extract = pd.to_datetime(joined['event_at'], utc=True).le(pd.Timestamp(extract_at))
    valid = joined.loc[elapsed.ge(pd.Timedelta(0)) & elapsed.lt(pd.Timedelta(days=7)) & before_extract]
    counts = valid.groupby('user_id').size().rename('purchases_in_window')
    users = users.join(counts, on='user_id', validate='one_to_one')
    users['purchases_in_window'] = users['purchases_in_window'].fillna(0).astype(int)
    users['converted'] = users['purchases_in_window'].gt(0).astype(int)
    return users


def sql_outcomes(raw, events, extract_at):
    with sqlite3.connect(':memory:') as connection:
        raw.to_sql('assignments_raw', connection, index=False)
        events.to_sql('conversion_events_raw', connection, index=False)
        return pd.read_sql_query((ROOT / 'sql/user_outcomes.sql').read_text(),
                                 connection, params={'extract_at': extract_at})


def wilson_interval(successes, users, z=1.959963984540054):
    if users == 0:
        return None, None
    rate = successes / users
    denominator = 1 + z * z / users
    middle = (rate + z * z / (2 * users)) / denominator
    half = z * math.sqrt(rate * (1 - rate) / users + z * z / (4 * users * users)) / denominator
    return max(0, middle - half), min(1, middle + half)


def difference_interval(n_t, y_t, n_c, y_c):
    if min(n_t, n_c) == 0:
        return None, None, None
    p_t, p_c = y_t / n_t, y_c / n_c
    l_t, u_t = wilson_interval(y_t, n_t)
    l_c, u_c = wilson_interval(y_c, n_c)
    difference = p_t - p_c
    lower = difference - math.sqrt((p_t - l_t) ** 2 + (u_c - p_c) ** 2)
    upper = difference + math.sqrt((u_t - p_t) ** 2 + (p_c - l_c) ** 2)
    return difference, max(-1, lower), min(1, upper)


def sample_ratio(n_t, n_c, expected_share=0.5):
    total = n_t + n_c
    if total == 0:
        return None
    expected_t = total * expected_share
    expected_c = total * (1 - expected_share)
    statistic = (n_t - expected_t) ** 2 / expected_t + (n_c - expected_c) ** 2 / expected_c
    return float(chi2.sf(statistic, df=1))


def summarize(selection):
    n_t = int(selection['arm'].eq('Treatment').sum())
    n_c = int(selection['arm'].eq('Control').sum())
    y_t = int(selection.loc[selection['arm'].eq('Treatment'), 'converted'].sum())
    y_c = int(selection.loc[selection['arm'].eq('Control'), 'converted'].sum())
    effect, lower, upper = difference_interval(n_t, y_t, n_c, y_c)
    return {'n_t': n_t, 'n_c': n_c, 'y_t': y_t, 'y_c': y_c,
            'effect': effect, 'lower': lower, 'upper': upper, 'srm_p': sample_ratio(n_t, n_c)}


def economic_result(result, cost=0.6, contribution=90):
    if result['effect'] is None:
        return {'point': None, 'lower': None, 'upper': None}
    return {label: result[key] * contribution * 1000 - cost * 1000
            for label, key in [('point', 'effect'), ('lower', 'lower'), ('upper', 'upper')]}


def decision(result, global_srm_p, split='Evaluation', cost=0.6, contribution=90, blocked=False):
    if result['n_t'] + result['n_c'] == 0:
        return 'No users'
    if result['effect'] is None:
        return 'Insufficient data'
    if blocked or global_srm_p is None or global_srm_p < 0.001 or result['srm_p'] is None or result['srm_p'] < 0.001:
        return 'Investigate data'
    if split == 'Development':
        return 'Development only'
    net = economic_result(result, cost, contribution)
    if net['lower'] > 0:
        return 'Worth a follow-up rollout'
    if net['upper'] < 0:
        return 'Does not cover assumed cost'
    return 'Inconclusive at this cost'


def planned_sample_size(baseline, absolute_effect, power=0.8):
    if not 0 < baseline < 1 or not 0 < absolute_effect < 1 - baseline:
        return None
    alternative = baseline + absolute_effect
    average = (baseline + alternative) / 2
    numerator = norm.ppf(0.975) * math.sqrt(2 * average * (1 - average))
    numerator += norm.ppf(power) * math.sqrt(baseline * (1 - baseline) + alternative * (1 - alternative))
    return math.ceil((numerator / absolute_effect) ** 2)


def data_checks(raw, events, users, sql_users, extract_at):
    clean_events = events.drop_duplicates('event_id')
    mature = pd.to_datetime(users['assigned_at'], utc=True) + pd.Timedelta(days=7)
    comparisons = users.set_index('user_id')['converted'].sort_index().eq(
        sql_users.set_index('user_id')['converted'].sort_index())
    checks = [
        ('Unique user output', users['user_id'].is_unique),
        ('Assignment re-deliveries are identical', len(raw.drop_duplicates()) == raw['user_id'].nunique()),
        ('Event re-deliveries are identical', len(events.drop_duplicates()) == events['event_id'].nunique()),
        ('Every assignment has seven complete days', bool(mature.le(pd.Timestamp(extract_at)).all())),
        ('SQL and pandas have the same users', set(users['user_id']) == set(sql_users['user_id'])),
        ('SQL and pandas conversion flags agree', bool(comparisons.all())),
        ('SQL and pandas purchase counts agree', users.set_index('user_id')['purchases_in_window'].sort_index().equals(
            sql_users.set_index('user_id')['purchases_in_window'].sort_index())),
        ('Development and evaluation IDs are disjoint', set(users.loc[users['split'].eq('Development'), 'user_id']).isdisjoint(
            set(users.loc[users['split'].eq('Evaluation'), 'user_id']))),
        ('Conversions cannot exceed users', bool(users['converted'].between(0, 1).all())),
        ('No unknown experiment labels', set(clean_events['experiment_id']) == set(users['experiment_id']))
    ]
    return pd.DataFrame(checks, columns=['check', 'passed'])


def experiment_quality(raw, events, users):
    records = []
    for experiment, selection in users.groupby('experiment_id'):
        event_users = events.loc[events['experiment_id'].eq(experiment), 'user_id']
        orphan_users = int(event_users.loc[~event_users.isin(selection['user_id'])].nunique())
        result = summarize(selection)
        records.append({'experiment_id': experiment, 'assigned_users': len(selection),
                        'srm_p': result['srm_p'], 'missing_assignment_event_users': orphan_users,
                        'blocked': result['srm_p'] < 0.001 or orphan_users > 0})
    return records


def filtered(users, experiment, split, customer_type='All', device='All'):
    selection = users.loc[users['experiment_id'].eq(experiment) & users['split'].eq(split)]
    if customer_type != 'All':
        selection = selection.loc[selection['customer_type'].eq(customer_type)]
    if device != 'All':
        selection = selection.loc[selection['device'].eq(device)]
    return selection


def select_development_groups(users):
    selected = {}
    for experiment in users['experiment_id'].unique():
        candidates = []
        for group in ['New', 'Returning']:
            result = summarize(filtered(users, experiment, 'Development', group))
            candidates.append((result['lower'], group))
        selected[experiment] = max(candidates)[1]
    return selected


def selection_oracles(users, quality):
    rows = []
    lookup = {row['experiment_id']: row for row in quality}
    choices = product(users['experiment_id'].unique(), ['Evaluation', 'Development'],
                      ['All', 'New', 'Returning'], ['All', 'Desktop', 'Mobile'])
    for experiment, split, customer_type, device in choices:
        result = summarize(filtered(users, experiment, split, customer_type, device))
        q = lookup[experiment]
        rows.append({'experiment': experiment, 'split': split, 'customer_type': customer_type,
                     'device': device, **result, 'net': economic_result(result),
                     'decision': decision(result, q['srm_p'], split, blocked=q['blocked'])})
    return rows


def save_outputs(users, raw, events, metadata):
    sql_users = sql_outcomes(raw, events, metadata['extract_at'])
    checks = data_checks(raw, events, users, sql_users, metadata['extract_at'])
    quality = experiment_quality(raw, events, users)
    chosen = select_development_groups(users)
    aggregate = users.groupby(['experiment_id', 'split', 'customer_type', 'device', 'arm']).agg(
        users=('user_id', 'size'), conversions=('converted', 'sum'), exposed=('exposed', 'sum')).reset_index()
    oracles = selection_oracles(users, quality)
    for folder in ['outputs', 'dist']:
        (ROOT / folder).mkdir(exist_ok=True)
    aggregate.to_csv(ROOT / 'outputs/aggregate_counts.csv', index=False)
    checks.to_csv(ROOT / 'outputs/data_checks.csv', index=False)
    pd.DataFrame(quality).to_csv(ROOT / 'outputs/experiment_quality.csv', index=False)
    pd.DataFrame(oracles).drop(columns='net').to_csv(ROOT / 'outputs/filter_results.csv', index=False)
    examples = users.groupby(['experiment_id', 'split', 'customer_type', 'device', 'arm']).head(3)
    details = events.drop_duplicates('event_id').loc[events.drop_duplicates('event_id')['user_id'].isin(examples['user_id'])]
    payload = {'metadata': metadata, 'counts': aggregate.to_dict('records'), 'quality': quality,
               'selected_groups': chosen, 'examples': examples.to_dict('records'),
               'events': details.to_dict('records'), 'checks': checks.to_dict('records')}
    (ROOT / 'dist/data.json').write_text(json.dumps(payload, indent=1, allow_nan=False) + '\n')
    (ROOT / 'outputs/python_oracles.json').write_text(json.dumps(oracles, indent=1, allow_nan=False) + '\n')
    summary = {'selected_groups': chosen, 'quality': quality, 'checks_passed': bool(checks['passed'].all()),
               'raw_assignment_rows': len(raw), 'users': len(users), 'event_deliveries': len(events),
               'duplicate_assignments': int(raw.duplicated('user_id').sum()),
               'duplicate_events': int(events.duplicated('event_id').sum()),
               'evaluation_results': [r for r in oracles if r['split'] == 'Evaluation' and r['customer_type'] == 'All' and r['device'] == 'All']}
    (ROOT / 'outputs/summary.json').write_text(json.dumps(summary, indent=2, allow_nan=False) + '\n')
    (ROOT / 'outputs/development_selection.json').write_text(json.dumps({
        'rule': 'Choose the larger development lower confidence bound from New and Returning.',
        'selected_groups': chosen, 'evaluation_outcomes_used': False}, indent=2) + '\n')
    return checks, summary


if __name__ == '__main__':
    raw, events, metadata = load_sources()
    users = user_outcomes(raw, events, metadata['extract_at'])
    checks, summary = save_outputs(users, raw, events, metadata)
    print(checks.to_string(index=False))
    print(json.dumps(summary, indent=2))
    if not checks['passed'].all():
        raise ValueError('A structural data check failed. Review the check table before release.')
