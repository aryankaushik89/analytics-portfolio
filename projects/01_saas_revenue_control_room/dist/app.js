const data = window.REVENUE_DATA;
const math = window.RevenueMath;
const state = {month: data.months.at(-1), region: 'All', channel: 'All', tab: 'overview', search: '', page: 1};
const money = value => new Intl.NumberFormat('en-CA', {style: 'currency', currency: 'CAD', maximumFractionDigits: 0}).format(value);
const preciseMoney = value => new Intl.NumberFormat('en-CA', {style: 'currency', currency: 'CAD'}).format(Math.abs(value)<.005?0:value);
const percent = value => value === null ? '—' : (value * 100).toFixed(1) + '%';
const monthName = value => new Date(value + '-01T12:00:00').toLocaleDateString('en-CA', {month: 'long', year: 'numeric'});
const escapeHtml = value => String(value).replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const selectedRows = () => math.filterRows(data.rows, state);
const selectedInvoices = () => math.filterRows(data.invoices, state);

function metric(label, value, detail, icon = '↗') {
  return `<article class="metric"><div class="metric-label">${label}<span class="metric-icon" aria-hidden="true">${icon}</span></div><div class="metric-number">${value}</div><small>${detail}</small></article>`;
}

function lineChart(rows, compact = false) {
  const months = [...new Set(rows.map(row => row.month))].filter(month => month <= state.month).slice(-12);
  const values = months.map(month => math.summarize(rows.filter(row => row.month === month)).closing_mrr);
  if (!values.length) return '<p class="empty">No records for this selection.</p>';
  const width = 650, height = compact ? 180 : 245, left = 55, right = 15, top = 20, bottom = 35;
  const maximum = Math.max(...values, 1) * 1.15;
  const x = i => left + i * (width - left - right) / Math.max(1, values.length - 1);
  const y = value => height - bottom - value / maximum * (height - top - bottom);
  const points = values.map((value, i) => `${x(i)},${y(value)}`).join(' ');
  const fill = `${x(0)},${height-bottom} ${points} ${x(values.length-1)},${height-bottom}`;
  let grid = '';
  for (let i = 0; i <= 4; i++) {
    const value = maximum * i / 4;
    grid += `<line x1="${left}" x2="${width-right}" y1="${y(value)}" y2="${y(value)}" stroke="#eef1e7"/><text x="${left-9}" y="${y(value)+3}" text-anchor="end">${value >= 1000 ? '$'+Math.round(value/1000)+'k' : '$'+Math.round(value)}</text>`;
  }
  const labels = months.map((month, i) => `<text x="${x(i)}" y="${height-12}" text-anchor="middle">${new Date(month+'-01T12:00:00').toLocaleDateString('en',{month:'short'})}${month.endsWith('-01')?' '+month.slice(2,4):''}</text>`).join('');
  const dots = values.map((value, i) => `<circle cx="${x(i)}" cy="${y(value)}" r="4" fill="#fff" stroke="#527455" stroke-width="2"><title>${monthName(months[i])}: ${preciseMoney(value)} CAD</title></circle>`).join('');
  return `<svg class="trend" viewBox="0 0 ${width} ${height}" role="img" aria-label="Monthly recurring revenue for the selected region and channel"><defs><linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#d9e5d0" stop-opacity=".8"/><stop offset="100%" stop-color="#f7f9f2" stop-opacity=".1"/></linearGradient></defs>${grid}<polygon points="${fill}" fill="url(#area)"/><polyline class="line" points="${points}"/>${dots}${labels}</svg>`;
}

function movementPanel(totals) {
  const labels = ['New business', 'Reactivation', 'Expansion', 'Contraction', 'Churn', 'Currency effect'];
  const max = Math.max(...math.movements.map(key => Math.abs(totals[key])), 1);
  const bars = math.movements.map((key, i) => `<div class="move-row"><span>${labels[i]}</span><div class="track"><div class="fill ${totals[key]<0?'negative':''} ${key==='fx_mrr'?'fx':''}" style="width:${Math.abs(totals[key])/max*100}%"></div></div><span class="amount">${totals[key]>0?'+':''}${preciseMoney(totals[key])}</span></div>`).join('');
  return `<article class="panel"><div class="panel-title"><div><h2>What moved MRR?</h2><p>Changes from the opening balance, including FX</p></div><span class="pill">${money(totals.opening_mrr)} → ${money(totals.closing_mrr)}</span></div>${bars}<div class="reconciliation"><span>Unexplained difference</span><strong class="${Math.abs(totals.difference)<.01?'pass':''}">${preciseMoney(totals.difference)} ${Math.abs(totals.difference)<.01?'✓':''}</strong></div></article>`;
}

function overview() {
  const rows = selectedRows(), totals = math.summarize(rows), billing = math.billingTotals(selectedInvoices());
  const change = totals.change;
  const delta = change === null ? 'No opening base' : `${change>=0?'↗':'↘'} ${percent(Math.abs(change))}`;
  const signal = totals.nrr === null ? 'Start with the first paid customer cohort.' : change < 0 ? 'Revenue is declining in this view.' : totals.nrr < 1 ? 'Growth is outpacing retention.' : 'Existing customers are adding value.';
  const explanation = totals.nrr === null ? 'This selection has no opening MRR. Retention needs an opening paid customer cohort.' : totals.nrr < 1 ? `The opening customer cohort retained ${percent(totals.nrr)} of its recurring value at constant currency. New business can lift total MRR while existing revenue contracts.` : `The opening customer cohort now represents ${percent(totals.nrr)} of its previous recurring value at constant currency. Check expansion alongside churn before changing the plan.`;
  document.querySelector('#view').innerHTML = `<section class="metrics">${metric('Monthly recurring revenue',money(totals.closing_mrr),`<span class="delta ${change<0?'down':''}">${delta}</span> from opening MRR`)}${metric('Annualized recurring revenue',money(totals.arr),'Closing MRR × 12 · subscription run rate','◷')}${metric('Net revenue retention',percent(totals.nrr),'Opening cohort · constant currency','◎')}${metric('Open invoice balance',money(billing.outstanding),`${billing.unpaid} invoices · issued in this month`,'▤')}</section>
  <section class="workspace-grid"><article class="panel"><div class="panel-title"><div><h2>Recurring revenue over time</h2><p>Month end balances · selected region and channel</p></div><span class="legend">MRR in CAD</span></div>${lineChart(math.filterRows(data.rows,state,false))}</article><article class="panel insight-panel"><div class="insight-kicker">MY NOTES</div><h2>${signal}</h2><p>${explanation}</p><div class="insight-rule"></div><div><div class="small-row"><span>Active paid accounts</span><strong>${totals.active}</strong></div><div class="small-row"><span>Gross revenue retention</span><strong>${percent(totals.grr)}</strong></div><div class="small-row"><span>Net new recurring revenue</span><strong>${preciseMoney(totals.closing_mrr-totals.opening_mrr)}</strong></div></div></article></section>
  <section class="bottom-grid">${movementPanel(totals)}<article class="panel"><div class="panel-title"><div><h2>Numbers you can trace</h2><p>Data checks completed in the Python analysis</p></div><span class="pill">${data.checks.filter(row=>row.passed).length}/${data.checks.length} passed</span></div><div class="quality-grid">${data.checks.slice(0,5).map(check=>`<div class="quality-item"><span class="check-circle">${check.passed?'✓':'!'}</span>${check.check}</div>`).join('')}</div><p class="quality-note">Three repeated event deliveries and two repeated invoice rows were detected and removed. Select a customer below to inspect its subscription and invoice records.</p></article></section>${customerTable(rows, true)}`;
}

function customerTable(rows, preview = false) {
  const search = state.search.toLowerCase();
  const matches = rows.filter(row => `${row.company} ${row.customer_id}`.toLowerCase().includes(search)).sort((a,b)=>b.closing_mrr-a.closing_mrr);
  const count = preview ? 5 : 15;
  const pageCount = Math.max(1,Math.ceil(matches.length/count));
  state.page = Math.min(state.page,pageCount);
  const visible = matches.slice((state.page-1)*count,state.page*count);
  return `<article class="panel"><div class="table-toolbar"><div><h2>Behind the number</h2><p>${monthName(state.month)} · select an account to see its records</p></div><div class="table-tools">${preview?'':`<input class="search" id="customer-search" placeholder="Search company or account" aria-label="Search customers" value="${escapeHtml(state.search)}">`}<button class="secondary" id="export-customers">Export selected data ↓</button></div></div><div class="table-wrap"><table><thead><tr><th>Account</th><th>Channel</th><th>Status</th><th class="num">Opening MRR</th><th class="num">Closing MRR</th><th class="num">Change</th></tr></thead><tbody>${visible.map(row=>`<tr><td><button class="company-button" data-customer="${row.customer_id}">${escapeHtml(row.company)}</button><span style="display:block;font-size:8px;color:#9ba58e;margin-top:5px">${row.customer_id} · ${row.currency} · ${row.billing_interval==='year'?'Annual':'Monthly'}</span></td><td>${row.channel}</td><td><span class="status ${row.status}">${row.status.replace('_',' ')}</span></td><td class="num">${preciseMoney(row.opening_mrr)}</td><td class="num">${preciseMoney(row.closing_mrr)}</td><td class="num">${preciseMoney(row.closing_mrr-row.opening_mrr)}</td></tr>`).join('')}</tbody></table>${!visible.length?'<p class="empty">No accounts match this selection.</p>':''}</div><div class="table-bottom"><span>${matches.length} matching accounts · amounts in CAD</span>${preview?'<button class="text-button" data-tab="customers">View all accounts →</button>':`<div class="paging"><button id="previous-page" ${state.page===1?'disabled':''}>←</button><span>${state.page} / ${pageCount}</span><button id="next-page" ${state.page===pageCount?'disabled':''}>→</button></div>`}</div></article>`;
}

function billingView() {
  const rows = selectedInvoices(), totals = math.billingTotals(rows);
  document.querySelector('#view').innerHTML = `<section class="metrics">${metric('Net invoices issued',money(totals.billed),'Invoice amounts less credit notes')}${metric('Net cash collected',money(totals.cash),'Payments less cash refunds','↓')}${metric('Outstanding balance',money(totals.outstanding),'For invoices issued in this month','▤')}${metric('Invoice reconciliation',preciseMoney(totals.billed-totals.cash-totals.outstanding),'Billed − net cash − outstanding','✓')}</section><p class="bill-note">This view follows the selected month's invoice cohort. Annual invoices cover 12 months, and credits affect billing rather than the subscription run rate. These figures are not recognized revenue or an all-period accounts receivable balance.</p><article class="panel"><div class="table-toolbar"><div><h2>Invoice trail</h2><p>Gross amount, credit, payment and refund amounts are in the invoice currency.</p></div><button class="secondary" id="export-invoices">Export invoice data ↓</button></div><div class="table-wrap"><table><thead><tr><th>Invoice / account</th><th>Currency</th><th class="num">Gross</th><th class="num">Credit</th><th class="num">Payment</th><th class="num">Refund</th><th class="num">Open CAD</th></tr></thead><tbody>${rows.map(row=>`<tr><td>${row.invoice_id}<br><button class="company-button" data-customer="${row.customer_id}" style="margin-top:6px;font-size:9px">${escapeHtml(row.company)}</button></td><td>${row.currency}</td>${['gross_minor','credits_minor','payments_minor','refunds_minor'].map(key=>`<td class="num">${(row[key]/100).toFixed(2)}</td>`).join('')}<td class="num">${preciseMoney(row.outstanding_cad)}</td></tr>`).join('')}</tbody></table>${!rows.length?'<p class="empty">No invoices for this selection.</p>':''}</div></article>`;
}

function definitionsView() {
  document.querySelector('#view').innerHTML = `<p class="section-intro">I built this to connect a commercial question to the underlying records. The figures are generated, but the checks and calculations run on the actual records included in the project.</p><section class="definition-grid"><article class="panel"><h2>What counts as recurring revenue?</h2><p>MRR is the monthly value of active and past-due fixed-price subscriptions. Annual amounts are divided by 12. Free, cancelled and unpaid subscriptions contribute zero. This demonstration has no usage charges or taxes.</p><p>ARR is closing MRR multiplied by 12. Both describe a run rate. They are different from invoice value, collected cash and recognized revenue.</p></article><article class="panel"><h2>How the movement reconciles</h2><p><code>Closing MRR = opening + new + reactivation + expansion + contraction + churn + FX</code></p><p>Contraction and churn are signed negative amounts. Commercial changes use current-month FX. FX revalues the opening local-currency balance. Each customer's movement reconciles before the totals are added.</p></article><article class="panel"><h2>Which customers enter retention?</h2><p>NRR uses customers with positive opening MRR. Their closing local-currency value is converted at opening FX, removing currency movement. New and reactivated accounts are excluded from this opening cohort.</p><p>GRR also excludes expansion by capping each retained account at its opening value. Both are calculated from summed values, not an average of customer percentages. A missing opening base is shown as unavailable.</p></article><article class="panel"><h2>Follow one account</h2><p>Open the customer ledger and search for <b>Midmonth Upgrade</b> in September 2026. It moves from CAD 100 to CAD 200 MRR on September 15. Billing is CAD 153.33 because only the remaining 16 days receive the higher price.</p><p>Also try <b>Returning Account</b>, <b>Past Due Account</b> and <b>Harbour USD</b> to see reactivation, collections and FX separately.</p></article><article class="panel"><h2>What is synthetic?</h2><p>All 360 accounts, subscription events, invoices, payment records and FX rates are generated with a fixed random seed. There is no real employer or customer data. Paid search has a deliberately higher simulated churn probability in later months.</p><p>The dataset demonstrates a method. It cannot establish real company performance, channel effectiveness or causality.</p></article><article class="panel"><h2>How I would use the result</h2><p>I would review existing customer losses alongside acquisition. I would then check the account records, compare regions and channels, and separate a subscription change from an invoice or payment issue.</p><p>The downloadable data, SQL and notebook document the calculation path. The walkthrough covers each control, the file structure, checks and important limitations.</p></article></section>`;
}

function showCustomer(customerId) {
  const history = data.rows.filter(row=>row.customer_id===customerId && row.month<=state.month);
  const row = history.find(row=>row.month===state.month);
  if (!row) return;
  const invoices = data.invoices.filter(invoice=>invoice.customer_id===customerId && invoice.month===state.month);
  const t = math.summarize([row]);
  document.querySelector('#dialog-content').innerHTML = `<p class="eyebrow">${row.customer_id} / ${monthName(state.month)}</p><h2>${escapeHtml(row.company)}</h2><p>${row.region} · ${row.channel} · billed in ${row.currency} · ${row.billing_interval==='year'?'annual':'monthly'} subscription</p><section class="metrics">${metric('Opening MRR',preciseMoney(row.opening_mrr),'Reported CAD')}${metric('Closing MRR',preciseMoney(row.closing_mrr),`${row.local_mrr.toFixed(2)} ${row.currency} monthly`)}${metric('Currency effect',preciseMoney(row.fx_mrr),'Opening balance revalued')}</section>${lineChart(history,true)}${movementPanel(t)}<h3>Invoices issued in this reporting month</h3>${invoices.length?`<div class="table-wrap"><table><thead><tr><th>Invoice</th><th>Gross ${row.currency}</th><th>Net billed CAD</th><th>Net cash CAD</th><th>Open CAD</th></tr></thead><tbody>${invoices.map(invoice=>`<tr><td>${invoice.invoice_id}</td><td>${(invoice.gross_minor/100).toFixed(2)}</td><td>${preciseMoney(invoice.net_billed_cad)}</td><td>${preciseMoney(invoice.net_cash_cad)}</td><td>${preciseMoney(invoice.outstanding_cad)}</td></tr>`).join('')}</tbody></table></div>`:'<p>No invoice was issued this month. An annual subscription can still contribute MRR between renewal invoices.</p>'}<p>Current FX: 1 ${row.currency} = ${row.cad_rate.toFixed(6)} CAD. Opening FX: ${row.prior_fx.toFixed(6)} CAD. Credits and refunds affect the invoice ledger, not the contract price.</p>`;
  document.querySelector('#detail-dialog').showModal();
}

function downloadRows(rows, filename) {
  if (!rows.length) return;
  const columns = Object.keys(rows[0]);
  const quote = value => '"'+String(value??'').replaceAll('"','""')+'"';
  const csv = [columns.map(quote).join(','), ...rows.map(row=>columns.map(key=>quote(row[key])).join(','))].join('\r\n');
  const url = URL.createObjectURL(new Blob([csv], {type:'text/csv;charset=utf-8;'}));
  const link = document.createElement('a');
  link.href = url; link.download = filename; link.click();
  setTimeout(()=>URL.revokeObjectURL(url),1000);
}

function render() {
  document.querySelectorAll('.nav-button').forEach(button=>button.classList.toggle('active',button.dataset.tab===state.tab));
  if (state.tab === 'overview') overview();
  else if (state.tab === 'customers') document.querySelector('#view').innerHTML = customerTable(selectedRows());
  else if (state.tab === 'billing') billingView();
  else definitionsView();
  document.querySelectorAll('[data-customer]').forEach(button=>button.addEventListener('click',()=>showCustomer(button.dataset.customer)));
  document.querySelectorAll('#view [data-tab]').forEach(button=>button.addEventListener('click',()=>{state.tab=button.dataset.tab;state.page=1;render();}));
  document.querySelector('#export-customers')?.addEventListener('click',()=>downloadRows(selectedRows().filter(row=>`${row.company} ${row.customer_id}`.toLowerCase().includes(state.search.toLowerCase())),`customer_metrics_${state.month}.csv`));
  document.querySelector('#export-invoices')?.addEventListener('click',()=>downloadRows(selectedInvoices(),`invoice_ledger_${state.month}.csv`));
  document.querySelector('#previous-page')?.addEventListener('click',()=>{state.page--;render();});
  document.querySelector('#next-page')?.addEventListener('click',()=>{state.page++;render();});
  document.querySelector('#customer-search')?.addEventListener('input',event=>{const position=event.target.selectionStart;state.search=event.target.value;state.page=1;render();const input=document.querySelector('#customer-search');input.focus();input.setSelectionRange(position,position);});
}

document.querySelector('#month-filter').innerHTML = [...data.months].reverse().map(month=>`<option value="${month}">${monthName(month)}</option>`).join('');
document.querySelector('#month-filter').value = state.month;
for (const key of ['month','region','channel']) document.querySelector(`#${key}-filter`).addEventListener('change',event=>{state[key]=event.target.value;state.page=1;state.search='';render();});
document.querySelectorAll('.nav-button').forEach(button=>button.addEventListener('click',()=>{state.tab=button.dataset.tab;state.page=1;state.search='';render();}));
document.querySelector('.brand').addEventListener('click',event=>{event.preventDefault();state.tab='overview';state.page=1;state.search='';render();});
document.querySelector('#reset-button').addEventListener('click',()=>{state.month=data.months.at(-1);state.region='All';state.channel='All';state.search='';state.page=1;for(const key of ['month','region','channel'])document.querySelector(`#${key}-filter`).value=state[key];render();});
document.querySelector('#close-dialog').addEventListener('click',()=>document.querySelector('#detail-dialog').close());
document.querySelector('#detail-dialog').addEventListener('click',event=>{if(event.target===event.currentTarget)event.currentTarget.close();});
document.querySelector('#walkthrough-button').addEventListener('click',()=>{document.querySelector('#dialog-content').innerHTML=`<p class="eyebrow">A QUICK WALKTHROUGH</p><h2>From a total to an explanation.</h2><p>Use the same records to check the headline number, its drivers and the account details.</p>${[['Choose a reporting month','Start with September 2026. Region and channel filters apply to all metrics, charts and downloads.'],['Read the revenue bridge','New business, reactivation, expansion, contraction, churn and currency explain the full change in MRR.'],['Check retention separately','NRR follows the opening paid cohort at constant currency. A growing total can still hide losses from existing accounts.'],['Open an account','Go to Customer ledger and search Midmonth Upgrade. Its September MRR is CAD 200, while the prorated invoice is CAD 153.33.'],['Compare billing and cash','Annual invoicing, credits and partial payments make these figures different from recurring revenue.'],['Read the assumptions','How this works documents the definitions. Everything here uses synthetic data and demonstrates an analytical method.']].map(([title,text],i)=>`<div class="tour-step"><span class="step-number">${i+1}</span><div><h3>${title}</h3><p>${text}</p></div></div>`).join('')}`;document.querySelector('#detail-dialog').showModal();});
render();
