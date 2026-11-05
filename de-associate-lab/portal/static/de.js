// DE Lab — front end built from the Claude Design screens.
// One hash router; every screen renders into #app from live API data.
"use strict";

// ---------------------------------------------------------------- helpers
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const esc = (t) => String(t ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const md = (t) => (window.marked ? marked.parse(t || "") : `<p>${esc(t)}</p>`);
const mdi = (t) => (window.marked ? marked.parseInline(t || "") : esc(t));
const store = {
  get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch { return d; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} },
  del(k) { try { localStorage.removeItem(k); } catch {} },
};
async function api(path, body) {
  const r = await fetch(path, body ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) } : {});
  const j = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(j.error || r.statusText);
  return j;
}
function busy(msg) { $("#overlayMsg").textContent = msg; $("#overlay").hidden = false; }
function idle() { $("#overlay").hidden = true; }
const todayISO = () => new Date().toLocaleDateString("en-CA");
const fmtDate = (iso) => { if (!iso) return ""; const d = new Date(iso + "T12:00:00"); return d.toLocaleDateString(undefined, { day: "numeric", month: "short" }); };
const shuffle = (a) => { a = [...a]; for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
const pct = (a, b) => (b ? Math.round((100 * a) / b) : 0);

const I = {
  check: '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
  lock: '<rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 018 0v3"/>',
  back: '<path d="M15 6l-6 6 6 6"/>', next: '<path d="M9 6l6 6-6 6"/>',
  play: '<path d="M7 5l12 7-12 7z"/>', home: '<path d="M4 11l8-7 8 7v9H4z"/><path d="M10 20v-6h4v6"/>',
  flask: '<path d="M9 3h6M10 3v6L5 19a1.5 1.5 0 001.3 2h11.4A1.5 1.5 0 0019 19l-5-10V3"/><path d="M7.5 15h9"/>',
  cards: '<rect x="3" y="6" width="14" height="14" rx="2"/><path d="M7 3h12a2 2 0 012 2v12"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>', chart: '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
  flame: '<path d="M12 3s5 4.5 5 10a5 5 0 01-10 0c0-2.5 1.5-4 1.5-4S9 12 11 12c0-4 1-9 1-9z"/>',
  bulb: '<path d="M9 18h6M10 21h4M12 3a6 6 0 00-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0012 3z"/>',
  flag: '<path d="M5 21V4M5 4h11l-2 4 2 4H5"/>', target: '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
  x: '<path d="M6 6l12 12M18 6L6 18"/>', warn: '<path d="M12 3l10 18H2z"/><path d="M12 10v5M12 18h.01"/>',
  reset: '<path d="M4 4v6h6"/><path d="M5 15a8 8 0 102-8.5L4 10"/>', eye: '<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
};
const ic = (n, size = 18, w = 2.2, cls = "icon") => `<svg class="${cls}" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${I[n]}</svg>`;

const LAB_META = {
  lab1_ingestion: { sub: "Load files into tables", sec: "Section 2" },
  lab2_jobs: { sub: "Run tasks in the right order", sec: "Section 4" },
  lab3_pipelines: { sub: "Pipelines that check data quality", sec: "Section 3" },
  lab4_devops: { sub: "Modular code and unit tests", sec: "Bonus" },
  lab5_delta_sql_streaming: { sub: "Delta history, SQL and streaming", sec: "Sections 3 + 6" },
  lab6_transform_tuning: { sub: "Clean, join and tune data", sec: "Section 3" },
  lab7_troubleshooting: { sub: "Find and fix slow jobs", sec: "Sections 6 + 1" },
  lab8_cicd_bundles: { sub: "Git folders and bundles", sec: "Section 5" },
  lab9_governance: { sub: "Who can see which data", sec: "Section 7" },
};
const SEC_SHORT = { 1: "Platform", 2: "Ingestion", 3: "Transformation", 4: "Lakeflow Jobs", 5: "CI/CD", 6: "Troubleshooting", 7: "Governance" };
const cleanTitle = (t) => String(t || "").replace(/^\d[a-z](-\d)?\s*·\s*/, "").replace(/\s*\(lesson [\d.]+\)/, "");
const labNo = (id) => id.match(/lab(\d)/)[1];

// ---------------------------------------------------------------- state
const S = { dash: null, labs: [], bank: null, catalog: null, sess: null, mock: null, timer: null, editor: null, gapMode: true };
async function refresh() {
  [S.dash, S.labs] = await Promise.all([api("/api/dashboard"), api("/api/labs")]);
}
async function bank() {
  if (!S.bank) S.bank = await api("/api/exam/questions");
  return S.bank;
}
const gated = (s) => s.type !== "info";
const unlocked = (lab, i) => lab.steps.slice(0, i).filter(gated).every((s) => s.done);
const stepState = (lab, i, cur) => {
  const s = lab.steps[i];
  if (s.done) return "done";
  if (cur && s.key === cur) return "now";
  return unlocked(lab, i) ? "open" : "lock";
};

// ---------------------------------------------------------------- shell
function shell(active, inner, cls = "") {
  const d = S.dash;
  const due = d.due.today;
  const nav = [
    ["today", "Today", "home", ""],
    ["labs", "Labs", "flask", `<span class="count">${d.steps.done}/${d.steps.total}</span>`],
    ["practice", "Practice", "cards", due ? `<span class="badge">${due} due</span>` : `<span class="count">${d.questions.tried}/${d.questions.total}</span>`],
    ["mock", "Mock exam", "clock", ""],
    ["progress", "Progress", "chart", ""],
  ];
  const ex = d.profile.exam_date;
  const left = ex ? Math.round((new Date(ex + "T12:00:00") - new Date(todayISO() + "T12:00:00")) / 864e5) : null;
  return `<div class="shell">
    <aside class="side">
      <a class="brand" href="#/today"><span class="logo">DE</span><span><b>DE Lab</b><small>Data Engineer Associate</small></span></a>
      <nav class="navlist" aria-label="Main">${nav.map(([id, label, icon, extra]) =>
        `<a class="nav ${active === id ? "on" : ""}" href="#/${id}" ${active === id ? 'aria-current="page"' : ""}>${ic(icon, 20, 2)}${label}${extra}</a>`).join("")}</nav>
      <div class="streak">
        <div class="row">${ic("flame", 26, 2)}<div><b>${d.streak ? `${d.streak}-day streak` : "Start a streak"}</b><small>${d.today_active ? "You studied today. Nice!" : d.streak ? "Study today to keep it" : "Study today to begin"}</small></div></div>
        <div class="days">${d.week.map((w, i) => `<span class="d ${w.active ? "on" : ""} ${i === 6 && !w.active ? "today" : ""}" title="${w.date}">${w.day[0]}</span>`).join("")}</div>
      </div>
      <div class="examday"><span>Exam day</span><button id="setExam">${ex ? `${fmtDate(ex)} · ${left >= 0 ? `${left} days left` : "done"}` : "Set your exam date"}</button></div>
    </aside>
    <main class="main"><div class="page ${cls}">${inner}</div></main>
  </div>`;
}
function wireShell() {
  const b = $("#setExam");
  if (b) b.onclick = async () => {
    const v = prompt("When is your exam? Type the date like 2026-12-15", S.dash.profile.exam_date || "");
    if (v === null) return;
    try { await api("/api/profile", { exam_date: v.trim() || null }); await refresh(); route(); } catch (e) { alert(e.message); }
  };
}

function stepDots(labRow, curKey) {
  const lab = S.labs.find((l) => l.id === labRow.id);
  const gs = lab.steps.filter(gated);
  return `<div class="dots" aria-label="Steps in this lab">${gs.map((s, i) => {
    const st = s.done ? "done" : s.key === curKey ? "now" : "lock";
    return `${i ? `<span class="dline ${s.done ? "done" : ""}"></span>` : ""}<span class="sdot ${st}" title="${esc(cleanTitle(s.title))}">${s.done ? ic("check", 14, 3) : i + 1}</span>`;
  }).join("")}</div>`;
}
function ringSvg(value, size = 170, r = 66, w = 16, color = "var(--primary)") {
  const c = 2 * Math.PI * r;
  return `<svg class="ring" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" role="img" aria-label="${value} percent">
    <circle cx="${size / 2}" cy="${size / 2}" r="${r}" fill="none" stroke="#EDF0F5" stroke-width="${w}"/>
    <circle class="fg" cx="${size / 2}" cy="${size / 2}" r="${r}" fill="none" stroke="${color}" stroke-width="${w}" stroke-linecap="round"
      stroke-dasharray="${c}" stroke-dashoffset="${c}" data-off="${c * (1 - value / 100)}" transform="rotate(-90 ${size / 2} ${size / 2})"/></svg>`;
}
function animateRings() { requestAnimationFrame(() => requestAnimationFrame(() => $$("circle.fg").forEach((c) => (c.style.strokeDashoffset = c.dataset.off)))); }

// ---------------------------------------------------------------- Today
function viewToday() {
  const d = S.dash, n = d.next_step;
  const h = new Date().getHours();
  const hello = h < 12 ? "Good morning" : h < 18 ? "Good afternoon" : "Good evening";
  const labRow = n && d.labs.find((l) => l.id === n.lab);
  const plan = [];
  if (n) plan.push([`#/lab/${n.lab}/${n.key}`, `Do lab step ${n.key}`, cleanTitle(n.title)]);
  if (d.due.today) plan.push(["#/practice/session?mode=due", `Review ${d.due.today} question${d.due.today > 1 ? "s" : ""}`, "They are due today. About 1 minute each."]);
  if (d.questions.new) plan.push(["#/practice/session?mode=new", "Try 10 new questions", `${d.questions.new} questions you have not seen yet`]);
  const weak = d.weak[0];
  const ws = d.weakest_section && d.weakest_section.pct < 70 ? d.weakest_section : null;
  const lastMock = d.mocks[0];
  const inner = `
    <header class="rise"><p class="eyebrow">${esc(new Date().toLocaleDateString(undefined, { weekday: "long", day: "numeric", month: "long" }))}</p>
      <h1 class="ptitle">${hello}! Let's keep going.</h1></header>
    <div class="row rise">
      <section class="card soft grow2" style="display:flex;flex-direction:column;gap:18px">
        ${n ? `<p class="eyebrow">Your next step · ${esc(labRow.label)}</p>
        <div><h2 style="font-size:26px;font-weight:600;letter-spacing:-.4px">${esc(cleanTitle(n.title))}</h2>
          <p class="lead" style="margin-top:6px">${esc(labRow.name)} — ${esc(LAB_META[n.lab].sub.toLowerCase())}. Step ${labRow.done + 1} of ${labRow.total}.</p></div>
        ${stepDots(labRow, n.key)}
        <div><a class="btn" href="#/lab/${n.lab}/${n.key}">Continue step ${esc(n.key)} ${ic("next", 18, 2.5)}</a></div>`
        : `<p class="eyebrow">All labs done</p><h2 class="h2">You finished every lab step. Great work!</h2><div><a class="btn" href="#/mock">Take a mock exam</a></div>`}
      </section>
      <section class="card grow1" style="display:flex;flex-direction:column;gap:12px">
        <h2 class="h2">Today's plan</h2>
        ${plan.map(([href, t, s], i) => `<a class="plan ${i === 0 ? "now" : ""}" href="${href}"><span class="n">${i + 1}</span><span class="t"><b>${esc(t)}</b><span>${esc(s)}</span></span></a>`).join("") || '<p class="muted">Nothing left for today.</p>'}
      </section>
    </div>
    <div class="stats rise">
      ${stat("Exam readiness", `${d.readiness}<small>%</small>`, d.readiness, "var(--primary)")}
      ${stat("Lab steps done", `${d.steps.done}<small> / ${d.steps.total}</small>`, pct(d.steps.done, d.steps.total))}
      ${stat("Questions tried", `${d.questions.tried}<small> / ${d.questions.total}</small>`, pct(d.questions.tried, d.questions.total))}
      ${stat("First-try right", d.questions.first_pct == null ? '—' : `${d.questions.first_pct}<small>%</small>`, d.questions.first_pct || 0, "var(--warm)")}
    </div>
    <section class="rise" style="display:flex;flex-direction:column;gap:14px">
      <div style="display:flex;justify-content:space-between;align-items:baseline"><h2 class="h2">Your lab path</h2><a href="#/labs" style="font-size:14px">See all labs</a></div>
      <div class="path"><div>${d.labs.map((l) => {
        const st = l.done === l.total ? "done" : n && n.lab === l.id ? "now" : "";
        return `<a class="labtile ${st}" href="#/lab/${l.id}/${l.next || l.steps[0].key}"><span class="tag">${esc(l.label.toUpperCase())}${st === "done" ? " · DONE" : ""}</span><b>${esc(l.name)}</b><span>${l.done}/${l.total} steps · ${LAB_META[l.id].sec}</span>
          <div class="bar"><div style="width:${pct(l.done, l.total)}%"></div></div></a>`;
      }).join("")}</div></div>
    </section>
    <div class="row rise">
      <div class="mini"><span class="ic" style="background:#FFF1E0;color:var(--warm-btn)">${ic("target", 22)}</span><div>
        <h3>${weak ? `Weak spot: ${esc(weak.title)}` : ws ? `Weakest section: ${esc(ws.name)}` : "No weak spots yet"}</h3>
        <p>${weak ? `You got ${weak.right} of ${weak.tried} right. Practise this topic, then try its lab.` : ws ? `${ws.pct}% right so far. A short practice set will help.` : "Answer a few practice questions and your weak spots show up here."}</p>
        <div>${weak ? `<a class="ghost" href="#/practice/session?mode=topic&id=${weak.id}">Practise this topic</a>` : `<a class="ghost" href="#/practice">Open practice</a>`}</div></div></div>
      <div class="mini"><span class="ic" style="background:var(--primary-soft);color:var(--primary)">${ic("clock", 22)}</span><div>
        <h3>${d.active_mock ? "You have a mock exam in progress" : lastMock ? `Last mock exam: ${pct(lastMock.correct, lastMock.total)}%` : "Try a mock exam"}</h3>
        <p>${d.active_mock ? "The timer keeps running. Finish it to see your results." : "45 questions in 90 minutes, mixed like the real exam."}</p>
        <div><a class="ghost" href="${d.active_mock ? `#/mock/exam/${d.active_mock}` : "#/mock"}">${d.active_mock ? "Continue the mock exam" : "Open mock exam"}</a></div></div></div>
    </div>`;
  return shell("today", inner);
}
function stat(k, v, p, color = "var(--ok)") {
  return `<div class="stat"><span class="k">${k}</span><span class="v">${v}</span><div class="bar"><div style="width:${p}%;background:${color}"></div></div></div>`;
}

// ---------------------------------------------------------------- Labs
function viewLabs() {
  const d = S.dash, n = d.next_step;
  const inner = `<header class="rise"><h1 class="ptitle">Labs</h1><p class="lead" style="margin-top:8px">Nine hands-on labs. Each step: read a short lesson, fill in the code, check it, answer one exam question.</p></header>
  <ol class="labslist rise">${d.labs.map((l) => {
    const lab = S.labs.find((x) => x.id === l.id);
    const done = l.done === l.total, now = n && n.lab === l.id;
    const ball = done ? `<span class="ball done pop">${ic("check", 22, 3, "icon")}</span>` : `<span class="ball ${now ? "now" : "todo"}">${labNo(l.id)}</span>`;
    const info = `<div class="info"><span class="tag ${done ? "done" : now ? "now" : ""}">${esc(l.label.toUpperCase())} · ${LAB_META[l.id].sec.toUpperCase()}${done ? " · DONE" : now ? " · NOW" : ""}</span>
      <span class="name">${esc(l.name)}</span><span class="sub">${esc(LAB_META[l.id].sub)} · ${l.done} of ${l.total} steps</span></div>`;
    const open = `<a class="${now ? "btn" : "ghost"}" href="#/lab/${l.id}/${l.next || l.steps[0].key}">${done ? "Look again" : now ? `Continue step ${esc(l.next)}` : l.done ? "Continue" : "Start lab"}</a>`;
    const body = now ? `<div style="display:flex;flex-wrap:wrap;gap:16px;align-items:center;justify-content:space-between">${info}${open}</div>
      <div class="bar"><div style="width:${pct(l.done, l.total)}%"></div></div>
      <ul class="stepgrid">${lab.steps.map((s, i) => {
        const st = stepState(lab, i, l.next);
        const lbl = `${st === "done" ? ic("check", 14, 3) : st === "lock" ? ic("lock", 14, 2) : ""}<span>${esc(s.type === "info" ? "Wrap-up" : s.key)} · ${esc(cleanTitle(s.title))}</span>`;
        return `<li>${st === "lock" ? `<span class="lock">${lbl}</span>` : `<a class="${st}" href="#/lab/${l.id}/${s.key}">${lbl}</a>`}</li>`;
      }).join("")}</ul>` : `${info}${open}`;
    return `<li><div class="rail">${ball}<span class="stem ${done ? "done" : ""}"></span></div><div class="labcard ${now ? "now" : ""}">${body}</div></li>`;
  }).join("")}</ol>`;
  return shell("labs", inner, "narrow");
}

// ---------------------------------------------------------------- Lab step
const GAP_RE = /<FILL-IN(?: (\d+))?>/g;
function hl(text) {
  // light syntax colours for the gap editor (comments, strings, a few keywords)
  return text.split(/(#.*$|"[^"\n]*"|'[^'\n]*'|\b(?:SELECT|FROM|CREATE|OR|REPLACE|TABLE|VIEW|AS|WHERE|GROUP|BY|ORDER|JOIN|ON|MERGE|INTO|USING|WHEN|MATCHED|NOT|THEN|INSERT|UPDATE|DELETE|SET|GRANT|REVOKE|TO|COPY|FILEFORMAT|LOCATION|def|return|import|from|for|in|if|else|with|lambda|True|False|None)\b)/m)
    .map((p, i) => !p ? "" : i % 2 === 0 ? esc(p) : p[0] === "#" ? `<span class="cm">${esc(p)}</span>` : /^["']/.test(p) ? `<span class="st">${esc(p)}</span>` : `<span class="kw">${esc(p)}</span>`).join("");
}
function gapEditor(starter, saved) {
  let g = 0;
  const lines = starter.split("\n");
  return lines.map((line, li) => {
    const parts = [];
    let last = 0, m;
    GAP_RE.lastIndex = 0;
    while ((m = GAP_RE.exec(line))) {
      parts.push(hl(line.slice(last, m.index)));
      const val = saved[g] ?? "";
      const num = m[1] || g + 1;
      parts.push(`<span class="gapw"><span class="gapn">${num}</span><textarea class="gap" data-g="${g}" rows="1" spellcheck="false" aria-label="Gap ${num}" placeholder="type here">${esc(val)}</textarea></span>`);
      g++;
      last = m.index + m[0].length;
    }
    parts.push(hl(line.slice(last)));
    return `<div class="cl"><span class="ln">${li + 1}</span><span class="tx">${parts.join("")}</span></div>`;
  }).join("");
}
function growGap(t) {
  const lines = t.value.split("\n");
  t.rows = Math.max(1, lines.length);
  t.style.width = `${Math.max(14, Math.max(...lines.map((l) => l.length)) + 3)}ch`;
}
function fillCode(starter) {
  const vals = $$("textarea.gap").map((t) => t.value);
  let g = 0;
  return starter.replace(GAP_RE, () => vals[g++] ?? "");
}
function alignSolution(starter, solution) {
  // read the gap values out of the solution. Comment lines, inline "  # notes" and spacing
  // differ between starter and solution, so they are ignored when matching.
  const clean = (t) => t.split("\n").filter((l) => !/^\s*#/.test(l)).map((l) => l.replace(/\s{2,}#.*$/, "").trimEnd()).join("\n").trim();
  const pieces = clean(starter).split(GAP_RE).filter((_, i) => i % 2 === 0);
  const lit = (p) => p.split(/\s+/).map((w) => w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("\\s*");
  const rx = new RegExp("^" + pieces.map(lit).join("([\\s\\S]*?)") + "$");
  const m = clean(solution).match(rx);
  return m ? m.slice(1).map((v) => v.trim()) : null;
}

let LAB = null;  // { lab, step, idx }
async function viewLabStep(labId, key) {
  const lab = S.labs.find((l) => l.id === labId);
  if (!lab) return (location.hash = "#/labs");
  let i = lab.steps.findIndex((s) => s.key === key);
  if (i < 0 || !unlocked(lab, i)) {
    i = lab.steps.findIndex((s, j) => !s.done && unlocked(lab, j));
    if (i < 0) i = 0;
    history.replaceState(null, "", `#/lab/${labId}/${lab.steps[i].key}`);
  }
  const s = lab.steps[i];
  LAB = { lab, step: s, idx: i };
  store.set("last-step", [labId, s.key]);
  $("#app").innerHTML = labStepHtml(lab, s, i);
  wireLabStep(lab, s);
  busy("Preparing this step… (the first time Spark starts it takes about 30 seconds)");
  try {
    const r = await api("/api/open", { lab: lab.id, step: s.key });
    if (r.error) termShow([], r.error, "Setup error");
    else if (r.prep && (r.prep.outputs.length || r.prep.error)) termShow(r.prep.outputs, r.prep.error, "Setup output (ran for you)");
  } catch (e) { termShow([], { ename: "Error", evalue: e.message }, "Setup error"); }
  idle();
}

function pillsHtml(lab, s) {
  return lab.steps.map((x, j) => {
    const st = stepState(lab, j, s.key);
    const inner = `<span class="b">${st === "done" ? ic("check", 13, 3, "") : st === "lock" ? "" : x.type === "info" ? "★" : j + 1}</span><span class="lbl">${esc(x.type === "info" ? "Wrap-up" : x.key)}</span>`;
    return st === "lock" ? `<span class="spill lock" title="Finish the earlier steps first">${inner}</span>` : `<a class="spill ${st}" href="#/lab/${lab.id}/${x.key}" title="${esc(cleanTitle(x.title))}">${inner}</a>`;
  }).join("");
}

function labStepHtml(lab, s, i) {
  const L = s.lesson, V = s.visual;
  const tabs = [];
  if (V) tabs.push(["idea", "The idea"]);
  if (L || s.explain.trim()) tabs.push(["words", "In plain words"]);
  if (V && V.slides && V.slides.length) tabs.push(["slides", "Course slides"]);
  if (L && s.explain.trim()) tabs.push(["real", "On real Databricks"]);
  const tab0 = store.get("learn-tab", "idea");
  const first = tabs.find((t) => t[0] === tab0) ? tab0 : (tabs[0] || [""])[0];
  const isFile = s.type === "file", isInfo = s.type === "info";
  const hasGaps = !isFile && GAP_RE.test(s.starter);
  GAP_RE.lastIndex = 0;
  S.gapMode = hasGaps && !store.get(`full:${lab.id}:${s.key}`, false);
  return `<div style="min-height:100vh;background:var(--ground)">
  <header class="topbar">
    <a class="ghost flat" href="#/labs">${ic("back")} Labs</a>
    <div class="ttl"><span>${esc(lab.label)} · ${esc(lab.name)}</span><b>Step ${i + 1} of ${lab.steps.length}</b></div>
    <nav class="stepnav" id="pills" aria-label="Steps">${pillsHtml(lab, s)}</nav>
  </header>
  <div class="steparea"><div>
    <section class="learn rise" aria-label="Learn">
      <div style="display:flex;flex-direction:column;gap:8px"><p class="eyebrow">Learn first · ${esc(s.key)}</p><h1>${esc(cleanTitle(s.title))}</h1></div>
      ${tabs.length > 1 ? `<div class="tabs" role="tablist">${tabs.map(([id, t]) => `<button class="tab ${id === first ? "on" : ""}" role="tab" data-tab="${id}">${t}</button>`).join("")}</div>` : ""}
      <div id="tabbody">${learnTab(s, first)}</div>
    </section>
    <section class="do rise" aria-label="Your turn">
      <div class="docard">
        <div class="dohead"><h2>${isInfo ? "Wrap-up" : "Your turn"}</h2>
          ${isInfo ? "" : `<div style="display:flex;gap:8px;flex-wrap:wrap"><button class="ghost" id="solBtn">${ic("eye")} Show solution</button><button class="ghost" id="resetBtn">${ic("reset")} Start over</button></div>`}</div>
        ${L && !isInfo ? `<details class="guide" open><summary>What to type</summary><div class="md">${md(L.do)}</div></details>` : ""}
        ${s.prep && !isInfo ? `<details class="guide"><summary>Setup code (already ran for you)</summary><div class="md"><pre><code>${esc(s.prep)}</code></pre></div></details>` : ""}
        <div class="editor"><div class="edhead"><span>${isFile ? esc(s.file) : isInfo ? "demo code" : "your code"}${hasGaps && S.gapMode ? " · fill the dashed boxes" : ""}</span>
          ${hasGaps ? `<button id="modeBtn">${S.gapMode ? "Edit the whole code" : "Back to the boxes"}</button>` : ""}</div>
          <div id="edHost"></div>
          <div class="edfoot">${isFile ? `<span>Saving writes the file, then runs the tests.</span>` : `<button class="run" id="runBtn">${ic("play", 14, 2)} Run</button><span>Run shows the output. Check also tests it.</span>`}</div></div>
        <div class="term" id="term" aria-live="polite"><div class="lbl">OUTPUT</div><pre class="idle">Press Run to see the output here.</pre></div>
        <div class="checkrow"><button class="btn" id="checkBtn">${isInfo ? "Mark as done" : isFile ? "Save and check" : "Check my answer"}</button><span class="hintline" id="hint"></span></div>
        <div id="result"></div>
        <div id="solution"></div>
      </div>
      ${s.after && !isInfo ? `<details class="guide"><summary>What runs after your code when you check</summary><div class="md"><pre><code>${esc(s.after)}</code></pre></div></details>` : ""}
      <div id="afterArea"></div>
    </section>
  </div></div></div>`;
}

function learnTab(s, tab) {
  const L = s.lesson, V = s.visual;
  if (tab === "idea" && V) return `<div style="display:flex;flex-direction:column;gap:18px">
    <div class="think">${ic("bulb", 26, 2)}<div><b>Think of it like this</b><div class="md">${md(V.analogy)}</div></div></div>
    ${V.diagram ? `<figure class="diagram" style="margin:0"><pre class="mermaid">${esc(V.diagram)}</pre><figcaption>How the data flows</figcaption></figure>` : ""}</div>`;
  if (tab === "words") return `<div class="md">${md(L ? L.read : s.explain)}</div>`;
  if (tab === "real") return `<div class="md">${md(s.explain)}</div>`;
  if (tab === "slides" && V) {
    const at = 0, [c, n, cap] = V.slides[at];
    return `<div class="slideview" data-at="0"><img src="/slides/${c}/${n}.jpg" alt="${esc(cap)}" id="slideImg">
      <div class="cap" id="slideCap">${esc(cap)} · Course ${c.slice(1)}, slide ${n}</div>
      <div class="nav2"><button class="ghost" id="slPrev">${ic("back")} Previous</button><span id="slCount">1 of ${V.slides.length}</span><button class="ghost" id="slNext">Next ${ic("next")}</button></div></div>`;
  }
  return "";
}
function drawMermaid() {
  if (!window.mermaid || !$(".mermaid")) return;
  (document.fonts ? document.fonts.ready : Promise.resolve()).then(() => { try { mermaid.run({ querySelector: ".mermaid" }); } catch {} });
}
function wireLearn(s) {
  drawMermaid();
  const V = s.visual;
  const img = $("#slideImg");
  if (img) {
    let at = 0;
    const show = () => { const [c, n, cap] = V.slides[at]; img.src = `/slides/${c}/${n}.jpg`; img.alt = cap; $("#slideCap").textContent = `${cap} · Course ${c.slice(1)}, slide ${n}`; $("#slCount").textContent = `${at + 1} of ${V.slides.length}`; };
    $("#slPrev").onclick = () => { at = (at - 1 + V.slides.length) % V.slides.length; show(); };
    $("#slNext").onclick = () => { at = (at + 1) % V.slides.length; show(); };
    img.onclick = () => { const lb = $("#lightbox"); $("img", lb).src = img.src; $("p", lb).textContent = img.alt; lb.hidden = false; };
  }
}

function mountEditor(lab, s, code) {
  const host = $("#edHost");
  const key = `${lab.id}:${s.key}`;
  if (S.gapMode) {
    host.innerHTML = `<div class="codebody">${gapEditor(s.starter, store.get(`gaps:${key}`, []))}</div>`;
    S.editor = null;
    $$("textarea.gap", host).forEach((t) => {
      growGap(t);
      t.oninput = () => { growGap(t); t.classList.remove("ok", "bad"); store.set(`gaps:${key}`, $$("textarea.gap").map((x) => x.value)); };
      t.onkeydown = (e) => {
        if ((e.metaKey || e.ctrlKey) && e.key === "Enter") { e.preventDefault(); runCode(); }
        else if (e.key === "Tab") {
          const all = $$("textarea.gap"), k = all.indexOf(t) + (e.shiftKey ? -1 : 1);
          if (all[k]) { e.preventDefault(); all[k].focus(); }
        }
      };
    });
    return;
  }
  const start = code ?? store.get(`code:${key}`, null) ?? s.starter;
  host.innerHTML = '<div class="fulled"></div>';
  if (window.CodeMirror) {
    S.editor = CodeMirror($(".fulled", host), { value: start, theme: "material-darker", mode: (s.file || "").endsWith(".yml") ? "yaml" : "python",
      lineNumbers: true, indentUnit: 4, viewportMargin: Infinity, readOnly: s.type === "info" ? "nocursor" : false,
      extraKeys: { "Ctrl-Enter": runCode, "Cmd-Enter": runCode, Tab: (cm) => cm.replaceSelection("    ") } });
    S.editor.on("change", () => store.set(`code:${key}`, S.editor.getValue()));
  } else {
    $(".fulled", host).innerHTML = `<textarea style="width:100%;min-height:260px;background:var(--code);color:#fff;font-family:var(--mono);border:0;padding:14px">${esc(start)}</textarea>`;
    const ta = $("textarea", host);
    S.editor = { getValue: () => ta.value, setValue: (v) => (ta.value = v), refresh() {} };
  }
}
const currentCode = () => (S.gapMode ? fillCode(LAB.step.starter) : S.editor.getValue());

function wireLabStep(lab, s) {
  wireLearn(s);
  $$(".tab").forEach((b) => (b.onclick = () => {
    $$(".tab").forEach((x) => x.classList.toggle("on", x === b));
    store.set("learn-tab", b.dataset.tab);
    $("#tabbody").innerHTML = learnTab(s, b.dataset.tab);
    wireLearn(s);
  }));
  mountEditor(lab, s);
  $("#runBtn") && ($("#runBtn").onclick = runCode);
  $("#checkBtn").onclick = checkCode;
  $("#solBtn") && ($("#solBtn").onclick = showSolution);
  $("#modeBtn") && ($("#modeBtn").onclick = () => {
    const code = currentCode();
    S.gapMode = !S.gapMode;
    store.set(`full:${lab.id}:${s.key}`, !S.gapMode);
    if (!S.gapMode) store.set(`code:${lab.id}:${s.key}`, code);
    $("#modeBtn").textContent = S.gapMode ? "Edit the whole code" : "Back to the boxes";
    mountEditor(lab, s, S.gapMode ? undefined : code);
  });
  $("#resetBtn") && ($("#resetBtn").onclick = () => {
    if (!confirm("Clear your answers for this step and start over?")) return;
    store.del(`gaps:${lab.id}:${s.key}`); store.del(`code:${lab.id}:${s.key}`); store.del(`full:${lab.id}:${s.key}`);
    S.gapMode = GAP_RE.test(s.starter) && s.type !== "file"; GAP_RE.lastIndex = 0;
    mountEditor(lab, s, s.starter);
    $("#result").innerHTML = ""; $("#solution").innerHTML = ""; $("#hint").textContent = "";
  });
  if (s.done) afterPass(true);
}

function termShow(outputs, error, label = "OUTPUT") {
  const parts = (outputs || []).map((o) => (o.type === "html" ? `<div class="html">${o.html}</div>` : `<pre>${esc(o.text)}</pre>`));
  if (error) {
    const tb = (error.traceback || "").split("\n").filter((l) => !/site-packages|py4j|^\s*$/.test(l)).slice(-10).join("\n");
    parts.push(`<pre class="err">${esc(error.ename)}: ${esc(error.evalue)}${tb ? "\n\n" + esc(tb) : ""}</pre>`);
  }
  if (!parts.length) parts.push('<pre class="okc">Done — no output.</pre>');
  $("#term").innerHTML = `<div class="lbl">${esc(label)}</div>${parts.join("")}`;
}
function emptyGap() {
  if (!S.gapMode) return /<FILL-IN/.test(S.editor.getValue()) ? "There is still a <FILL-IN> in your code. Replace it first." : null;
  const t = $$("textarea.gap").find((x) => !x.value.trim());
  if (!t) return null;
  t.focus(); t.classList.add("bad"); setTimeout(() => t.classList.remove("bad"), 400);
  return `Box ${t.closest(".gapw").querySelector(".gapn").textContent} is still empty.`;
}
async function runCode() {
  if (!LAB || LAB.step.type === "file") return;
  busy("Running your code…");
  try { const r = await api("/api/run", { lab: LAB.lab.id, code: currentCode() }); termShow(r.outputs, r.error); }
  catch (e) { termShow([], { ename: "Error", evalue: e.message }); }
  idle();
}
async function checkCode() {
  const { lab, step: s } = LAB;
  const hint = $("#hint");
  if (s.type !== "info") {
    const miss = emptyGap();
    if (miss) { hint.className = "hintline bad"; hint.textContent = miss; return; }
  }
  hint.className = "hintline"; hint.textContent = "";
  busy(s.type === "file" ? "Saving and running the tests… (about 30 seconds)" : s.type === "info" ? "Saving…" : "Checking your answer…");
  try {
    const r = await api("/api/check", { lab: lab.id, step: s.key, code: s.type === "info" ? "" : currentCode() });
    if (s.type !== "info") termShow(r.outputs, r.error);
    if (r.passed) {
      $$("textarea.gap").forEach((t) => t.classList.add("ok"));
      s.done = true;
      $("#pills").innerHTML = pillsHtml(lab, s);
      $("#result").innerHTML = `<div class="banner ok rise"><span class="ball pop">${ic("check", 26, 3, "")}</span><div><b>${s.type === "info" ? "Marked as done" : "Nice — it works!"}</b><span>${s.type === "info" ? "On to the next part." : "Your answer passed the check."}</span></div></div>`;
      $("#result .ball svg").style.color = "#fff";
      refresh().catch(() => {});
      afterPass(false);
    } else {
      $("#result").innerHTML = `<div class="banner bad rise"><span class="ball">${ic("x", 20, 3, "")}</span><div><b>Not quite</b><span>Read the message, change your code, and check again.</span></div></div>
        ${r.message ? `<div class="msg" style="margin-top:10px">${esc(r.message)}</div>` : ""}`;
      $("#result .ball svg").style.color = "#fff";
    }
  } catch (e) { $("#result").innerHTML = `<div class="msg">${esc(e.message)}</div>`; }
  idle();
}
async function showSolution() {
  const { lab, step: s } = LAB;
  if (!confirm("Try it yourself first! Show the solution anyway?")) return;
  const r = await api("/api/solution", { lab: lab.id, step: s.key });
  if (S.gapMode) {
    const vals = alignSolution(s.starter, r.code);
    if (vals) {
      $$("textarea.gap").forEach((t, k) => { t.value = vals[k]; growGap(t); t.classList.remove("bad"); });
      store.set(`gaps:${lab.id}:${s.key}`, vals);
      $("#solution").innerHTML = `<p class="hintline">${ic("eye")} The boxes now hold the solution. Read each line and make sure you know <b>why</b> — then press Check.</p>`;
      return;
    }
  }
  $("#solution").innerHTML = `<div class="guide" style="background:var(--ground);border-radius:16px;padding:14px 16px"><b>Solution</b><div class="md"><pre><code>${esc(r.code)}</code></pre></div>
    <button class="ghost" id="useSol">Put it in the editor</button></div>`;
  $("#useSol").onclick = () => {
    if (S.gapMode) { S.gapMode = false; store.set(`full:${lab.id}:${s.key}`, true); if ($("#modeBtn")) $("#modeBtn").textContent = "Back to the boxes"; }
    mountEditor(lab, s, r.code); store.set(`code:${lab.id}:${s.key}`, r.code);
  };
}

function nextLink() {
  const { lab, idx } = LAB;
  const nx = lab.steps[idx + 1];
  if (nx) return `<a class="btn green" href="#/lab/${lab.id}/${nx.key}">Next step ${ic("next", 18, 2.5)}</a>`;
  const li = S.labs.indexOf(lab), nl = S.labs[li + 1];
  return nl ? `<a class="btn green" href="#/lab/${nl.id}/${nl.steps[0].key}">Lab finished — start ${esc(nl.label)} ${ic("next", 18, 2.5)}</a>` : `<a class="btn green" href="#/mock">Every lab done — try a mock exam</a>`;
}
function afterPass(already) {
  const s = LAB.step, Q = s.learn;
  const last = !!s.check || s.type === "info";
  const area = $("#afterArea");
  if (!Q || !last) { area.innerHTML = `<div class="nextbar rise"><span class="l">${ic("check", 18, 3)} Step done</span>${nextLink()}</div>`; return; }
  area.innerHTML = `<div class="docard rise">
    <p class="eyebrow">Exam check · one question</p>
    <div class="md">${md(Q.q)}</div>
    <div class="opts">${Q.opts.map((o, k) => `<button class="opt" data-k="${k}"><span class="k">${"ABCD"[k]}</span><span class="t">${mdi(o)}</span><span class="tag"></span></button>`).join("")}</div>
    <div id="qfb"></div></div><div id="nextArea"></div>`;
  const done = () => { $("#nextArea").innerHTML = `<div class="nextbar rise" style="margin-top:4px"><span class="l">Step ${esc(s.key)} complete</span>${nextLink()}</div>`; };
  $$("#afterArea .opt").forEach((b) => (b.onclick = async () => {
    const r = await api("/api/answer", { lab: LAB.lab.id, gid: s.gid, choice: +b.dataset.k });
    $$("#afterArea .opt").forEach((x) => (x.disabled = true));
    const right = $(`#afterArea .opt[data-k="${r.answer}"]`);
    right.classList.add("right"); $(".tag", right).textContent = "Right answer";
    if (!r.correct) { b.classList.add("wrong"); $(".tag", b).textContent = "Your pick"; }
    $("#qfb").innerHTML = `<div class="explain rise" style="margin-top:12px"><div><h2 style="color:${r.correct ? "var(--ok-text)" : "var(--bad-text)"}">${r.correct ? "Right!" : "Not quite"}</h2><div class="md">${md(r.explain)}</div></div>
      <div class="sep"></div><div><h2 class="muted">How it works</h2><div class="md">${md(Q.why)}</div></div></div>`;
    s.quiz_done = true;
    done();
  }));
  if (already && s.quiz_done) done();
}

// ---------------------------------------------------------------- Practice home
async function viewPractice() {
  const [cat] = await Promise.all([api("/api/exam/sections")]);
  S.catalog = cat;
  const d = S.dash, due = d.due;
  const total = due.today + due.tomorrow + due.week || 1;
  const inner = `<header class="rise"><h1 class="ptitle">Practice</h1><p class="lead" style="margin-top:8px">${d.questions.total} practice questions, each with a plain-words explanation. Questions you miss come back sooner.</p></header>
  <div class="row rise">
    <section class="duecard">
      <span class="eb">Review due today</span>
      <h2 style="font-size:28px;font-weight:600">${due.today ? `${due.today} question${due.today > 1 ? "s" : ""} to review` : "Nothing due right now"}</h2>
      <p>${due.today ? "These come back because the right moment to remember them is now." : "Answer new questions and they will come back here on the right day."}</p>
      <div class="duebars" aria-hidden="true"><span style="flex:${due.today || 0.01};background:var(--warm)"></span><span style="flex:${due.tomorrow || 0.01};background:#FFC48A"></span><span style="flex:${due.week || 0.01};background:#FFE0BF"></span></div>
      <div class="legend"><span><i style="background:var(--warm)"></i>Today ${due.today}</span><span><i style="background:#FFC48A"></i>Tomorrow ${due.tomorrow}</span><span><i style="background:#FFE0BF"></i>This week ${due.week}</span></div>
      <div>${due.today ? `<a class="btn warm" href="#/practice/session?mode=due">Start review</a>` : `<a class="btn warm" href="#/practice/session?mode=new">Try 10 new questions</a>`}</div>
    </section>
    <section class="card grow1" style="display:flex;flex-direction:column;gap:10px;padding:24px">
      <h2 class="h2">Quick practice</h2>
      <a class="quick first" href="#/practice/session?mode=new"><span><b>10 new questions</b><small>${d.questions.new} not seen yet</small></span>${ic("next")}</a>
      <a class="quick" href="#/practice/session?mode=mixed"><span><b>10 mixed questions</b><small>From every section</small></span>${ic("next")}</a>
      <a class="quick" href="#/practice/session?mode=weak"><span><b>My mistakes</b><small>Questions whose last answer was wrong</small></span>${ic("next")}</a>
    </section>
  </div>
  <section class="rise" style="display:flex;flex-direction:column;gap:12px">
    <div style="display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:8px"><h2 class="h2">By exam section</h2><span class="muted" style="font-size:13px">Open a section to pick one idea</span></div>
    ${cat.sections.map((s) => {
      const topics = d.topics.filter((t) => t.section === s.id);
      return `<details class="sec"><summary>
        <span class="secn">${s.id}</span>
        <span style="flex:1 1 240px;display:flex;flex-direction:column;gap:2px"><b style="font-size:16px;font-weight:600">${esc(s.name)}</b><span class="muted" style="font-size:13px">${s.weight}% of the exam · ${s.count} questions · ${s.attempted} tried${s.due ? ` · ${s.due} due` : ""}</span></span>
        <span style="flex:0 1 180px"><div class="bar"><div style="width:${pct(s.attempted, s.count)}%"></div></div></span>
        <span style="display:flex;gap:8px;flex-wrap:wrap"><a class="btn" style="min-height:44px;font-size:14px;padding:0 16px" href="#/learn/${s.id}" onclick="event.stopPropagation()">Learn first</a><a class="ghost" href="#/practice/session?mode=section&id=${s.id}" onclick="event.stopPropagation()">Practise only</a></span>
      </summary><div class="secbody">${topics.map((t) => `<a class="chip" href="#/practice/session?mode=topic&id=${t.id}"><span class="dot" style="background:${!t.tried ? "#D7DCE6" : t.right / t.tried >= 0.7 ? "var(--ok)" : "var(--warm)"}"></span>${esc(t.title)} <span class="muted">${t.tried}/${t.total}</span></a>`).join("")}</div></details>`;
    }).join("")}
  </section>`;
  return shell("practice", inner, "mid");
}

// ---------------------------------------------------------------- Learn a section (notes first)
function conceptBody(c) {
  return `<div style="display:flex;flex-direction:column;gap:16px;margin-top:12px">
    <div class="think">${ic("bulb", 26, 2)}<div><b>Think of it like this</b><div class="md">${md(c.analogy)}</div></div></div>
    <div><h3 class="h3">What you must know</h3><ol class="facts">${c.facts.map(([t, b]) => `<li><b>${mdi(t)}</b><div class="md">${md(b)}</div></li>`).join("")}</ol></div>
    ${c.table ? `<div class="md">${md(c.table)}</div>` : ""}
    ${c.traps.length ? `<div class="caution">${ic("warn", 22, 2)}<div><b>Exam traps</b><div class="md"><ul>${c.traps.map((t) => `<li>${mdi(t)}</li>`).join("")}</ul></div></div></div>` : ""}
    ${c.slides.length ? `<div><h3 class="h3">From your course slides</h3><div class="thumbs">${c.slides.map(([k, n, cap]) => `<figure data-src="/slides/${k}/${n}.jpg" data-cap="${esc(cap)}"><img loading="lazy" src="/slides/${k}/${n}.jpg" alt="${esc(cap)}"><figcaption>${esc(cap)}<br><small>Course ${k.slice(1)}, slide ${n}</small></figcaption></figure>`).join("")}</div></div>` : ""}
    <p class="muted" style="margin:0;font-size:13px">Source: ${esc(c.source)}</p>
  </div>`;
}
function wireThumbs() {
  $$(".thumbs figure").forEach((f) => (f.onclick = () => { const lb = $("#lightbox"); $("img", lb).src = f.dataset.src; $("p", lb).textContent = f.dataset.cap; lb.hidden = false; }));
}
async function viewLearn(sec) {
  const L = await api(`/api/learn?section=${sec}`);
  const d = S.dash;
  const head = `<a class="ghost flat" href="#/practice" style="align-self:flex-start">${ic("back")} Practice</a>
    <header class="rise"><p class="eyebrow">Section ${L.id} · ${L.weight}% of the exam · ${L.count} practice questions</p><h1 class="ptitle" style="margin-top:6px">${esc(L.name)}</h1></header>`;
  if (!L.ready) return shell("practice", `${head}<section class="card"><h2 class="h2">Notes for this section are being written</h2><p class="lead" style="margin-top:8px">You can still practise its ${L.count} questions — every answer has a full explanation.</p><p><a class="btn" href="#/practice/session?mode=section&id=${L.id}">Practise section ${L.id}</a></p></section>`, "narrow");
  const pos = store.get(`guided:#/practice/session?mode=guided&id=${L.id}`, 0);
  const inner = `${head}
    <section class="card rise"><div class="md" style="font-size:17px">${md(L.intro)}</div>
      <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:16px"><a class="btn" href="#/practice/session?mode=guided&id=${L.id}">${pos ? `Continue guided questions (${pos + 1} of ${L.count})` : `Start guided questions (all ${L.count})`} ${ic("next", 18, 2.5)}</a></div></section>
    ${L.concepts.map((c, k) => {
      const t = d.topics.find((x) => x.id === c.topic) || { tried: 0, right: 0 };
      return `<details class="sec concept rise" ${k === 0 ? "open" : ""}><summary>
        <span class="secn">${k + 1}</span>
        <span style="flex:1 1 300px;display:flex;flex-direction:column;gap:2px"><b style="font-size:18px;font-weight:600">${esc(c.title)}</b><span class="muted" style="font-size:14px">${esc(c.one_line)}</span></span>
        <span class="chippill">${c.count} questions · ${t.tried} tried</span>
      </summary><div style="padding:0 22px 22px">${conceptBody(c)}
        <div style="margin-top:16px"><a class="btn green" href="#/practice/session?mode=guided&id=${L.id}&topic=${c.topic}">Guided questions on this idea (${c.count}) ${ic("next", 18, 2.5)}</a></div></div></details>`;
    }).join("")}`;
  setTimeout(wireThumbs, 0);
  return shell("practice", inner, "narrow");
}

// ---------------------------------------------------------------- Practice session (question screen)
async function startSession(q) {
  const all = await bank();
  const t = todayISO();
  const mode = q.get("mode"), id = q.get("id");
  let list = [], title = "Practice";
  if (mode === "due") { list = all.filter((x) => x.attempt && x.attempt.next_review <= t); title = "Review due today"; }
  else if (mode === "section") { const sec = all.filter((x) => String(x.section) === id); list = [...sec.filter((x) => !x.attempt), ...sec.filter((x) => x.attempt)]; title = `Section ${id} · ${SEC_SHORT[id]}`; }
  else if (mode === "topic") { const tp = all.filter((x) => x.topic === id); list = [...tp.filter((x) => !x.attempt), ...tp.filter((x) => x.attempt)]; title = (tp[0] && tp[0].topic_title) || "Topic"; }
  else if (mode === "new") { list = all.filter((x) => !x.attempt).slice(0, 10); title = "10 new questions"; }
  else if (mode === "mixed") { list = shuffle(all).slice(0, 10); title = "10 mixed questions"; }
  else if (mode === "weak") { list = all.filter((x) => x.attempt && !x.attempt.correct); title = "My mistakes"; }
  else if (mode === "guided") {
    const L = await api(`/api/learn?section=${id}`);
    const byId = Object.fromEntries(all.map((x) => [x.id, x]));
    list = L.order.map((k) => byId[k]).filter((x) => x && (!q.get("topic") || x.topic === q.get("topic")));
    const c = q.get("topic") && L.concepts.find((k) => k.topic === q.get("topic"));
    title = c ? `Learn: ${c.title}` : `Learn section ${id} · ${SEC_SHORT[id]}`;
    S.sess = { key: location.hash, list, i: 0, res: [], title, sel: new Set(), result: null, guided: L, back: `#/learn/${id}` };
    const at = store.get(`guided:${location.hash}`, 0);
    S.sess.i = Math.min(at, Math.max(0, list.length - 1));
    S.sess.res = list.slice(0, S.sess.i).map((x) => !!(x.attempt && x.attempt.correct));
    return;
  }
  else if (mode === "ids") { const ids = (id || "").split(","); list = ids.map((k) => all.find((x) => x.id === k)).filter(Boolean); title = "Review mock exam mistakes"; }
  S.sess = { key: location.hash, list, i: 0, res: [], title, sel: new Set(), result: null };
}
async function viewSession(q) {
  if (!S.sess || S.sess.key !== location.hash) await startSession(q);
  const ss = S.sess;
  if (!ss.list.length) return shell("practice", `<a class="ghost flat" href="#/practice" style="align-self:flex-start">${ic("back")} Practice</a>
    <section class="card"><h2 class="h2">Nothing to show here</h2><p class="lead" style="margin-top:8px">There are no questions in this set right now.</p><p><a class="btn" href="#/practice/session?mode=new">Try 10 new questions</a></p></section>`, "narrow");
  if (ss.i >= ss.list.length) return sessionEnd();
  const x = ss.list[ss.i];
  const sec = S.dash.sections.find((s) => s.id === x.section);
  const pics = (x.images || []).map((src) => `<img class="qimg" src="${esc(src)}" alt="Original question ${x.number}">`).join("");
  const needPic = x.choices.some((c) => !String(c.text || "").trim());
  const inner = `
    <div style="display:flex;flex-wrap:wrap;align-items:center;gap:12px 20px">
      <a class="ghost flat" href="${ss.back || "#/practice"}">${ic("back")} ${ss.guided ? "Section notes" : "Practice"}</a>
      <span style="font-weight:600">${esc(ss.title)}</span>
      <div class="segs" aria-label="Progress">${ss.list.map((_, k) => `<span class="${k < ss.res.length ? (ss.res[k] ? "r" : "w") : k === ss.i ? "c" : ""}"></span>`).join("")}</div>
      <span class="muted" style="font-size:14px">Question ${ss.i + 1} of ${ss.list.length}</span>
    </div>
    ${ss.guided ? knowFirst(x) : ""}
    <section class="card rise" id="qcard" style="display:flex;flex-direction:column;gap:20px" ${ss.guided && !ss.revealed ? "hidden" : ""}>
      <div style="display:flex;flex-wrap:wrap;gap:8px"><span class="chippill blue">Section ${x.section} · ${esc(SEC_SHORT[x.section])}</span>${x.topic_title ? `<span class="chippill">${esc(x.topic_title)}</span>` : ""}<span class="chippill">Question ${esc(x.number)}</span>${x.attempt ? `<span class="chippill ${x.attempt.correct ? "" : "warm"}">Last time: ${x.attempt.correct ? "right" : "missed"}</span>` : ""}</div>
      <h1 class="qtitle">${esc(x.q)}</h1>
      ${pics ? `<details class="pic" ${needPic ? "open" : ""}><summary>See the original question picture (code and tables)</summary>${pics}</details>` : ""}
      <p class="muted" style="margin:0;font-size:14px">${x.multiple ? "Choose all the right answers." : "Choose one answer."}</p>
      <div class="opts" id="opts">${x.choices.map((c) => `<button class="opt" data-l="${esc(c.label)}" aria-pressed="false"><span class="k">${esc(c.label)}</span><span class="t">${esc(c.text || "See the picture above")}</span><span class="tag"></span></button>`).join("")}</div>
      <div class="checkrow" id="qcheck"><button class="btn" id="qBtn" disabled>Check my answer</button></div>
    </section>
    <div id="qfb"></div>`;
  setTimeout(() => wireQuestion(x, sec), 0);
  return shell("practice", inner, "narrow");
}
function knowFirst(x) {
  const ss = S.sess, L = ss.guided;
  const c = L.concepts.find((k) => k.topic === x.topic);
  const prev = ss.list[ss.i - 1];
  const newIdea = !prev || prev.topic !== x.topic;
  return `<section class="know rise">
    ${newIdea && c ? `<p class="eyebrow">New idea · ${esc(c.title)}</p>` : `<p class="eyebrow">Know this first</p>`}
    <div class="md" style="font-size:17px">${md(L.before[x.id] || "")}</div>
    ${c ? `<details class="guide"><summary>Re-read the full note: ${esc(c.title)}</summary>${conceptBody(c)}</details>` : ""}
    ${ss.revealed ? "" : `<div><button class="btn" id="reveal">Got it — show the question ${ic("next", 18, 2.5)}</button></div>`}
  </section>`;
}
function wireQuestion(x) {
  const ss = S.sess;
  ss.sel = new Set();
  if ($("#reveal")) $("#reveal").onclick = () => { ss.revealed = true; $("#reveal").parentElement.remove(); $("#qcard").hidden = false; $("#qcard").scrollIntoView({ behavior: "smooth", block: "start" }); };
  $$("#opts .opt").forEach((b) => (b.onclick = () => {
    if (ss.result) return;
    const l = b.dataset.l;
    if (!x.multiple) ss.sel.clear();
    ss.sel.has(l) ? ss.sel.delete(l) : ss.sel.add(l);
    $$("#opts .opt").forEach((o) => { const on = ss.sel.has(o.dataset.l); o.classList.toggle("sel", on); o.setAttribute("aria-pressed", on); });
    $("#qBtn").disabled = !ss.sel.size;
  }));
  $("#qBtn").onclick = async () => {
    $("#qBtn").disabled = true;
    try {
      const r = await api("/api/exam/answer", { id: x.id, choices: [...ss.sel] });
      ss.result = r;
      x.attempt = { correct: r.correct, next_review: r.next_review };
      ss.res.push(r.correct);
      showFeedback(x, r);
      refresh().catch(() => {});
    } catch (e) { $("#qBtn").disabled = false; alert(e.message); }
  };
}
function showFeedback(x, r) {
  const ss = S.sess;
  $$("#opts .opt").forEach((o) => {
    o.disabled = true; o.classList.remove("sel");
    const l = o.dataset.l, ok = r.answers.includes(l), mine = ss.sel.has(l);
    if (ok) { o.classList.add("right"); $(".tag", o).textContent = mine ? "Your pick · right" : "Right answer"; }
    else if (mine) { o.classList.add("wrong"); $(".tag", o).textContent = "Your pick"; }
    else o.classList.add("dim");
  });
  $("#qcheck").innerHTML = "";
  const X = r.explained || {};
  const step = x.lab && S.labs.find((l) => l.id === x.lab);
  const st = step && step.steps.find((s) => s.gid === x.gid);
  const wrong = Object.entries(X.wrong || {}).sort();
  $(".segs").innerHTML = ss.list.map((_, k) => `<span class="${k < ss.res.length ? (ss.res[k] ? "r" : "w") : ""}"></span>`).join("");
  $("#qfb").innerHTML = `
    <div class="banner ${r.correct ? "ok" : "bad"} rise"><span class="ball pop" style="color:#fff">${ic(r.correct ? "check" : "x", r.correct ? 26 : 20, 3, "")}</span><div><b>${r.correct ? "Right!" : "Not quite"}</b><span>${r.correct ? "Nice. Read why, so you remember it." : `The answer is ${esc(r.answers.join(", "))}. Read why below.`}</span></div></div>
    ${X.flag ? `<div class="caution rise" style="margin-top:16px">${ic("warn", 22, 2)}<div><b>Check this one</b><div class="md">${md(X.flag)}</div></div></div>` : ""}
    <section class="explain rise" style="margin-top:16px">
      ${X.idea ? `<div><h2 style="color:var(--primary-text)">The idea being tested</h2><div class="md">${md(X.idea)}</div></div><div class="sep"></div>` : ""}
      ${X.why ? `<div><h2 style="color:var(--ok-text)">Why ${esc(r.answers.join(", "))} is right</h2><div class="md">${md(X.why)}</div></div>` : ""}
      ${wrong.length ? `<div class="sep"></div><div><h2 style="color:var(--bad-text)">Why the others are wrong</h2>${wrong.map(([k, v]) => `<div class="wr"><span class="k">${esc(k)}</span><div class="md">${md(v)}</div></div>`).join("")}</div>` : ""}
      ${!X.idea && !X.why ? `<div><h2 class="muted">Explanation</h2><div class="md"><pre>${esc(r.explanation)}</pre></div></div>` : ""}
    </section>
    <div class="nextbar rise" style="margin-top:16px">
      <span class="l">${ic("clock")} Next review: ${esc(fmtDate(r.next_review) || "tomorrow")}</span>
      <span style="display:flex;gap:10px;flex-wrap:wrap">${st ? `<a class="ghost" href="#/lab/${x.lab}/${st.key}">Open the lab on this</a>` : ""}<button class="btn" id="nextQ">${ss.i + 1 < ss.list.length ? "Next question" : "See my results"} ${ic("next", 18, 2.5)}</button></span>
    </div>`;
  $("#nextQ").onclick = () => { ss.i++; ss.result = null; ss.revealed = false; if (ss.guided) store.set(`guided:${ss.key}`, ss.i); route(); window.scrollTo(0, 0); };
}
function sessionEnd() {
  setTimeout(animateRings, 0);
  if (S.sess.guided) store.del(`guided:${S.sess.key}`);
  const ss = S.sess, right = ss.res.filter(Boolean).length;
  return shell("practice", `<section class="card rise" style="display:flex;flex-wrap:wrap;gap:32px;align-items:center">
    <div style="position:relative;width:170px;height:170px">${ringSvg(pct(right, ss.res.length), 170, 66, 16, "var(--ok)")}
      <div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center"><span style="font-size:38px;font-weight:600">${right}/${ss.res.length}</span><span class="muted" style="font-size:13px">right</span></div></div>
    <div style="flex:1 1 300px;display:flex;flex-direction:column;gap:12px"><h1 class="ptitle" style="font-size:28px">${right === ss.res.length ? "All right. Excellent!" : "Set finished. Well done!"}</h1>
      <p class="lead">Questions you missed will come back tomorrow. Right ones come back later, so you remember them for the exam.</p>
      <div style="display:flex;gap:10px;flex-wrap:wrap"><a class="btn" href="${ss.back || "#/practice"}">${ss.guided ? "Back to the section notes" : "Back to practice"}</a><a class="ghost" href="#/today">Go to Today</a></div></div>
  </section>`, "narrow");
}

// ---------------------------------------------------------------- Mock exam
function viewMock() {
  const d = S.dash, m = d.mocks;
  const best = m.length ? Math.max(...m.map((x) => pct(x.correct, x.total))) : null;
  const inner = `<header class="rise"><h1 class="ptitle">Mock exam</h1><p class="lead" style="margin-top:8px">Practise like the real exam: 45 questions, 90 minutes, no hints until the end.</p></header>
  <div class="stats rise">
    <div class="stat"><span class="k">Attempts</span><span class="v">${m.length}</span></div>
    <div class="stat"><span class="k">Best score</span><span class="v">${best == null ? "—" : `${best}<small>%</small>`}</span></div>
    <div class="stat"><span class="k">Last score</span><span class="v">${m.length ? `${pct(m[0].correct, m[0].total)}<small>%</small>` : "—"}</span></div>
    <div class="stat"><span class="k">Goal</span><span class="v">70<small>%</small></span></div>
  </div>
  <div class="row rise">
    <section class="card grow2" style="display:flex;flex-direction:column;gap:16px">
      <h2 class="h2">How it works</h2>
      ${[["clock", "90 minutes. The timer keeps running even if you leave this page."], ["flag", "Flag a question to come back to it. You can change answers any time."], ["eye", "No feedback during the exam. At the end you see every answer explained."], ["target", "Missed questions go to your review list automatically."]]
        .map(([i, t]) => `<div style="display:flex;gap:12px;align-items:flex-start">${ic(i, 20, 2)}<span class="body" style="font-size:15px">${t}</span></div>`).join("")}
      <div>${d.active_mock ? `<a class="btn" href="#/mock/exam/${d.active_mock}">Continue your mock exam</a>` : `<button class="btn" id="startMock">Start mock exam</button>`}</div>
    </section>
    <section class="card grow1" style="display:flex;flex-direction:column;gap:10px">
      <h2 class="h2">Questions per section</h2>
      ${d.mock_allocation.map((a) => `<div style="display:flex;justify-content:space-between;font-size:14px;gap:10px"><span>${a.id} · ${esc(SEC_SHORT[a.id])}</span><b>${a.count}</b></div>`).join("")}
      <p class="muted" style="font-size:13px;margin:4px 0 0">Matches the official section weights.</p>
    </section>
  </div>
  <section class="card rise" style="display:flex;flex-direction:column;gap:12px"><h2 class="h2">Past attempts</h2>
    ${m.length ? `<div style="overflow-x:auto"><table class="past"><thead><tr><th>Date</th><th>Score</th><th>Weakest section</th><th></th></tr></thead><tbody>
      ${m.map((x) => `<tr><td>${x.started ? new Date(x.started * 1000).toLocaleDateString(undefined, { day: "numeric", month: "short" }) : ""}</td><td><b>${pct(x.correct, x.total)}%</b> <span class="muted">${x.correct}/${x.total}</span></td><td>${esc(x.weakest || "—")}</td><td><a href="#/mock/results/${x.id}">See results</a></td></tr>`).join("")}</tbody></table></div>`
      : '<p class="muted" style="margin:0">No attempts yet. Your first one shows where you stand.</p>'}
  </section>`;
  setTimeout(() => {
    const b = $("#startMock");
    if (b) b.onclick = async () => {
      if (!confirm("Start the 90-minute mock exam now?")) return;
      try { const ex = await api("/api/mock/start", {}); await refresh(); location.hash = `#/mock/exam/${ex.id}`; } catch (e) { alert(e.message); }
    };
  }, 0);
  return shell("mock", inner, "mid");
}

async function viewMockExam(id) {
  if (!S.mock || S.mock.id !== id) {
    const ex = await api(`/api/mock?id=${encodeURIComponent(id)}`);
    if (ex.finished) return (location.hash = `#/mock/results/${id}`);
    S.mock = { ...ex, i: 0, flags: new Set(store.get(`flags:${id}`, [])) };
  }
  renderMockQ();
}
function renderMockQ() {
  const M = S.mock, q = M.questions[M.i], sel = M.answers[q.id] || [];
  const answered = Object.values(M.answers).filter((a) => a.length).length;
  const pics = (q.images || []).map((src) => `<img class="qimg" src="${esc(src)}" alt="Question picture">`).join("");
  const needPic = q.choices.some((c) => !String(c.text || "").trim());
  $("#app").innerHTML = `<div style="min-height:100vh">
    <header class="topbar"><a class="ghost flat" href="#/mock">${ic("back")} Leave (timer keeps running)</a>
      <div class="ttl"><span>Mock exam</span><b>Question ${M.i + 1} of ${M.questions.length}</b></div>
      <div style="margin-left:auto;display:flex;gap:12px;align-items:center"><span class="muted" style="font-size:14px">${answered} answered</span><span class="timer" id="clock" role="timer">--:--</span></div></header>
    <div class="steparea"><div>
      <section class="learn" style="flex:2 1 560px;gap:18px">
        <h1 class="qtitle">${esc(q.q)}</h1>
        ${pics ? `<details class="pic" ${needPic ? "open" : ""}><summary>See the original question picture</summary>${pics}</details>` : ""}
        <p class="muted" style="margin:0;font-size:14px">${q.multiple ? "Choose all the right answers." : "Choose one answer."}</p>
        <div class="opts">${q.choices.map((c) => `<button class="opt ${sel.includes(c.label) ? "sel" : ""}" data-l="${esc(c.label)}"><span class="k">${esc(c.label)}</span><span class="t">${esc(c.text || "See the picture above")}</span></button>`).join("")}</div>
        <div style="display:flex;flex-wrap:wrap;gap:10px;justify-content:space-between">
          <button class="ghost" id="mPrev" ${M.i ? "" : "disabled"}>${ic("back")} Back</button>
          <button class="ghost ${M.flags.has(q.id) ? "flagged" : ""}" id="mFlag">${ic("flag")} ${M.flags.has(q.id) ? "Flagged" : "Flag for later"}</button>
          ${M.i + 1 < M.questions.length ? `<button class="btn" id="mNext">Next ${ic("next", 18, 2.5)}</button>` : `<button class="btn" id="mFin2">Finish exam</button>`}
        </div>
      </section>
      <aside class="docard" style="flex:1 1 280px">
        <h2 class="h2" style="font-size:17px">All questions</h2>
        <div class="cells">${M.questions.map((x, k) => `<button class="cell ${(M.answers[x.id] || []).length ? "ans" : ""} ${M.flags.has(x.id) ? "flag" : ""} ${k === M.i ? "cur" : ""}" data-k="${k}" aria-label="Question ${k + 1}">${k + 1}</button>`).join("")}</div>
        <div class="legend"><span><i style="background:var(--primary)"></i>Answered</span><span><i style="background:#FFB46B"></i>Flagged</span><span><i style="background:#EDF0F5"></i>Not yet</span></div>
        <button class="btn green" id="mFin">Finish exam</button>
      </aside>
    </div></div></div>`;
  $$(".opt").forEach((b) => (b.onclick = async () => {
    const old = M.answers[q.id] || [];
    let v = q.multiple ? new Set(old) : new Set();
    const l = b.dataset.l;
    if (q.multiple && v.has(l)) v.delete(l); else v.add(l);
    v = [...v];
    try { await api("/api/mock/save", { id: M.id, question: q.id, choices: v }); M.answers[q.id] = v; renderMockQ(); }
    catch (e) { alert(e.message); }
  }));
  const go = (k) => { M.i = k; renderMockQ(); window.scrollTo(0, 0); };
  $("#mPrev").onclick = () => go(M.i - 1);
  $("#mNext") && ($("#mNext").onclick = () => go(M.i + 1));
  $("#mFlag").onclick = () => { M.flags.has(q.id) ? M.flags.delete(q.id) : M.flags.add(q.id); store.set(`flags:${M.id}`, [...M.flags]); renderMockQ(); };
  $$(".cell").forEach((c) => (c.onclick = () => go(+c.dataset.k)));
  $("#mFin2") && ($("#mFin2").onclick = () => finishMock(false));
  $("#mFin").onclick = () => finishMock(false);
  clearInterval(S.timer);
  const tick = () => {
    const el = $("#clock");
    if (!el) return clearInterval(S.timer);
    const left = Math.max(0, Math.ceil(M.expires - Date.now() / 1000));
    el.textContent = `${Math.floor(left / 60)}:${String(left % 60).padStart(2, "0")}`;
    if (!left) finishMock(true);
  };
  tick(); S.timer = setInterval(tick, 1000);
}
async function finishMock(expired) {
  const M = S.mock;
  const left = M.questions.filter((x) => !(M.answers[x.id] || []).length).length;
  if (!expired && !confirm(left ? `${left} question${left > 1 ? "s are" : " is"} not answered. Finish anyway?` : "Finish the exam and see your results?")) return;
  clearInterval(S.timer);
  busy("Scoring your exam…");
  try { await api("/api/mock/finish", { id: M.id }); await refresh(); S.mock = null; location.hash = `#/mock/results/${M.id}`; }
  catch (e) { alert(e.message); }
  idle();
}

async function viewMockResults(id) {
  const [ex, all] = await Promise.all([api(`/api/mock?id=${encodeURIComponent(id)}`), bank()]);
  if (!ex.finished) return (location.hash = `#/mock/exam/${id}`);
  const R = ex.result, res = R.results;
  const flags = new Set(store.get(`flags:${id}`, []));
  const info = S.dash.mocks.find((m) => m.id === id) || {};
  const score = pct(R.correct, R.total);
  const prev = S.dash.mocks.filter((m) => m.started < info.started);
  const first = prev.length ? pct(prev[prev.length - 1].correct, prev[prev.length - 1].total) : null;
  const secs = S.dash.sections.map((s) => {
    const rs = res.filter((r) => r.section === s.id);
    const right = rs.filter((r) => r.correct).length;
    return { ...s, right, n: rs.length, p: pct(right, rs.length) };
  }).filter((s) => s.n);
  const weakest = [...secs].sort((a, b) => a.p - b.p)[0];
  const labFor = { 1: "Lab 7", 2: "Lab 1", 3: "Lab 6", 4: "Lab 2", 5: "Lab 8", 6: "Lab 7", 7: "Lab 9" };
  const wrongIds = res.filter((r) => !r.correct).map((r) => r.id);
  const need = Math.max(0, Math.ceil(0.7 * R.total) - R.correct);
  const used = info.finished_at && info.started ? Math.min(90, Math.round((info.finished_at - info.started) / 60)) : null;
  const byId = Object.fromEntries(all.map((q) => [q.id, q]));
  const headline = score >= 70 ? "You reached your goal. Great work!" : need <= 2 ? `So close! ${need} more right answer${need > 1 ? "s" : ""} reaches your goal.` : "A good start. Now you know what to study.";
  const inner = `<div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap"><a class="ghost flat" href="#/mock">${ic("back")} Mock exam</a><b>Results${info.started ? ` · ${new Date(info.started * 1000).toLocaleDateString(undefined, { day: "numeric", month: "short" })}` : ""}</b></div>
  <section class="card rise" style="border-radius:28px;padding:32px;display:flex;flex-wrap:wrap;gap:32px;align-items:center">
    <div style="position:relative;width:170px;height:170px;flex-shrink:0">${ringSvg(score)}
      <div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center"><span style="font-size:38px;font-weight:600">${score}%</span><span class="muted" style="font-size:13px">${R.correct} of ${R.total}</span></div></div>
    <div style="flex:1 1 340px;display:flex;flex-direction:column;gap:12px">
      <h1 style="font-size:30px;font-weight:600;letter-spacing:-.5px">${headline}</h1>
      <p class="lead">${first != null ? `That is <b>${score - first >= 0 ? "+" : ""}${score - first}%</b> since your first try. ` : ""}Your goal is 70%.${weakest && weakest.p < 70 ? ` Focus on the orange sections below.` : ""}</p>
      <div style="display:flex;flex-wrap:wrap;gap:10px;font-size:14px"><span class="chippill" style="background:var(--ok-soft);color:var(--ok-deep)">${R.correct} right</span><span class="chippill" style="background:var(--bad-soft);color:var(--bad-deep)">${R.total - R.correct} wrong</span>${used != null ? `<span class="chippill">${used} of 90 min used</span>` : ""}</div>
    </div>
  </section>
  <div class="row rise">
    <section class="card" style="flex:1.3 1 440px;display:flex;flex-direction:column;gap:18px;padding:26px">
      <div style="display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:8px"><h2 class="h2">By section</h2><span class="muted" style="display:inline-flex;align-items:center;gap:8px;font-size:13px"><span style="width:2px;height:14px;background:var(--ink)"></span>70% goal</span></div>
      ${secs.map((s) => `<div style="display:flex;flex-direction:column;gap:6px"><div style="display:flex;justify-content:space-between;gap:12px;font-size:15px"><span>${esc(s.name)}</span><span style="font-weight:600;white-space:nowrap;color:${s.p >= 70 ? "var(--ok-text)" : "#B8460A"}">${s.right}/${s.n} · ${s.p}%</span></div>
        <div class="goalbar"><div style="width:${s.p}%;background:${s.p >= 70 ? "var(--ok)" : "var(--warm-btn)"}"></div><i></i></div></div>`).join("")}
    </section>
    <section style="flex:1 1 320px;background:var(--primary-soft);border-radius:24px;padding:26px;display:flex;flex-direction:column;gap:14px">
      <h2 class="h2">Your plan from this exam</h2>
      ${[`The ${wrongIds.length} questions you missed were added to your review list.`, weakest ? `Do ${labFor[weakest.id]}. It covers your weakest section, ${esc(weakest.name)}.` : "Keep going with your labs.", "Try another mock exam in about a week."]
        .map((t, k) => `<div style="display:flex;gap:12px;align-items:flex-start;background:#fff;border-radius:16px;padding:14px"><span class="plan" style="padding:0;border:0"><span class="n" style="background:var(--primary);color:#fff;width:28px;height:28px;font-size:13px">${k + 1}</span></span><span style="font-size:15px;line-height:1.5">${t}</span></div>`).join("")}
      ${wrongIds.length ? `<a class="btn" style="align-self:flex-start" href="#/practice/session?mode=ids&id=${wrongIds.join(",")}">Review my ${wrongIds.length} mistakes</a>` : ""}
    </section>
  </div>
  <section class="card rise" style="display:flex;flex-direction:column;gap:12px;padding:26px">
    <div style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:12px"><h2 class="h2">Every question, with explanations</h2>
      <div style="display:flex;gap:8px;flex-wrap:wrap" id="rfilter"><button class="chip" data-f="all">All ${res.length}</button><button class="chip on" data-f="wrong">Wrong ${wrongIds.length}</button><button class="chip" data-f="flag">Flagged ${res.filter((r) => flags.has(r.id)).length}</button></div></div>
    <div id="rlist" style="display:flex;flex-direction:column;gap:10px"></div>
  </section>`;
  setTimeout(() => {
    const draw = (f) => {
      $$("#rfilter .chip").forEach((c) => c.classList.toggle("on", c.dataset.f === f));
      const rows = res.map((r, k) => ({ r, k })).filter(({ r }) => f === "all" || (f === "wrong" ? !r.correct : flags.has(r.id)));
      $("#rlist").innerHTML = rows.map(({ r, k }) => {
        const q = byId[r.id] || {};
        return `<div><button class="qrow" data-k="${k}"><span class="n ${r.correct ? "r" : "w"}">${k + 1}</span><span class="t"><span>${esc(q.q || `Question ${r.number}`)}</span><span class="muted" style="font-size:13px">${esc(SEC_SHORT[r.section])} · You: ${esc(r.choices.join(", ") || "no answer")} · Right: ${esc(r.answers.join(", "))}</span></span><span style="font-size:14px;color:var(--primary-text);font-weight:500">Explain</span></button><div class="rx" hidden></div></div>`;
      }).join("") || '<p class="muted">Nothing here.</p>';
      $$("#rlist .qrow").forEach((b) => (b.onclick = () => {
        const box = b.nextElementSibling, r = res[+b.dataset.k], X = r.explained || {};
        if (!box.hidden) { box.hidden = true; return; }
        const wrong = Object.entries(X.wrong || {}).sort();
        box.innerHTML = `<div class="explain" style="margin:8px 0 6px">${X.flag ? `<div class="caution">${ic("warn", 20, 2)}<div><b>Check this one</b><div class="md">${md(X.flag)}</div></div></div>` : ""}
          ${X.idea ? `<div><h2 style="color:var(--primary-text)">The idea</h2><div class="md">${md(X.idea)}</div></div>` : ""}
          ${X.why ? `<div><h2 style="color:var(--ok-text)">Why ${esc(r.answers.join(", "))} is right</h2><div class="md">${md(X.why)}</div></div>` : `<div class="md"><pre>${esc(r.explanation)}</pre></div>`}
          ${wrong.length ? `<div><h2 style="color:var(--bad-text)">Why the others are wrong</h2>${wrong.map(([k2, v]) => `<div class="wr"><span class="k">${esc(k2)}</span><div class="md">${md(v)}</div></div>`).join("")}</div>` : ""}</div>`;
        box.hidden = false;
      }));
    };
    $$("#rfilter .chip").forEach((c) => (c.onclick = () => draw(c.dataset.f)));
    draw(wrongIds.length ? "wrong" : "all");
    animateRings();
  }, 0);
  return shell("mock", inner);
}

// ---------------------------------------------------------------- Progress
function viewProgress() {
  const d = S.dash;
  const maxMin = Math.max(30, ...d.week.map((w) => w.minutes));
  const qPart = Math.round(d.sections.reduce((a, s) => a + s.weight * (s.total ? s.right / s.total : 0), 0));
  const lPart = pct(d.steps.done, d.steps.total);
  const nexts = [];
  if (d.next_step) nexts.push(["Now", `Lab step ${d.next_step.key}`, cleanTitle(d.next_step.title), `#/lab/${d.next_step.lab}/${d.next_step.key}`, "Continue"]);
  if (d.due.today) nexts.push(["Today", `${d.due.today} review question${d.due.today > 1 ? "s" : ""}`, "Due today", "#/practice/session?mode=due", "Review"]);
  if (d.weakest_section && d.weakest_section.pct < 70) nexts.push(["This week", `Section ${d.weakest_section.id} · ${SEC_SHORT[d.weakest_section.id]}`, `${d.weakest_section.pct}% right so far`, `#/practice/session?mode=section&id=${d.weakest_section.id}`, "Practise"]);
  else nexts.push(["This week", "10 new questions", `${d.questions.new} not seen yet`, "#/practice/session?mode=new", "Start"]);
  const inner = `<header class="rise"><h1 class="ptitle">Progress</h1><p class="lead" style="margin-top:8px">Where you stand, and what to do next.</p></header>
  <div class="row rise">
    <section class="card grow2" style="display:flex;flex-wrap:wrap;gap:28px;align-items:center">
      <div style="position:relative;width:170px;height:170px;flex-shrink:0">${ringSvg(d.readiness)}
        <div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center"><span style="font-size:38px;font-weight:600">${d.readiness}%</span><span class="muted" style="font-size:13px">ready</span></div></div>
      <div style="flex:1 1 260px;display:flex;flex-direction:column;gap:10px">
        <h2 class="h2">Exam readiness</h2>
        <p class="body" style="margin:0;font-size:15px;line-height:1.6">70% comes from practice questions you got right, weighted like the exam sections (now <b>${qPart}%</b>). 30% comes from lab steps done (now <b>${lPart}%</b>).</p>
        <p class="muted" style="margin:0;font-size:13px">70% × ${qPart}% + 30% × ${lPart}% = ${d.readiness}%</p>
      </div>
    </section>
    <section class="card grow1" style="display:flex;flex-direction:column;gap:14px">
      <div style="display:flex;justify-content:space-between;align-items:baseline"><h2 class="h2">This week</h2><span class="muted" style="font-size:14px">${d.week_minutes} min</span></div>
      <div class="wk">${d.week.map((w, i) => `<div><div class="b ${i === 6 ? "today" : ""}" style="height:${Math.max(4, (100 * w.minutes) / maxMin)}%" title="${w.minutes} min"></div><span class="${i === 6 ? "today" : ""}">${w.day}</span></div>`).join("")}</div>
      <p class="muted" style="margin:0;font-size:13px">Minutes with the app open and in use.</p>
    </section>
  </div>
  <section class="rise" style="background:var(--primary-soft);border-radius:24px;padding:24px;display:flex;flex-direction:column;gap:14px">
    <h2 class="h2">What to do next</h2>
    <ul class="nextgrid">${nexts.map(([w, t, s, href, b], k) => `<li><span class="when ${k ? "" : "now"}">${w.toUpperCase()}</span><b>${esc(t)}</b><span class="muted" style="font-size:14px">${esc(s)}</span><a class="${k ? "ghost" : "btn"}" href="${href}" style="align-self:flex-start">${b}</a></li>`).join("")}</ul>
  </section>
  <div class="row rise">
    <section class="card grow2" style="display:flex;flex-direction:column;gap:16px">
      <h2 class="h2">By exam section</h2>
      ${d.sections.map((s) => `<a href="#/practice/session?mode=section&id=${s.id}" style="display:flex;flex-direction:column;gap:6px;text-decoration:none;color:var(--ink)">
        <div style="display:flex;justify-content:space-between;gap:12px;font-size:15px"><span>${s.id} · ${esc(s.name)} <span class="muted" style="font-size:13px">${s.weight}%</span></span><span style="font-weight:600;white-space:nowrap">${s.pct == null ? '<span class="muted" style="font-weight:400">not started</span>' : `${s.pct}% right`} <span class="muted" style="font-weight:400;font-size:13px">· ${s.tried}/${s.total} tried</span></span></div>
        <div class="goalbar"><div style="width:${pct(s.right, s.total)}%;background:${s.pct == null ? "#D7DCE6" : s.pct >= 70 ? "var(--ok)" : "var(--warm-btn)"}"></div><i></i></div></a>`).join("")}
    </section>
    <section class="card grow1" style="display:flex;flex-direction:column;gap:16px">
      <h2 class="h2">Labs</h2>
      <div class="labcells">${d.labs.map((l) => `<b>${labNo(l.id)}</b><div class="c" title="${esc(l.name)}">${Array.from({ length: l.total }, (_, k) => `<span class="${k < l.done ? "d" : ""}"></span>`).join("")}</div><span class="muted">${l.done}/${l.total}</span>`).join("")}</div>
      <h2 class="h2" style="margin-top:8px">Weak topics</h2>
      ${d.weak.length ? d.weak.map((t) => `<a class="weak" href="#/practice/session?mode=topic&id=${t.id}"><span><b style="font-weight:600">${esc(t.title)}</b><small>${t.right} of ${t.tried} right</small></span><em>Practise</em></a>`).join("") : '<p class="muted" style="margin:0;font-size:14px">Weak topics appear after you try 3 questions in a topic.</p>'}
    </section>
  </div>`;
  setTimeout(animateRings, 0);
  return shell("progress", inner);
}

// ---------------------------------------------------------------- router
async function route() {
  clearInterval(S.timer);
  const [path, qs] = location.hash.replace(/^#\/?/, "").split("?");
  const parts = path.split("/").filter(Boolean);
  const q = new URLSearchParams(qs || "");
  const app = $("#app");
  try {
    if (!S.dash) await refresh();
    const [a, b, c] = parts;
    let html;
    if (!a || a === "today") html = viewToday();
    else if (a === "labs") html = viewLabs();
    else if (a === "lab") return void (await viewLabStep(b, c));
    else if (a === "practice" && b === "session") html = await viewSession(q);
    else if (a === "learn") html = await viewLearn(b);
    else if (a === "practice") html = await viewPractice();
    else if (a === "mock" && b === "exam") return void (await viewMockExam(c));
    else if (a === "mock" && b === "results") html = await viewMockResults(c);
    else if (a === "mock") html = viewMock();
    else if (a === "progress") html = viewProgress();
    else return void (location.hash = "#/today");
    if (typeof html === "string") { app.innerHTML = html; wireShell(); }
  } catch (e) {
    app.innerHTML = `<div class="page narrow" style="padding:60px 20px"><section class="card"><h2 class="h2">Something went wrong</h2><p class="lead" style="margin:10px 0">${esc(e.message)}</p><p class="muted">Is the portal server still running? Start it with <code>.venv/bin/python -m portal.server</code>.</p><button class="btn" onclick="location.reload()">Try again</button></section></div>`;
  }
}
window.addEventListener("hashchange", () => { if (!location.hash.startsWith("#/practice/session")) S.sess = null; route().then(() => window.scrollTo(0, 0)); });

// ---------------------------------------------------------------- study time heartbeat
let lastInput = Date.now();
["pointerdown", "keydown", "scroll", "pointermove"].forEach((e) => addEventListener(e, () => (lastInput = Date.now()), { passive: true }));
setInterval(() => {
  if (document.visibilityState === "visible" && Date.now() - lastInput < 120000) api("/api/heartbeat", { minutes: 1 }).catch(() => {});
}, 60000);

if (window.mermaid) mermaid.initialize({ startOnLoad: false, theme: "base", securityLevel: "loose",
  flowchart: { curve: "basis", htmlLabels: true, padding: 14, nodeSpacing: 40, rankSpacing: 50, wrappingWidth: 240 },
  themeVariables: { fontFamily: "Lexend, sans-serif", fontSize: "14px", primaryColor: "#EAEFFF", primaryBorderColor: "#9DB0F0",
    primaryTextColor: "#1C2433", lineColor: "#8A93A8", secondaryColor: "#E9F6EF", tertiaryColor: "#FFF6EC" } });
$("#lightbox").onclick = () => ($("#lightbox").hidden = true);
route();
