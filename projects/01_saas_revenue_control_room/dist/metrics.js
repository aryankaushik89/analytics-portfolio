(function (scope) {
  const movements = ['new_mrr', 'reactivation_mrr', 'expansion_mrr', 'contraction_mrr', 'churn_mrr', 'fx_mrr'];

  function filterRows(rows, selection, matchMonth = true) {
    return rows.filter(row => (!matchMonth || row.month === selection.month)
      && (selection.region === 'All' || row.region === selection.region)
      && (selection.channel === 'All' || row.channel === selection.channel));
  }

  function summarize(rows) {
    const keys = ['opening_mrr', 'closing_mrr', ...movements, 'retained_cohort_mrr', 'gross_retained_mrr'];
    const totals = Object.fromEntries(keys.map(key => [key, rows.reduce((sum, row) => sum + row[key], 0)]));
    totals.arr = totals.closing_mrr * 12;
    totals.nrr = totals.opening_mrr > 0 ? totals.retained_cohort_mrr / totals.opening_mrr : null;
    totals.grr = totals.opening_mrr > 0 ? totals.gross_retained_mrr / totals.opening_mrr : null;
    totals.active = rows.filter(row => row.closing_mrr > 0).length;
    totals.change = totals.opening_mrr > 0 ? totals.closing_mrr / totals.opening_mrr - 1 : null;
    totals.difference = totals.closing_mrr - totals.opening_mrr - movements.reduce((sum, key) => sum + totals[key], 0);
    return totals;
  }

  function billingTotals(rows) {
    return {billed: rows.reduce((sum, row) => sum + row.net_billed_cad, 0),
      cash: rows.reduce((sum, row) => sum + row.net_cash_cad, 0),
      outstanding: rows.reduce((sum, row) => sum + row.outstanding_cad, 0),
      unpaid: rows.filter(row => row.outstanding_cad > .005).length};
  }

  scope.RevenueMath = {filterRows, summarize, billingTotals, movements};
})(typeof window === 'undefined' ? globalThis : window);
