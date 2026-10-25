const data = window.PRICING_DATA;
const el = id => document.getElementById(id);
const money = value => new Intl.NumberFormat('en-CA',{style:'currency',currency:'CAD',maximumFractionDigits:0}).format(value);
const preciseMoney = value => new Intl.NumberFormat('en-CA',{style:'currency',currency:'CAD',minimumFractionDigits:2}).format(value);
const percent = value => `${value.toFixed(3)}%`;
const controls = ['plan','segment','channel','costShock','volume','search'].map(el);
let currentRows = [];

function economics(merchant, planName, costShockBps, volumeChangePct){
  const plan=data.plans[planName], costs=data.costs, factor=1+volumeChangePct/100;
  const sales=merchant.monthly_sales_cad*factor, transactions=Math.round(merchant.transactions*factor);
  const debitTransactions=Math.round(transactions*merchant.debit_share), creditTransactions=transactions-debitTransactions;
  const creditSales=sales*(1-merchant.debit_share), debitSales=sales*merchant.debit_share;
  const refundAmount=sales*merchant.refund_rate, netSales=sales-refundAmount;
  const baseInterchangeBps=costs.credit_interchange_bps+merchant.premium_card_share*costs.premium_increment_bps+merchant.international_share*costs.international_increment_bps;
  const interchangeCost=creditSales*(baseInterchangeBps+costShockBps)/10000;
  const debitCost=debitTransactions*costs.debit_per_transaction_cents/100;
  const networkCost=sales*costs.network_bps/10000;
  const processorCost=sales*costs.processor_bps/10000+transactions*costs.processor_per_transaction_cents/100;
  const refundCost=transactions*merchant.refund_rate*costs.refund_handling_cents/100;
  const totalCost=interchangeCost+debitCost+networkCost+processorCost+refundCost;
  const pricedCost=totalCost-creditSales*costShockBps/10000;
  const feeRevenue=pricedCost+sales*plan.markup_bps/10000+transactions*plan.per_transaction_cents/100+plan.monthly_fee_cad;
  const contribution=feeRevenue-totalCost;
  const fixedAndTransaction=transactions*plan.per_transaction_cents/100+plan.monthly_fee_cad;
  return {...merchant,plan:planName,scenario_sales_cad:sales,scenario_transactions:transactions,debit_transactions:debitTransactions,credit_transactions:creditTransactions,credit_sales_cad:creditSales,debit_sales_cad:debitSales,refund_amount_cad:refundAmount,net_sales_cad:netSales,interchange_cost_cad:interchangeCost,debit_cost_cad:debitCost,network_cost_cad:networkCost,processor_cost_cad:processorCost,refund_handling_cost_cad:refundCost,total_cost_cad:totalCost,fee_revenue_cad:feeRevenue,contribution_margin_cad:contribution,effective_rate_pct:sales?feeRevenue/sales*100:null,margin_rate_pct:feeRevenue?contribution/feeRevenue*100:null,break_even_markup_bps:sales?(totalCost-fixedAndTransaction)/sales*10000:null};
}

function filteredRows(){
  const segment=el('segment').value, channel=el('channel').value, query=el('search').value.trim().toUpperCase();
  return data.merchants.filter(row=>(segment==='All'||row.segment===segment)&&(channel==='All'||row.channel===channel)&&(!query||row.merchant_id.includes(query)));
}

function render(){
  const plan=el('plan').value, shock=Number(el('costShock').value), volume=Number(el('volume').value);
  el('costShockValue').textContent=`${shock>0?'+':''}${shock} bps`; el('volumeValue').textContent=`${volume>0?'+':''}${volume}%`;
  currentRows=filteredRows().map(row=>economics(row,plan,shock,volume));
  const empty=!currentRows.length; el('emptyState').hidden=!empty; el('metrics').hidden=empty; el('segmentChart').parentElement.hidden=empty; el('decisionNote').hidden=empty; el('export').disabled=empty;
  el('resultTitle').textContent=`${plan} pricing`;
  const p=data.plans[plan]; el('planTerms').textContent=`${p.markup_bps} bps commercial markup + ${p.per_transaction_cents}¢ per transaction + ${preciseMoney(p.monthly_fee_cad)} monthly`;
  if(empty){el('merchantRows').innerHTML='<tr><td colspan="7">No merchant rows to show.</td></tr>';return;}
  const sum=key=>currentRows.reduce((total,row)=>total+row[key],0), sales=sum('scenario_sales_cad'), fees=sum('fee_revenue_cad'), margin=sum('contribution_margin_cad');
  const negative=currentRows.filter(row=>row.contribution_margin_cad<0).length;
  el('salesMetric').textContent=money(sales); el('merchantMetric').textContent=`${currentRows.length} merchants · ${Math.round(sum('scenario_transactions')).toLocaleString('en-CA')} transactions`;
  el('rateMetric').textContent=percent(fees/sales*100); el('marginMetric').textContent=money(margin); el('marginMetric').className=margin<0?'negative-text':'positive-text';
  el('marginRateMetric').textContent=`${(margin/fees*100).toFixed(1)}% of fee revenue`; el('negativeMetric').textContent=negative.toLocaleString('en-CA');
  renderChart(); renderTable();
  const note=shock>=75?`The selected cost increase leaves ${negative} merchant${negative===1?'':'s'} below zero contribution. Pricing is held fixed in this stress case.`:volume<=-30?'The volume decline reduces percentage revenue and transaction fees while the monthly fee remains fixed. Check the merchant detail before treating the portfolio average as universal.':`${plan} produces ${money(margin)} of contribution margin for this filtered synthetic group. Compare the effective rate and the segment bars before choosing one structure for every merchant.`;
  el('decisionNote').innerHTML=`<strong>Readout.</strong> ${note}`;
}

function renderChart(){
  const segments=['Micro','Small','Mid-market','Enterprise'];
  const values=segments.map(segment=>({segment,value:currentRows.filter(r=>r.segment===segment).reduce((t,r)=>t+r.contribution_margin_cad,0)}));
  const scale=Math.max(...values.map(v=>Math.abs(v.value)),1);
  el('segmentChart').innerHTML=values.map(v=>`<div class="bar-row"><span class="bar-label">${v.segment}</span><span class="bar-track"><span class="bar-fill ${v.value<0?'negative':''}" style="width:${Math.abs(v.value)/scale*100}%"></span></span><span class="bar-value ${v.value<0?'negative-text':''}">${money(v.value)}</span></div>`).join('');
}

function renderTable(){
  const rows=[...currentRows].sort((a,b)=>a.contribution_margin_cad-b.contribution_margin_cad).slice(0,12);
  el('merchantRows').innerHTML=rows.map(row=>`<tr><td>${row.merchant_id}</td><td>${row.segment}</td><td>${row.channel}</td><td>${money(row.scenario_sales_cad)}</td><td>${percent(row.effective_rate_pct)}</td><td class="${row.contribution_margin_cad<0?'negative-text':''}">${money(row.contribution_margin_cad)}</td><td><button class="row-button" data-id="${row.merchant_id}">Inspect</button></td></tr>`).join('');
  document.querySelectorAll('.row-button').forEach(button=>button.addEventListener('click',()=>openDetail(button.dataset.id)));
}

function openDetail(id){
  const row=currentRows.find(item=>item.merchant_id===id); if(!row)return;
  const costs=[['Interchange',row.interchange_cost_cad],['Debit',row.debit_cost_cad],['Network',row.network_cost_cad],['Processing',row.processor_cost_cad],['Refund handling',row.refund_handling_cost_cad]];
  el('dialogContent').innerHTML=`<div class="dialog-body"><p class="section-label">${row.segment} · ${row.channel}</p><h2>${row.merchant_id}</h2><p>${money(row.scenario_sales_cad)} processed across ${row.scenario_transactions.toLocaleString('en-CA')} transactions. Refunds are ${money(row.refund_amount_cad)} in this scenario.</p><div class="bridge"><div><span>Merchant fee revenue</span><strong>${preciseMoney(row.fee_revenue_cad)}</strong></div><div><span>Total modelled cost</span><strong>${preciseMoney(row.total_cost_cad)}</strong></div>${costs.map(c=>`<div><span>${c[0]}</span><strong>${preciseMoney(c[1])}</strong></div>`).join('')}<div><span>Contribution margin</span><strong class="${row.contribution_margin_cad<0?'negative-text':'positive-text'}">${preciseMoney(row.contribution_margin_cad)}</strong><small>${row.margin_rate_pct.toFixed(1)}% of fee revenue</small></div><div><span>Break-even markup</span><strong>${row.break_even_markup_bps.toFixed(1)} bps</strong><small>After fixed and transaction fees</small></div></div></div>`;
  el('merchantDialog').showModal();
}

function exportCsv(){
  if(!currentRows.length)return;
  const columns=['merchant_id','segment','channel','scenario_sales_cad','scenario_transactions','refund_amount_cad','fee_revenue_cad','total_cost_cad','contribution_margin_cad','effective_rate_pct','break_even_markup_bps'];
  const lines=[columns.join(','),...currentRows.map(row=>columns.map(key=>typeof row[key]==='number'?row[key].toFixed(4):`"${String(row[key]).replaceAll('"','""')}"`).join(','))];
  const link=document.createElement('a'); link.href=URL.createObjectURL(new Blob([lines.join('\n')],{type:'text/csv'})); link.download='merchant_pricing_filtered.csv'; link.click(); URL.revokeObjectURL(link.href);
}

controls.forEach(control=>control.addEventListener(control.type==='search'?'input':'change',render));
el('reset').addEventListener('click',()=>{el('plan').value='Current';el('segment').value='All';el('channel').value='All';el('costShock').value='0';el('volume').value='0';el('search').value='';render();});
el('export').addEventListener('click',exportCsv); el('merchantDialog').querySelector('.dialog-close').addEventListener('click',()=>el('merchantDialog').close());
render();
