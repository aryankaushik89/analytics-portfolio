import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const context = {window:{}};
vm.createContext(context);
vm.runInContext(fs.readFileSync('dist/metrics.js','utf8'),context);
const data = JSON.parse(fs.readFileSync('outputs/dashboard_data.json','utf8'));
const math = context.window.RevenueMath;
let cases = 0;
for (const month of data.months) {
  for (const region of ['All','Canada','United States','Europe','Missing region']) {
    for (const channel of ['All','Organic','Paid search','Partner','Outbound']) {
      const selection={month,region,channel};
      const rows=math.filterRows(data.rows,selection);
      const total=math.summarize(rows);
      const bills=math.billingTotals(math.filterRows(data.invoices,selection));
      assert(Math.abs(total.difference)<.001,'MRR bridge');
      assert(Math.abs(bills.billed-bills.cash-bills.outstanding)<.001,'invoice bridge');
      assert(total.grr===null || total.grr<=1.0000001,'GRR cap');
      if(!rows.length) assert.equal(total.nrr,null,'empty retention');
      const expected=rows.reduce((sum,row)=>sum+row.closing_mrr,0);
      assert.equal(total.closing_mrr,expected,'MRR aggregation');
      cases++;
    }
  }
}
const latest=math.summarize(math.filterRows(data.rows,{month:'2026-09',region:'All',channel:'All'}));
assert(Math.abs(latest.closing_mrr-85826.85004731)<.01,'independent Python result');
console.log(`${cases} dashboard selection cases passed, including empty selections.`);
