"""Run the documented SQL and export the actual results used by the dashboard."""

from pathlib import Path
import json
import sqlite3
import numpy as np
import pandas as pd
from generate_data import make_data

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / 'outputs'
DIST = ROOT / 'dist'
MOVEMENTS = ['new_mrr', 'reactivation_mrr', 'expansion_mrr', 'contraction_mrr', 'churn_mrr', 'fx_mrr']


def run_sql():
    OUTPUT.mkdir(exist_ok=True)
    database = sqlite3.connect(OUTPUT / 'revenue.sqlite')
    for csv in sorted((ROOT / 'data').glob('*.csv')):
        pd.read_csv(csv).to_sql(csv.stem, database, if_exists='replace', index=False)
    for name in ['clean_events', 'monthly_subscriptions', 'customer_month_metrics', 'invoice_ledger']:
        database.execute(f'DROP TABLE IF EXISTS {name}')
    for query in sorted((ROOT / 'sql').glob('*.sql')):
        database.executescript(query.read_text())
    metrics = pd.read_sql_query('SELECT * FROM customer_month_metrics ORDER BY month, customer_id', database)
    invoices = pd.read_sql_query('SELECT * FROM invoice_ledger ORDER BY invoice_date, invoice_id', database)
    database.close()
    return metrics, invoices


def monthly_summary(metrics):
    summary = metrics.groupby('month')[['opening_mrr', 'closing_mrr', *MOVEMENTS,
                                        'retained_cohort_mrr', 'gross_retained_mrr']].sum().reset_index()
    denominator = summary['opening_mrr'].replace(0, np.nan)
    summary['nrr'] = summary['retained_cohort_mrr'] / denominator
    summary['grr'] = summary['gross_retained_mrr'] / denominator
    summary['arr'] = summary['closing_mrr'] * 12
    summary['bridge_difference'] = summary['closing_mrr'] - summary['opening_mrr'] - summary[MOVEMENTS].sum(axis=1)
    return summary


def cohort_summary(metrics):
    paid = metrics[metrics['local_mrr'] > 0]
    first = paid.groupby('customer_id')['month'].min().rename('cohort')
    joined = metrics.merge(first, on='customer_id')
    joined = joined[joined['month'] >= joined['cohort']].copy()
    joined['active'] = joined['local_mrr'] > 0
    cohort = joined.groupby(['cohort', 'month']).agg(active=('active', 'sum'), customers=('customer_id', 'nunique')).reset_index()
    cohort['logo_retention'] = cohort['active'] / cohort['customers']
    return cohort


def data_checks(metrics, invoices):
    raw_events = pd.read_csv(ROOT / 'data/subscription_events_raw.csv')
    raw_invoices = pd.read_csv(ROOT / 'data/invoices_raw.csv')
    cases = [
        ('One customer per month', int(metrics.duplicated(['customer_id', 'month']).sum()) == 0),
        ('Every customer movement reconciles', bool((metrics['bridge_difference'].abs() < .000001).all())),
        ('Every monthly bridge reconciles', bool((monthly_summary(metrics)['bridge_difference'].abs() < .000001).all())),
        ('Invoice cash and balance reconcile', bool(np.allclose(invoices['net_billed_cad'], invoices['net_cash_cad'] + invoices['outstanding_cad']))),
        ('Outstanding balances are nonnegative', bool((invoices['outstanding_cad'] >= -.000001).all())),
        ('Three repeated event deliveries found', int(raw_events.duplicated('event_id').sum()) == 3),
        ('Two repeated invoice rows removed', len(raw_invoices) - len(invoices) == 2),
        ('Free accounts have no recurring revenue', bool((metrics.loc[metrics['customer_id'] == 'C0003', 'local_mrr'] == 0).all()))
    ]
    return pd.DataFrame(cases, columns=['check', 'passed'])


def export_dashboard(metrics, invoices, checks):
    columns = ['month', 'customer_id', 'company', 'region', 'channel', 'currency', 'billing_interval',
               'status', 'local_mrr', 'prior_local_mrr', 'cad_rate', 'prior_fx', 'opening_mrr', 'closing_mrr',
               *MOVEMENTS, 'retained_cohort_mrr', 'gross_retained_mrr']
    payload = {'months': sorted(metrics['month'].unique())[1:],
               'rows': json.loads(metrics[columns].to_json(orient='records', double_precision=8)),
               'invoices': json.loads(invoices.to_json(orient='records', double_precision=8)),
               'checks': checks.to_dict('records'), 'as_of': '2026-09-30',
               'source': 'Synthetic data generated with seed 89. No employer or customer records.'}
    DIST.mkdir(exist_ok=True)
    (DIST / 'data.js').write_text('window.REVENUE_DATA = ' + json.dumps(payload, separators=(',', ':')) + ';\n')
    (OUTPUT / 'dashboard_data.json').write_text(json.dumps(payload, separators=(',', ':')))


def write_findings(summary, invoices, checks):
    last = summary.iloc[-1]
    ledger = invoices[invoices['month'] == last['month']]
    text = f'''# What I found

All figures below come from the synthetic demonstration business. They do not describe a real company.

For {last['month']}, closing MRR is CAD {last['closing_mrr']:,.2f}, compared with CAD {last['opening_mrr']:,.2f} at the opening. Annualized recurring revenue is CAD {last['arr']:,.2f}.

The movement is explained by new subscriptions of CAD {last['new_mrr']:,.2f}, expansion of CAD {last['expansion_mrr']:,.2f}, reactivation of CAD {last['reactivation_mrr']:,.2f}, contraction of CAD {last['contraction_mrr']:,.2f}, churn of CAD {last['churn_mrr']:,.2f} and an FX movement of CAD {last['fx_mrr']:,.2f}. The reconciliation difference is CAD {last['bridge_difference']:.8f}.

Constant currency net revenue retention is {last['nrr']:.1%}. Gross revenue retention is {last['grr']:.1%}. These compare the opening paid customer cohort with its closing value and exclude new and reactivated customers. GRR caps each customer's retained amount at their opening value.

Net invoices issued this month total CAD {ledger['net_billed_cad'].sum():,.2f}. Net cash associated with those invoices is CAD {ledger['net_cash_cad'].sum():,.2f}, leaving CAD {ledger['outstanding_cad'].sum():,.2f} outstanding in that invoice cohort. This is not total accounts receivable across all previous periods.

## What I would check next

I would review churn and contraction alongside acquisition before increasing the marketing budget. A larger customer base can hide weaker retention. The channel filter lets me compare those movements without changing the underlying customer cohort definitions.

I would also separate billing and collections from recurring revenue. Annual invoices and midmonth changes make the figures different even when the subscription calculation is correct. The Midmonth Upgrade account ends September at CAD 200 MRR but is billed CAD 153.33 under the stated proration rule.

## Limits

The data generation intentionally makes paid search churn more common in later months. That pattern demonstrates an analytical workflow, not evidence about marketing channels in real businesses. Every customer has one subscription, channels and regions stay fixed, changes normally happen at month boundaries and payment, credit and refund records settle within the invoice month. Taxes, usage charges, delayed settlements and recognized revenue are outside this model. FX rates are simulated. Results are descriptive and do not establish campaign causality.

The {len(checks)} visible data checks passed. Separate automated tests exercise edge cases and segment reconciliations.
'''
    (ROOT / 'docs').mkdir(exist_ok=True)
    (ROOT / 'docs/findings.md').write_text(text)


def main():
    make_data()
    metrics, invoices = run_sql()
    summary = monthly_summary(metrics)
    checks = data_checks(metrics, invoices)
    metrics.to_csv(OUTPUT / 'customer_month_metrics.csv', index=False)
    invoices.to_csv(OUTPUT / 'invoice_ledger.csv', index=False)
    summary.to_csv(OUTPUT / 'monthly_summary.csv', index=False)
    cohort_summary(metrics).to_csv(OUTPUT / 'cohort_retention.csv', index=False)
    checks.to_csv(OUTPUT / 'data_checks.csv', index=False)
    if not checks['passed'].all():
        raise ValueError('A data check failed. See outputs/data_checks.csv.')
    export_dashboard(metrics, invoices, checks)
    write_findings(summary, invoices, checks)
    print(summary.tail(3).round(3).to_string(index=False))
    print(f'\n{len(checks)} data checks passed. Dashboard data exported.')


if __name__ == '__main__':
    main()
