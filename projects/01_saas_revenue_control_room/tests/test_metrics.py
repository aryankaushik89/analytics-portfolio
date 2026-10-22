from pathlib import Path
import sys
import unittest
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from analysis import monthly_summary


class RevenueChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = pd.read_csv(ROOT / 'outputs/customer_month_metrics.csv')
        cls.invoices = pd.read_csv(ROOT / 'outputs/invoice_ledger.csv')
        cls.latest = cls.rows[cls.rows['month'] == '2026-09']

    def test_customer_month_grain(self):
        self.assertFalse(self.rows.duplicated(['customer_id', 'month']).any())

    def test_every_month_reconciles(self):
        self.assertLess(self.rows['bridge_difference'].abs().max(), .000001)

    def test_segments_reconcile(self):
        for _, rows in self.rows.groupby(['region', 'channel']):
            self.assertLess(monthly_summary(rows)['bridge_difference'].abs().max(), .000001)

    def test_annual_subscription_is_divided_by_twelve(self):
        row = self.latest.set_index('customer_id').loc['C0001']
        self.assertEqual(row['unit_amount_minor'], 120000)
        self.assertEqual(row['local_mrr'], 100)

    def test_past_due_still_counts(self):
        row = self.latest.set_index('customer_id').loc['C0008']
        self.assertEqual(row['status'], 'past_due')
        self.assertEqual(row['local_mrr'], 100)

    def test_cancelled_account_churn(self):
        row = self.latest.set_index('customer_id').loc['C0007']
        self.assertEqual(row['closing_mrr'], 0)
        self.assertEqual(row['churn_mrr'], -100)

    def test_returning_customer_is_not_new_business(self):
        row = self.latest.set_index('customer_id').loc['C0006']
        self.assertEqual(row['reactivation_mrr'], 100)
        self.assertEqual(row['new_mrr'], 0)

    def test_new_annual_business_is_normalized(self):
        row = self.rows[(self.rows['month'] == '2026-02') & (self.rows['customer_id'] == 'C0005')].iloc[0]
        self.assertEqual(row['new_mrr'], 200)

    def test_fx_does_not_create_expansion(self):
        row = self.latest.set_index('customer_id').loc['C0002']
        self.assertEqual(row['expansion_mrr'], 0)
        self.assertNotEqual(row['fx_mrr'], 0)

    def test_free_workspace_is_excluded(self):
        self.assertTrue((self.rows.loc[self.rows['customer_id'] == 'C0003', 'closing_mrr'] == 0).all())

    def test_midmonth_bill_differs_from_run_rate(self):
        invoice = self.invoices[(self.invoices['customer_id'] == 'C0004') & (self.invoices['month'] == '2026-09')].iloc[0]
        self.assertEqual(invoice['gross_minor'], 15333)
        self.assertEqual(self.latest.set_index('customer_id').loc['C0004', 'local_mrr'], 200)

    def test_invoice_balance_identity(self):
        self.assertTrue(np.allclose(self.invoices['net_billed_cad'], self.invoices['net_cash_cad'] + self.invoices['outstanding_cad']))

    def test_nrr_uses_opening_customers(self):
        s = monthly_summary(self.latest).iloc[0]
        opening_customers = self.latest[self.latest['prior_local_mrr'] > 0]
        expected = (opening_customers['local_mrr'] * opening_customers['prior_fx']).sum() / opening_customers['opening_mrr'].sum()
        self.assertAlmostEqual(s['nrr'], expected)
        self.assertLessEqual(s['grr'], 1.0000001)

    def test_duplicate_invoices_are_removed(self):
        raw = pd.read_csv(ROOT / 'data/invoices_raw.csv')
        self.assertEqual(len(raw) - len(self.invoices), 2)
        self.assertFalse(self.invoices['invoice_id'].duplicated().any())


if __name__ == '__main__':
    unittest.main()
