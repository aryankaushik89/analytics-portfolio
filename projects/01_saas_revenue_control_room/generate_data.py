"""Create a small subscription business with records we can trace and check."""

from pathlib import Path
import calendar
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
MONTHS = pd.date_range('2024-12-01', '2026-09-01', freq='MS')


def make_data():
    DATA.mkdir(exist_ok=True)
    rng = np.random.default_rng(89)
    customers = []
    events = []
    invoices = []
    payments = []
    credits = []
    refunds = []
    event_number = 0

    # The first eight accounts cover cases that are easy to check by hand.
    names = ['Maple Annual', 'Harbour USD', 'Free Workspace', 'Midmonth Upgrade',
             'Annual New Business', 'Returning Account', 'Cancelled Account', 'Past Due Account']

    for number in range(1, 361):
        customer = f'C{number:04d}'
        region = str(rng.choice(['Canada', 'United States', 'Europe'], p=[.6, .3, .1]))
        currency = 'CAD' if region == 'Canada' else 'USD'
        channel = str(rng.choice(['Organic', 'Paid search', 'Partner', 'Outbound'], p=[.4, .3, .2, .1]))
        start = 0 if number <= 130 else int(rng.integers(1, len(MONTHS)))
        interval = 'year' if rng.random() < .22 else 'month'
        rate = int(rng.choice([49, 149, 499])) * 100
        rate = int(rate * .85) if interval == 'year' else rate
        if number <= 8:
            region, currency, channel, interval, rate, start = 'Canada', 'CAD', 'Organic', 'month', 10000, 0
        if number == 1:
            interval = 'year'
        if number == 2:
            region, currency = 'United States', 'USD'
        if number == 3:
            rate = 0
        if number == 5:
            interval, rate, start = 'year', 20000, 14

        customers.append({'customer_id': customer, 'company': names[number - 1] if number <= 8 else f'Demo company {number:03d}',
                          'region': region, 'channel': channel, 'currency': currency,
                          'signup_date': MONTHS[start].date().isoformat()})
        current = 0
        status = 'cancelled'
        previous_state = None

        for month_index, month in enumerate(MONTHS):
            if month_index < start:
                continue
            opening = current
            renewal = (month_index - start) % 12 == 0
            can_change = interval == 'month' or renewal
            if month_index == start:
                current, status = rate, 'active'
            elif number > 8 and can_change:
                chance = rng.random()
                if current > 0:
                    if chance < (.075 if month_index >= 16 and channel == 'Paid search' else .03):
                        current, status = 0, 'cancelled'
                    elif chance < .12:
                        current = int(round(current * 1.3))
                        status = 'active'
                    elif chance < .16:
                        current = max(1000, int(round(current * .8)))
                        status = 'active'
                    else:
                        status = 'past_due' if rng.random() < .04 else 'active'
                elif chance < .10:
                    current, status = rate, 'active'

            if number == 4 and month_index == 21:
                current = 20000
            if number == 6:
                current = 0 if month_index == 20 else 10000
                status = 'cancelled' if current == 0 else 'active'
            if number == 7 and month_index == 21:
                current, status = 0, 'cancelled'
            if number == 8 and month_index == 21:
                status = 'past_due'

            unit_amount = current * (12 if interval == 'year' else 1)
            state = (unit_amount, interval, status)
            if state != previous_state:
                event_number += 1
                day = 15 if number == 4 and month_index == 21 else 1
                event_date = month.replace(day=day).isoformat()
                events.append({'event_id': f'E{event_number:05d}', 'customer_id': customer,
                               'effective_at': event_date, 'received_at': event_date,
                               'unit_amount_minor': unit_amount, 'quantity': 1,
                               'billing_interval': interval, 'status': status})
                previous_state = state

            # Monthly billing follows the month's contract; annual changes occur at renewal.
            should_bill = current > 0 and (interval == 'month' or renewal or opening == 0)
            if month_index == 0 or not should_bill:
                continue
            gross = current * (12 if interval == 'year' else 1)
            if number == 4 and month_index == 21:
                days = calendar.monthrange(month.year, month.month)[1]
                gross = round(opening + (current - opening) * (days - 14) / days)
            invoice_id = f'I{len(invoices) + 1:05d}'
            invoice_date = month.date().isoformat()
            credit = round(gross * .1) if rng.random() < .025 and number > 8 else 0
            net_due = gross - credit
            collection = 0 if status == 'past_due' else (net_due if rng.random() > .05 else round(net_due * .5))
            refund = credit if credit and collection == net_due and rng.random() < .5 else 0
            invoices.append({'invoice_id': invoice_id, 'customer_id': customer, 'invoice_date': invoice_date,
                             'currency': currency, 'gross_minor': gross, 'billing_interval': interval,
                             'service_months': 12 if interval == 'year' else 1})
            if credit:
                credits.append({'credit_id': f'CN{len(credits) + 1:05d}', 'invoice_id': invoice_id, 'amount_minor': credit})
            if collection:
                payments.append({'payment_id': f'P{len(payments) + 1:05d}', 'invoice_id': invoice_id,
                                 'amount_minor': collection + refund})
            if refund:
                refunds.append({'refund_id': f'R{len(refunds) + 1:05d}', 'invoice_id': invoice_id, 'amount_minor': refund})

    # Duplicate delivery records are deliberate. SQL removes these before aggregation.
    events.extend([dict(row, received_at=row['received_at'][:10] + 'T01:00:00') for row in events[8:11]])
    invoices.extend([dict(row) for row in invoices[12:14]])
    fx = []
    periods = []
    for index, month in enumerate(MONTHS):
        periods.append({'month': month.strftime('%Y-%m'), 'month_end': (month + pd.offsets.MonthEnd(0)).date().isoformat()})
        fx.append({'month': month.strftime('%Y-%m'), 'currency': 'CAD', 'cad_rate': 1.0})
        fx.append({'month': month.strftime('%Y-%m'), 'currency': 'USD', 'cad_rate': round(1.35 + .025 * np.sin(index / 3), 6)})

    tables = {'customers': customers, 'subscription_events_raw': events, 'invoices_raw': invoices,
              'payments': payments, 'credit_notes': credits, 'refunds': refunds, 'fx_rates': fx, 'months': periods}
    for name, records in tables.items():
        pd.DataFrame(records).to_csv(DATA / f'{name}.csv', index=False)
    return tables


if __name__ == '__main__':
    result = make_data()
    print({name: len(rows) for name, rows in result.items()})
