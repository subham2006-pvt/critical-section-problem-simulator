const $ = (id) => document.getElementById(id);
let busy = false;
const algorithmNames = {mutex: "Mutex Lock", semaphore: "Semaphore", peterson: "Peterson's Algorithm"};

async function post(url, data={}) {
  const res = await fetch(url, {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(data)});
  const json = await res.json();
  if (!res.ok) throw new Error(json.error || "Request failed");
  return json;
}
function render(s) {
  $("tick").textContent = s.tick;
  
  $("resourceNumber").textContent = s.shared_value;
  $("entries").textContent = s.stats.entries;
  $("completed").textContent = s.stats.completed;
  $("avgWait").innerHTML = `${s.stats.avg_wait} <small>ticks</small>`;
  $("throughput").textContent = s.stats.throughput.toFixed(3);
  $("lockStatus").textContent = s.locked ? "LOCKED" : "AVAILABLE";
  $("mutexState").textContent = s.locked ? `Locked by ${s.owner || "process"}` : "Unlocked";
  $("semValue").textContent = s.semaphore_value;
  $("queueValue").textContent = s.waiting_queue.length ? s.waiting_queue.join(", ") : "Empty";
  $("safetyState").textContent = s.stats.violation_count ? "Violation detected" : "No violation detected";
  $("safetyState").className = s.stats.violation_count ? "" : "safe";
  $("ownerLabel").textContent = s.owner ? `${s.owner} owns the resource` : "No active owner";
  $("resourceSub").textContent = s.owner ? "Critical section is occupied" : "Resource is available";
  $("resourceBox").classList.toggle("active", !!s.owner);
  $("algorithmNote").textContent = s.algorithm_info.description + (s.algorithm === "peterson" ? " Peterson's algorithm supports exactly two processes." : "");
  $("processCount").disabled = s.algorithm === "peterson";
  if (s.algorithm === "peterson") $("processCount").value = "2";
  $("processList").innerHTML = s.processes.map(p => {
    let cls = p.state === "In Critical Section" ? "entered" : p.state === "Waiting" ? "waiting" : "";
    let state = p.state === "In Critical Section" ? "CRITICAL" : p.state.toUpperCase();
    return `<div class="process-card ${cls}"><div class="pid">${p.id}</div><div class="process-info"><b>${p.id} · ${p.phase === "critical" ? "Critical section" : p.phase === "entry" ? "Entry section" : "Remainder section"}</b><small>${escapeHtml(p.last_action)} · Entries: ${p.entries} · Wait: ${p.wait_ticks} ticks</small></div><span class="state-chip">${state}</span></div>`;
  }).join("");
  $("eventLog").innerHTML = s.events.map(e => `<div class="event ${e.kind}"><span class="event-time">T+${String(e.time).padStart(3,"0")}</span><i class="event-dot"></i><span>${escapeHtml(e.message)}</span></div>`).join("");
}
function escapeHtml(str) { return String(str).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c])); }
async function refresh() { const r = await fetch("/api/state"); render(await r.json()); }
async function guarded(fn) {
  if (busy) return;
  busy = true;
  $("stepBtn").disabled = $("runBtn").disabled = true;
  try { render(await fn()); } catch(e) { alert(e.message); }
  finally { busy = false; $("stepBtn").disabled = $("runBtn").disabled = false; }
}
$("algorithm").addEventListener("change", () => guarded(() => post("/api/configure", {algorithm:$("algorithm").value, process_count:Number($("processCount").value)})));
$("processCount").addEventListener("change", () => guarded(() => post("/api/configure", {algorithm:$("algorithm").value, process_count:Number($("processCount").value)})));
$("stepBtn").addEventListener("click", () => guarded(() => post("/api/step")));
$("runBtn").addEventListener("click", () => guarded(() => post("/api/run", {steps:8})));
$("resetBtn").addEventListener("click", () => guarded(() => post("/api/reset")));
refresh();
