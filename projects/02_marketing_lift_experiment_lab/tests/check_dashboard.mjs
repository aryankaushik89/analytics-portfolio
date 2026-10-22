import fs from 'node:fs';
import assert from 'node:assert/strict';
import {selectRows, summarize, economics, decide, sampleSize, difference, csvText} from '../dist/metrics.mjs';

const data = JSON.parse(fs.readFileSync(new URL('../dist/data.json', import.meta.url)));
const oracles = JSON.parse(fs.readFileSync(new URL('../outputs/python_oracles.json', import.meta.url)));
let count = 0;
for (const oracle of oracles) {
  const result = summarize(selectRows(data, oracle));
  for (const key of ['n_t', 'n_c', 'y_t', 'y_c']) assert.equal(result[key], oracle[key]);
  for (const key of ['effect', 'lower', 'upper']) assert.ok(Math.abs(result[key] - oracle[key]) < 1e-12);
  assert.ok(Math.abs(result.srm_p - oracle.srm_p) < 1.5e-7);
  const net = economics(result, 0.6, 90);
  for (const key of ['point', 'lower', 'upper']) assert.ok(Math.abs(net[key] - oracle.net[key]) < 1e-8);
  const quality = data.quality.find(r => r.experiment_id === oracle.experiment);
  assert.equal(decide(result, quality, oracle.split, 0.6, 90), oracle.decision);
  count++;
}
assert.deepEqual(difference(0, 0, 20, 1), [null, null, null]);
assert.ok(difference(100, 0, 100, 0)[1] < 0);
assert.equal(decide(summarize([]), {blocked: false, srm_p: 1}, 'Evaluation', 0.6, 90), 'No users');
assert.equal(sampleSize(0, 0.01), null);
assert.equal(sampleSize(0.95, 0.1), null);
assert.ok(sampleSize(0.07, 0.005) > sampleSize(0.07, 0.01));
assert.equal(csvText([{a: 'a,b', b: 'a"b'}]), '"a","b"\r\n"a,b","a""b"');
console.log(`${count} filter selections matched independent Python counts, confidence intervals, SRM probabilities, economics and decisions. Seven empty-state, planning and CSV boundary checks passed.`);
