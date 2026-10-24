const demo = window.METRIC_DEMO;
const questionInput = document.querySelector("#question");
const examples = new Map(demo.examples.map(item => [item.question.toLowerCase(), item]));
let current = null;

document.querySelector("#scorecard").textContent = `${demo.scorecard.passed}/${demo.scorecard.cases} evaluation cases passed`;
document.querySelector("#examples").innerHTML = demo.examples.slice(0, 6).map(item => `<button class="example-button" type="button" data-question="${item.question}">${item.question}</button>`).join("");

const escapeHtml = value => String(value).replace(/[&<>"]/g, character => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[character]));
const formatCell = value => typeof value === "number" ? new Intl.NumberFormat("en-CA", {maximumFractionDigits:2}).format(value) : value;

function renderTable(answer) {
  if (!answer.rows.length) return "";
  const head = answer.columns.map(column => `<th>${escapeHtml(column)}</th>`).join("");
  const body = answer.rows.map(row => `<tr>${row.map(value => `<td>${escapeHtml(formatCell(value))}</td>`).join("")}</tr>`).join("");
  return `<table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table>`;
}

function fallback(question) {
  const lower = question.toLowerCase();
  if (["revenue","growth","performing","doing"].some(word => lower.includes(word))) {
    return {status:"clarification",answer:"Please specify MRR, active customers, churn, NRR or invoice collection rate, plus a month or year.",interpretation:"The request needs a metric and time period before a query can run.",sql:null,parameters:[],columns:[],rows:[],definition:null};
  }
  return {status:"unsupported",answer:"I could not map this to an approved metric.",interpretation:"This question is outside the approved metric dictionary.",sql:null,parameters:[],columns:[],rows:[],definition:null};
}

function render(answer) {
  current = answer;
  const badge = document.querySelector("#status-badge");
  badge.textContent = answer.status;
  badge.className = `badge ${answer.status}`;
  document.querySelector("#answer").textContent = answer.answer;
  document.querySelector("#interpretation").textContent = answer.interpretation;
  document.querySelector("#sql").textContent = answer.sql || "No query was run.";
  document.querySelector("#parameters").textContent = answer.parameters.length ? JSON.stringify(answer.parameters) : "None";
  document.querySelector("#definition").textContent = answer.definition || "No metric definition selected.";
  document.querySelector("#result-table").innerHTML = renderTable(answer);
  document.querySelector("#copy-button").disabled = !answer.sql;
  document.querySelector("#export-button").disabled = !answer.rows.length;
}

function runQuestion(question) {
  const answer = examples.get(question.trim().toLowerCase()) || fallback(question);
  render(answer);
}

document.querySelector("#question-form").addEventListener("submit", event => { event.preventDefault(); runQuestion(questionInput.value); });
document.querySelector("#examples").addEventListener("click", event => {
  if (!event.target.dataset.question) return;
  questionInput.value = event.target.dataset.question;
  runQuestion(questionInput.value);
});
document.querySelector("#copy-button").addEventListener("click", async () => {
  if (current?.sql) await navigator.clipboard.writeText(current.sql);
});
document.querySelector("#export-button").addEventListener("click", () => {
  if (!current?.rows.length) return;
  const lines = [current.columns.join(","), ...current.rows.map(row => row.join(","))];
  const link = document.createElement("a");
  link.href = URL.createObjectURL(new Blob([lines.join("\n")], {type:"text/csv"}));
  link.download = "metric_result.csv";
  link.click();
  URL.revokeObjectURL(link.href);
});

runQuestion(questionInput.value);
