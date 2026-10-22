import {selectRows, summarize, economics, decide, sampleSize, csvText} from './metrics.mjs';

let data;
const $ = id => document.getElementById(id);
const number = value => new Intl.NumberFormat('en-CA').format(value);
const percent = value => value === null ? '—' : (value * 100).toFixed(2) + '%';
const pp = value => value === null ? '—' : (value >= 0 ? '+' : '') + (value * 100).toFixed(2) + ' pp';
const money = value => value === null ? '—' : new Intl.NumberFormat('en-CA', {
  style: 'currency', currency: 'CAD', maximumFractionDigits: 0}).format(value);
const pValue = value => value < 0.000001 ? '< 0.000001' : value.toFixed(4);

function filters() {
  return {experiment: $('experiment').value, split: $('split').value,
    customer_type: $('customer').value, device: $('device').value};
}

function assumptions() {
  const cost = $('cost').valueAsNumber;
  const contribution = $('contribution').valueAsNumber;
  const valid = Number.isFinite(cost) && cost >= 0 && cost <= 20 &&
    Number.isFinite(contribution) && contribution >= 0 && contribution <= 1000;
  return {cost, contribution, valid};
}

function activeResult() {
  const selected = filters();
  const rows = selectRows(data, selected);
  const result = summarize(rows);
  const quality = data.quality.find(r => r.experiment_id === selected.experiment);
  const inputs = assumptions();
  const blocked = quality.blocked || (result.srm_p !== null && result.srm_p < 0.001);
  const verdict = inputs.valid ? decide(result, quality, selected.split, inputs.cost, inputs.contribution) : 'Check the cost inputs';
  const exploratory = selected.device !== 'All' || (selected.customer_type !== 'All' &&
    selected.customer_type !== data.selected_groups[selected.experiment]);
  return {selected, result, quality, inputs, blocked, verdict, exploratory};
}

function intervalSvg(result) {
  const minimum = Math.min(-0.01, result.lower - 0.004);
  const maximum = Math.max(0.01, result.upper + 0.004);
  const x = value => 38 + (value - minimum) / (maximum - minimum) * 422;
  const labels = [minimum, 0, maximum];
  return `<svg viewBox="0 0 500 100" role="img" aria-label="95% conversion effect interval ${pp(result.lower)} to ${pp(result.upper)}">
    <line x1="38" x2="460" y1="45" y2="45" stroke="#d5ddcf"/>
    <line x1="${x(0)}" x2="${x(0)}" y1="18" y2="65" stroke="#8c9986" stroke-dasharray="3 3"/>
    <line x1="${x(result.lower)}" x2="${x(result.upper)}" y1="41" y2="41" stroke="#477454" stroke-width="4"/>
    <circle cx="${x(result.effect)}" cy="41" r="6" fill="#315e48"/>
    ${labels.map(v => `<text x="${x(v)}" y="85" text-anchor="middle" font-family="Arial" font-size="11" fill="#69775e">${(v * 100).toFixed(1)} pp</text>`).join('')}
  </svg>`;
}

function renderDecision() {
  const {selected, result, quality, inputs, blocked, verdict, exploratory} = activeResult();
  const total = result.n_t + result.n_c;
  const config = data.metadata.experiments.find(r => r.experiment_id === selected.experiment);
  $('scope').textContent = `${config.name} · ${selected.split} · ${selected.customer_type} customers · ${selected.device} devices · ${number(total)} assigned users. ${selected.split === 'Evaluation' && selected.customer_type === 'All' && selected.device === 'All' ? 'Primary comparison.' : 'Exploratory view. The main result uses all evaluation users.'}`;
  $('verdict').className = 'verdict' + (blocked ? ' blocked' : verdict === 'Worth a follow-up rollout' ? '' : ' warn');
  const explanation = blocked ? 'The experiment fails its data checks. A filtered view cannot clear the full-experiment block. Fix the extract before using the effect.' :
    selected.split === 'Development' ? 'Use this split to choose a customer group. It is not the final result.' :
    !inputs.valid ? 'Enter cost from 0 to 20 and contribution from 0 to 1,000 CAD.' :
    exploratory ? 'This is an exploratory slice with an unadjusted interval. Use it to propose another test; the main decision uses all evaluation users.' :
    'This compares a fixed conversion-effect interval with the current cost assumptions. All campaign data is synthetic.';
  $('verdict').innerHTML = `<h2>${verdict}</h2><p>${explanation}</p>`;
  $('users').textContent = number(total);
  $('split-counts').textContent = `${number(result.n_t)} treatment / ${number(result.n_c)} control`;
  $('lift').textContent = blocked ? 'Withheld' : pp(result.effect);
  $('lift-range').textContent = blocked ? 'Resolve data quality first' : `95% interval ${pp(result.lower)} to ${pp(result.upper)}`;
  $('incremental').textContent = blocked ? '—' : (result.effect * 1000).toFixed(1);
  const net = economics(result, inputs.cost, inputs.contribution);
  $('net').textContent = blocked || !inputs.valid ? '—' : money(net.point);
  $('net-range').textContent = blocked || !inputs.valid ? 'No cost recommendation' : `95% interval ${money(net.lower)} to ${money(net.upper)}`;
  renderRates(result, blocked);
  $('break-even').textContent = !inputs.valid ? 'Check the inputs above.' : inputs.contribution === 0 ? 'At zero contribution, extra conversions cannot cover a positive cost.' :
    `Break-even lift at these inputs: ${(100 * inputs.cost / inputs.contribution).toFixed(2)} percentage points.`;
  $('cost-message').textContent = 'Per 1,000 assigned treatment users, not per 1,000 ad impressions or total randomized users. The interval holds cost and contribution fixed.';
  $('quality-content').innerHTML = `<p class="${quality.blocked ? 'fail' : 'pass'}">Full experiment SRM p ${pValue(quality.srm_p)} · ${quality.blocked ? 'Blocked' : 'No SRM flag'}</p><p>Current selection SRM p ${pValue(result.srm_p)}. Planned treatment share 50%.</p><p>${quality.missing_assignment_event_users} conversion users without an assignment record. All retained assignments have 7 complete days.</p>`;
  $('counts-table').innerHTML = `<table><thead><tr><th>Assigned group</th><th>Users</th><th>Converted users</th><th>Conversion rate</th></tr></thead><tbody>${[['Control', result.n_c, result.y_c], ['Treatment', result.n_t, result.y_t]].map(([arm, n, y]) => `<tr><td>${arm}</td><td>${number(n)}</td><td>${blocked ? 'Withheld' : number(y)}</td><td>${blocked ? 'Withheld' : percent(y / n)}</td></tr>`).join('')}</tbody></table>`;
}

function renderRates(result, blocked) {
  if (blocked) {
    $('rate-chart').innerHTML = '<p class="empty">Conversion comparison withheld until the extract is fixed.</p>';
    $('interval-chart').innerHTML = '';
    return;
  }
  const maximum = Math.max(result.y_t / result.n_t, result.y_c / result.n_c) * 1.25;
  $('rate-chart').innerHTML = [['Control', result.y_c / result.n_c], ['Treatment', result.y_t / result.n_t]].map(([label, rate]) =>
    `<div class="rate-row"><span>${label}</span><div class="bar-track"><div class="bar ${label === 'Treatment' ? 'treatment' : ''}" style="width:${rate / maximum * 100}%"></div></div><strong>${percent(rate)}</strong></div>`).join('') + `<div class="chart-scale">Shared scale 0 to ${percent(maximum)}</div>`;
  $('interval-chart').innerHTML = intervalSvg(result);
}

function renderGroups() {
  const {selected, quality} = activeResult();
  const chosen = data.selected_groups[selected.experiment];
  $('group-rule').textContent = `Development chose ${chosen.toLowerCase()} customers using the larger lower confidence bound, before evaluation outcomes were used. The overall evaluation result remains primary.`;
  const rows = ['New', 'Returning'].map(group => {
    const result = summarize(selectRows(data, {...selected, customer_type: group}));
    const blocked = quality.blocked || result.srm_p < 0.001;
    return `<tr><td>${group}${group === chosen ? ' · development choice' : ''}</td><td>${number(result.n_t + result.n_c)}</td><td>${blocked ? 'Withheld' : pp(result.effect)}</td><td>${blocked ? 'Withheld' : pp(result.lower) + ' to ' + pp(result.upper)}</td><td>${selected.split === 'Evaluation' && selected.device === 'All' && group === chosen ? 'Fixed group check' : 'Exploratory'}</td></tr>`;
  });
  $('group-table').innerHTML = `<table><thead><tr><th>Customer group</th><th>Users</th><th>Conversion lift</th><th>95% interval</th><th>Interpretation</th></tr></thead><tbody>${rows.join('')}</tbody></table>`;
}

function shownExamples() {
  const f = filters();
  const query = $('search').value.trim().toLowerCase();
  return data.examples.filter(r => r.experiment_id === f.experiment && r.split === f.split &&
    (f.customer_type === 'All' || r.customer_type === f.customer_type) &&
    (f.device === 'All' || r.device === f.device) && r.user_id.toLowerCase().includes(query));
}

function renderRecords() {
  const rows = shownExamples();
  $('example-count').textContent = `${rows.length} example records match these filters.`;
  $('export-records').disabled = rows.length === 0;
  if (!rows.length) {
    $('records-table').innerHTML = '<p class="empty">No example users match. Try clearing the search or widening a filter.</p>';
    return;
  }
  $('records-table').innerHTML = `<table><thead><tr><th>User</th><th>Group</th><th>Customer</th><th>Device</th><th>Exposed</th><th>Converted</th></tr></thead><tbody>${rows.map(r => `<tr><td><button class="record-link" data-user="${r.user_id}">${r.user_id}</button></td><td>${r.arm}</td><td>${r.customer_type}</td><td>${r.device}</td><td>${r.exposed ? 'Yes' : 'No'}</td><td>${r.converted ? 'Yes' : 'No'}</td></tr>`).join('')}</tbody></table>`;
  document.querySelectorAll('[data-user]').forEach(button => button.addEventListener('click', () => showUser(button.dataset.user)));
}

function showUser(id) {
  const user = data.examples.find(r => r.user_id === id);
  const events = data.events.filter(r => r.user_id === id);
  const start = new Date(user.assigned_at);
  const end = new Date(start.getTime() + 7 * 86400000);
  const quality = data.quality.find(r => r.experiment_id === user.experiment_id);
  $('detail-content').innerHTML = `<p><strong>${id}</strong><br>${user.arm} · ${user.customer_type} · ${user.device} · ${user.split}</p><p>Assigned ${start.toISOString()}. The window ends ${end.toISOString()} (exclusive).<br>${user.purchases_in_window} purchases in the window → converted = ${user.converted}. Ad exposure = ${user.exposed}.</p>${quality.blocked ? '<p class="fail">This example belongs to a blocked experiment. It is for tracing records only.</p>' : ''}<div class="table-wrap">${events.length ? `<table><thead><tr><th>Event</th><th>Event time (UTC)</th><th>In 7-day window?</th></tr></thead><tbody>${events.map(event => `<tr><td>${event.event_id}</td><td>${event.event_at}</td><td>${new Date(event.event_at) >= start && new Date(event.event_at) < end ? 'Yes' : 'No'}</td></tr>`).join('')}</tbody></table>` : '<p>No purchase events. The user still belongs in the denominator.</p>'}</div>`;
  $('detail').showModal();
}

function renderPlanning() {
  const baseline = $('baseline').valueAsNumber / 100;
  const effect = $('mde').valueAsNumber / 100;
  const size = sampleSize(baseline, effect);
  $('planning-result').textContent = size === null || !Number.isFinite(size) ?
    'Enter a positive baseline and increase that add to less than 100%.' : `${number(size)} users per arm · ${number(size * 2)} in total`;
}

function download(rows, filename) {
  const url = URL.createObjectURL(new Blob([csvText(rows)], {type: 'text/csv;charset=utf-8'}));
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function exportSummary() {
  const {selected, result, inputs, blocked, verdict, exploratory} = activeResult();
  const net = economics(result, inputs.cost, inputs.contribution);
  download([{...selected, synthetic: true, exploratory, n_t: result.n_t, n_c: result.n_c,
    y_t: blocked ? '' : result.y_t, y_c: blocked ? '' : result.y_c,
    effect: blocked ? '' : result.effect, ci_lower: blocked ? '' : result.lower,
    ci_upper: blocked ? '' : result.upper, cost: inputs.valid ? inputs.cost : '',
    contribution: inputs.valid ? inputs.contribution : '',
    net_per_1000: blocked || !inputs.valid ? '' : net.point, decision: verdict}], 'experiment_selection.csv');
}

function showView(name) {
  if (!['decision', 'groups', 'records', 'planning', 'notes'].includes(name)) name = 'decision';
  document.querySelectorAll('.view').forEach(section => { section.hidden = section.id !== name; });
  document.querySelectorAll('.tab').forEach(button => {
    button.classList.toggle('active', button.dataset.view === name);
    if (button.dataset.view === name) button.setAttribute('aria-current', 'page');
    else button.removeAttribute('aria-current');
  });
}

function render() { renderDecision(); renderGroups(); renderRecords(); }

async function start() {
  try {
    const response = await fetch('data.json');
    if (!response.ok) throw new Error('Could not load data.json.');
    data = await response.json();
    for (const id of ['experiment', 'split', 'customer', 'device']) $(id).addEventListener('change', render);
    for (const id of ['cost', 'contribution']) $(id).addEventListener('input', renderDecision);
    for (const id of ['baseline', 'mde']) $(id).addEventListener('input', renderPlanning);
    $('search').addEventListener('input', renderRecords);
    $('close-detail').addEventListener('click', () => $('detail').close());
    $('export-summary').addEventListener('click', exportSummary);
    $('export-records').addEventListener('click', () => download(shownExamples(), 'experiment_examples.csv'));
    $('reset').addEventListener('click', () => {
      $('experiment').value = 'retargeting'; $('split').value = 'Evaluation';
      $('customer').value = 'All'; $('device').value = 'All'; $('search').value = '';
      $('cost').value = '0.60'; $('contribution').value = '90'; render();
    });
    document.querySelectorAll('[data-view]').forEach(button => button.addEventListener('click', () => {
      showView(button.dataset.view);
      location.hash = button.dataset.view;
    }));
    window.addEventListener('hashchange', () => showView(location.hash.slice(1)));
    showView(location.hash.slice(1));
    render(); renderPlanning();
  } catch (error) {
    $('load-error').hidden = false;
    $('load-error').textContent = 'The experiment data could not load. Reload the page or serve the dist folder over HTTP.';
    $('scope').textContent = 'Results unavailable.';
    console.error(error);
  }
}

start();
