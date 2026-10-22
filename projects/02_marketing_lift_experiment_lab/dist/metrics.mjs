// Counts are user-level outcomes calculated in Python. No exposure-based filter.
export function wilson(y, n) {
  if (!n) return [null, null];
  const z = 1.959963984540054;
  const p = y / n;
  const denominator = 1 + z * z / n;
  const middle = (p + z * z / (2 * n)) / denominator;
  const half = z * Math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denominator;
  return [Math.max(0, middle - half), Math.min(1, middle + half)];
}

export function difference(nT, yT, nC, yC) {
  if (!nT || !nC) return [null, null, null];
  const pT = yT / nT;
  const pC = yC / nC;
  const [lT, uT] = wilson(yT, nT);
  const [lC, uC] = wilson(yC, nC);
  const effect = pT - pC;
  return [effect, Math.max(-1, effect - Math.hypot(pT - lT, uC - pC)),
    Math.min(1, effect + Math.hypot(uT - pT, pC - lC))];
}

// erfc approximation for the chi-square(1) survival probability.
export function srm(nT, nC) {
  if (!nT && !nC) return null;
  const x = Math.abs(nT - nC) / Math.sqrt(2 * (nT + nC));
  const t = 1 / (1 + 0.3275911 * x);
  return Math.min(1, Math.max(0, (((((1.061405429 * t - 1.453152027) * t) +
    1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-x * x)));
}

export function summarize(rows) {
  const sum = (arm, key) => rows.filter(r => r.arm === arm).reduce((a, r) => a + r[key], 0);
  const n_t = sum('Treatment', 'users');
  const n_c = sum('Control', 'users');
  const y_t = sum('Treatment', 'conversions');
  const y_c = sum('Control', 'conversions');
  const [effect, lower, upper] = difference(n_t, y_t, n_c, y_c);
  return {n_t, n_c, y_t, y_c, effect, lower, upper, srm_p: srm(n_t, n_c)};
}

export function selectRows(data, filters) {
  return data.counts.filter(r => r.experiment_id === filters.experiment && r.split === filters.split &&
    (filters.customer_type === 'All' || r.customer_type === filters.customer_type) &&
    (filters.device === 'All' || r.device === filters.device));
}

export function economics(result, cost, contribution) {
  if (result.effect === null) return {point: null, lower: null, upper: null};
  return {point: 1000 * (result.effect * contribution - cost),
    lower: 1000 * (result.lower * contribution - cost),
    upper: 1000 * (result.upper * contribution - cost)};
}

export function decide(result, quality, split, cost, contribution) {
  if (!result.n_t && !result.n_c) return 'No users';
  if (result.effect === null) return 'Insufficient data';
  if (quality.blocked || quality.srm_p === null || quality.srm_p < 0.001 || result.srm_p < 0.001) return 'Investigate data';
  if (split === 'Development') return 'Development only';
  const net = economics(result, cost, contribution);
  if (net.lower > 0) return 'Worth a follow-up rollout';
  if (net.upper < 0) return 'Does not cover assumed cost';
  return 'Inconclusive at this cost';
}

export function sampleSize(baseline, effect) {
  if (!(baseline > 0 && baseline < 1 && effect > 0 && baseline + effect < 1)) return null;
  const alternative = baseline + effect;
  const average = (baseline + alternative) / 2;
  const numerator = 1.959963984540054 * Math.sqrt(2 * average * (1 - average)) +
    0.8416212335729143 * Math.sqrt(baseline * (1 - baseline) + alternative * (1 - alternative));
  return Math.ceil((numerator / effect) ** 2);
}

export function csvText(rows) {
  if (!rows.length) return '';
  const keys = Object.keys(rows[0]);
  const quote = value => '"' + String(value ?? '').replaceAll('"', '""') + '"';
  return [keys.map(quote).join(','), ...rows.map(row => keys.map(k => quote(row[k])).join(','))].join('\r\n');
}
