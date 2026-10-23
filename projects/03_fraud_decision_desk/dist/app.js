const transactions = window.FRAUD_DATA.transactions;
const saved = window.FRAUD_DATA.metrics;
const defaults = {
  threshold: Number(saved.selected_threshold),
  capacity: Number(saved.assumptions.daily_review_capacity),
};

const thresholdInput = document.querySelector("#threshold");
const capacityInput = document.querySelector("#capacity");
const dateFilter = document.querySelector("#date-filter");
const queueBody = document.querySelector("#queue-body");
const emptyState = document.querySelector("#empty-state");
const detailDialog = document.querySelector("#detail-dialog");

thresholdInput.value = defaults.threshold;
capacityInput.value = defaults.capacity;

const dates = [...new Set(transactions.map(row => row.day))].sort();
dateFilter.innerHTML = `<option value="all">All test dates</option>${dates.map(day => `<option value="${day}">${day}</option>`).join("")}`;

const money = value => new Intl.NumberFormat("en-CA", { style: "currency", currency: "CAD", maximumFractionDigits: 0 }).format(value);
const number = value => new Intl.NumberFormat("en-CA").format(value);
const percent = value => `${(value * 100).toFixed(1)}%`;

function buildQueue(rows, threshold, capacity) {
  const grouped = new Map();
  rows.forEach(row => {
    if (!grouped.has(row.day)) grouped.set(row.day, []);
    if (row.fraud_score >= threshold) grouped.get(row.day).push(row);
  });
  const queue = [];
  grouped.forEach(dayRows => {
    dayRows.sort((a, b) => b.fraud_score - a.fraud_score || a.transaction_time.localeCompare(b.transaction_time));
    queue.push(...dayRows.slice(0, capacity));
  });
  return queue.sort((a, b) => b.fraud_score - a.fraud_score);
}

function calculate(rows, queue) {
  const reviewedIds = new Set(queue.map(row => row.transaction_id));
  const frauds = rows.filter(row => row.is_fraud === 1);
  const truePositives = queue.filter(row => row.is_fraud === 1);
  const falsePositives = queue.filter(row => row.is_fraud === 0);
  const missed = frauds.filter(row => !reviewedIds.has(row.transaction_id));
  const avoidedLoss = truePositives.reduce((sum, row) => sum + row.amount, 0) * saved.assumptions.recovery_rate;
  const reviewCost = queue.length * saved.assumptions.review_cost;
  const frictionCost = falsePositives.length * saved.assumptions.false_positive_cost;
  return {
    truePositive: truePositives.length,
    falsePositive: falsePositives.length,
    falseNegative: missed.length,
    trueNegative: rows.length - truePositives.length - falsePositives.length - missed.length,
    precision: queue.length ? truePositives.length / queue.length : 0,
    recall: frauds.length ? truePositives.length / frauds.length : 0,
    avoidedLoss,
    reviewCost,
    frictionCost,
    netValue: avoidedLoss - reviewCost - frictionCost,
  };
}

function renderMatrix(metrics) {
  const items = [
    ["Fraud reviewed", metrics.truePositive],
    ["Legitimate reviewed", metrics.falsePositive],
    ["Fraud missed", metrics.falseNegative],
    ["Legitimate not reviewed", metrics.trueNegative],
  ];
  document.querySelector("#matrix").innerHTML = items.map(([label, value]) => `<div><span>${label}</span><strong>${number(value)}</strong></div>`).join("");
}

function renderCosts(metrics) {
  const items = [
    ["Avoided fraud loss", metrics.avoidedLoss, false],
    ["Review cost", metrics.reviewCost, true],
    ["Friction cost", metrics.frictionCost, true],
  ];
  const max = Math.max(...items.map(item => item[1]), 1);
  document.querySelector("#cost-bars").innerHTML = items.map(([label, value, loss]) => `
    <div class="bar-row ${loss ? "loss" : ""}">
      <span>${label}</span><div class="bar-track"><div class="bar-fill" style="width:${value / max * 100}%"></div></div><strong>${money(value)}</strong>
    </div>`).join("");
}

function renderQueue(queue) {
  emptyState.hidden = queue.length > 0;
  queueBody.innerHTML = queue.slice(0, 100).map(row => `
    <tr>
      <td>${row.transaction_id}</td><td>${row.day}</td><td>${money(row.amount)}</td><td>${percent(row.fraud_score)}</td>
      <td>${row.velocity_1h}</td><td class="${row.is_fraud ? "outcome-fraud" : ""}">${row.is_fraud ? "Fraud" : "Legitimate"}</td>
      <td><button class="record-button" data-id="${row.transaction_id}">Details</button></td>
    </tr>`).join("");
}

function update() {
  const threshold = Number(thresholdInput.value);
  const capacity = Number(capacityInput.value);
  const filtered = dateFilter.value === "all" ? transactions : transactions.filter(row => row.day === dateFilter.value);
  const queue = buildQueue(filtered, threshold, capacity);
  const metrics = calculate(filtered, queue);
  window.currentQueue = queue;

  document.querySelector("#threshold-value").textContent = percent(threshold);
  document.querySelector("#capacity-value").textContent = `${number(capacity)} reviews per day`;
  document.querySelector("#reviews").textContent = number(queue.length);
  document.querySelector("#review-share").textContent = `${percent(queue.length / Math.max(filtered.length, 1))} of transactions`;
  document.querySelector("#precision").textContent = percent(metrics.precision);
  document.querySelector("#recall").textContent = percent(metrics.recall);
  document.querySelector("#net-value").textContent = money(metrics.netValue);
  document.querySelector("#result-note").textContent = dateFilter.value === "all" ? `${dates[0]} to ${dates.at(-1)}` : dateFilter.value;
  renderMatrix(metrics);
  renderCosts(metrics);
  renderQueue(queue);
}

function showDetails(id) {
  const row = transactions.find(item => item.transaction_id === id);
  document.querySelector("#detail-title").textContent = row.transaction_id;
  const details = [
    ["Time", new Date(row.transaction_time).toLocaleString("en-CA")], ["Amount", money(row.amount)],
    ["Fraud score", percent(row.fraud_score)], ["Observed outcome", row.is_fraud ? "Fraud" : "Legitimate"],
    ["Transactions in prior hour", row.velocity_1h], ["Distance from home", `${row.distance_home_km.toFixed(1)} km`],
    ["Merchant risk input", row.merchant_risk.toFixed(3)], ["Channel", row.card_present ? "Card present" : "Card not present"],
    ["International flag", row.foreign_transaction ? "Yes" : "No"],
  ];
  document.querySelector("#detail-list").innerHTML = details.map(([term, value]) => `<div><dt>${term}</dt><dd>${value}</dd></div>`).join("");
  detailDialog.showModal();
}

function exportQueue() {
  if (!window.currentQueue.length) return;
  const columns = ["transaction_id", "transaction_time", "amount", "fraud_score", "velocity_1h", "is_fraud"];
  const lines = [columns.join(","), ...window.currentQueue.map(row => columns.map(column => row[column]).join(","))];
  const blob = new Blob([lines.join("\n")], { type: "text/csv" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "fraud_review_queue.csv";
  link.click();
  URL.revokeObjectURL(link.href);
}

[thresholdInput, capacityInput, dateFilter].forEach(control => control.addEventListener("input", update));
document.querySelector("#reset-button").addEventListener("click", () => {
  thresholdInput.value = defaults.threshold;
  capacityInput.value = defaults.capacity;
  dateFilter.value = "all";
  update();
});
document.querySelector("#export-button").addEventListener("click", exportQueue);
queueBody.addEventListener("click", event => {
  if (event.target.matches("[data-id]")) showDetails(event.target.dataset.id);
});

update();
