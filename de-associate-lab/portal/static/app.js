// DE Lab Portal — front end
const S = { labs: [], lab: null, step: null, editor: null };
const $ = (sel) => document.querySelector(sel);
const esc = (t) => String(t ?? "").replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
const md = (t) => (window.marked ? marked.parse(t || "") : `<pre>${esc(t)}</pre>`);
const store = {
  get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch { return d; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} },
};

async function api(path, body) {
  const r = await fetch(path, body ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) } : {});
  const j = await r.json();
  if (!r.ok) throw new Error(j.error || r.statusText);
  return j;
}
function busy(msg) { $("#overlayMsg").textContent = msg; $("#overlay").hidden = false; }
function idle() { $("#overlay").hidden = true; }

// ---------------------------------------------------------------- navigation
const gated = (s) => s.type !== "info";
function unlocked(lab, i) {
  return lab.steps.slice(0, i).filter(gated).every((s) => s.done);
}
function labPct(lab) {
  const g = lab.steps.filter(gated);
  return g.length ? Math.round((100 * g.filter((s) => s.done).length) / g.length) : 0;
}

const THEME = {
  lab1_ingestion: { color: "#2563eb", soft: "#e8f0ff", icon: "📥", course: "Exam §2 Ingestion · 21%" },
  lab2_jobs: { color: "#7c3aed", soft: "#f1eafe", icon: "🗂️", course: "Exam §4 Lakeflow Jobs · 16%" },
  lab3_pipelines: { color: "#0d9488", soft: "#e2f6f3", icon: "🔀", course: "Exam §3 Transform (pipelines) · 22%" },
  lab4_devops: { color: "#ea580c", soft: "#fff0e6", icon: "🧪", course: "Course 4 · testing (bonus)" },
  lab5_delta_sql_streaming: { color: "#db2777", soft: "#fde8f2", icon: "⚡", course: "Exam §3 + §6 · Delta & SQL" },
  lab6_transform_tuning: { color: "#0891b2", soft: "#e0f5fa", icon: "🧹", course: "Exam §3 Transform & model · 22%" },
  lab7_troubleshooting: { color: "#dc2626", soft: "#fdecec", icon: "🩺", course: "Exam §6 + §1 · 10% + 6%" },
  lab8_cicd_bundles: { color: "#4f46e5", soft: "#ecebff", icon: "🚀", course: "Exam §5 CI/CD · 10%" },
  lab9_governance: { color: "#059669", soft: "#e3f7ef", icon: "🛡️", course: "Exam §7 Governance · 15%" },
};
const theme = (l) => THEME[l.id] || THEME.lab1_ingestion;
const CHECK_SVG = `<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3.5 8.5l3 3 6-7" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
const LOCK_SVG = `<svg viewBox="0 0 16 16" aria-hidden="true"><rect x="3.5" y="7" width="9" height="6.5" rx="1.5" fill="currentColor"/><path d="M5.5 7V5.2a2.5 2.5 0 015 0V7" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>`;
const cleanTitle = (t) => t.replace(/^\d[a-z]\s*·\s*/, "").replace(/\s*\(lesson [\d.]+\)/, "");
const lessonTag = (t) => (t.match(/\(lesson ([\d.]+)\)/) || [])[1];

function ring(pct, color, size = 34) {
  const r = (size - 6) / 2, c = 2 * Math.PI * r;
  return `<svg class="ring" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
    <circle cx="${size / 2}" cy="${size / 2}" r="${r}" fill="none" stroke="rgba(255,255,255,.14)" stroke-width="3.5"/>
    <circle cx="${size / 2}" cy="${size / 2}" r="${r}" fill="none" stroke="${color}" stroke-width="3.5" stroke-linecap="round"
      stroke-dasharray="${c}" stroke-dashoffset="${c * (1 - pct / 100)}" transform="rotate(-90 ${size / 2} ${size / 2})"/></svg>`;
}

function renderTabs() {
  $("#labtabs").innerHTML = S.labs.map((l) => {
    const t = theme(l), pct = labPct(l), active = S.lab && S.lab.id === l.id;
    return `<button data-lab="${l.id}" class="course ${active ? "active" : ""}" style="--c:${t.color}">
      <span class="course-icon">${t.icon}</span>
      <span class="course-txt"><b>${l.label}</b><small>${esc(l.name)}</small></span>
      <span class="course-ring">${ring(pct, t.color)}<i>${pct === 100 ? "✓" : pct}</i></span></button>`;
  }).join("");
  document.querySelectorAll("#labtabs button").forEach((b) => (b.onclick = () => openLab(b.dataset.lab)));
  const all = S.labs.flatMap((l) => l.steps.filter(gated));
  const done = all.filter((s) => s.done).length;
  $("#overallbar").style.width = `${(100 * done) / all.length}%`;
  $("#overalltxt").textContent = `${done} / ${all.length} tasks`;
  if (S.lab) {
    const t = theme(S.lab);
    document.documentElement.style.setProperty("--lab", t.color);
    document.documentElement.style.setProperty("--lab-soft", t.soft);
  }
}

function renderSteps() {
  const lab = S.lab, t = theme(lab), pct = labPct(lab);
  const g = lab.steps.filter(gated);
  $("#labhead").innerHTML = `<div class="lab-badge">${t.icon}</div>
    <div><div class="lab-course">${esc(t.course)}</div><h2>${lab.label} · ${esc(lab.name)}</h2></div>
    <div class="lab-progress"><div class="bar"><div style="width:${pct}%"></div></div>
      <span>${g.filter((s) => s.done).length} of ${g.length} tasks · ${pct}%</span></div>`;
  let n = 0;
  $("#steps").innerHTML = lab.steps.map((s, i) => {
    const open = unlocked(lab, i), active = S.step && S.step.key === s.key;
    const state = s.done ? "done" : !open ? "locked" : active ? "current" : "todo";
    const num = s.type === "info" ? "★" : ++n;
    const tag = lessonTag(s.title);
    return `<li class="step ${state} ${active ? "active" : ""}" data-i="${i}">
      <span class="check">${s.done ? CHECK_SVG : open ? `<em>${num}</em>` : LOCK_SVG}</span>
      <span class="step-txt"><span class="step-title">${esc(cleanTitle(s.title))}</span>
        <span class="step-meta">${s.key.match(/^\d[a-z]/) ? `<code>${esc(s.key)}</code>` : ""}${tag ? ` · lesson ${tag}` : ""}${s.done ? ` · <b class="okc">done</b>` : ""}</span></span></li>`;
  }).join("");
  document.querySelectorAll("#steps li").forEach((li) => (li.onclick = () => {
    const i = +li.dataset.i;
    if (unlocked(lab, i)) openStep(lab.steps[i].key);
  }));
}

function openLab(id) {
  document.querySelector("aside").hidden = false;
  document.querySelector(".layout").classList.remove("practice-layout");
  S.lab = S.labs.find((l) => l.id === id);
  store.set("lab", id);
  const first = S.lab.steps.find((s, i) => !s.done && unlocked(S.lab, i)) || S.lab.steps[0];
  openStep(store.get(`step:${id}`, first.key), true);
}

// ---------------------------------------------------------------- step page
async function openStep(key, fromLab) {
  const lab = S.lab;
  let i = lab.steps.findIndex((s) => s.key === key);
  if (i < 0 || !unlocked(lab, i)) i = lab.steps.findIndex((s, j) => !s.done && unlocked(lab, j));
  if (i < 0) i = 0;
  S.step = lab.steps[i];
  store.set(`step:${lab.id}`, S.step.key);
  renderTabs(); renderSteps(); renderStep();
  if (window.addSectionPracticeLink) window.addSectionPracticeLink();
  busy(fromLab ? "Starting Spark and preparing the lab… (first time ≈ 30 s)" : "Preparing this step…");
  try {
    const r = await api("/api/open", { lab: lab.id, step: S.step.key });
    if (r.error) termShow([], r.error, "Setup error");
    else if (r.prep && (r.prep.outputs.length || r.prep.error)) termShow(r.prep.outputs, r.prep.error, "Setup output");
  } catch (e) { termShow([], { ename: "Error", evalue: e.message }, "Setup error"); }
  idle();
}

function renderStep() {
  const s = S.step, lab = S.lab;
  const idx = lab.steps.indexOf(s) + 1;
  const isFile = s.type === "file", isInfo = s.type === "info";
  const saved = store.get(`code:${lab.id}:${s.key}`, null);
  const Ls = s.lesson;
  const readKey = `read:${lab.id}:${s.key}`;
  const opened = !Ls || s.done || store.get(readKey, false);
  const Vs = s.visual;
  const visualHtml = Vs ? `
      <div class="analogy"><div class="analogy-icon">💡</div><div><b>Think of it like this</b><div class="learn">${md(Vs.analogy)}</div></div></div>
      ${Vs.diagram ? `<div class="diagram"><div class="diagram-lbl">📊 How it flows</div><pre class="mermaid">${esc(Vs.diagram)}</pre></div>` : ""}
      ${Vs.slides && Vs.slides.length ? `<div class="slides-lbl">🖼 From your course slides <span>(click to enlarge)</span></div>
        <div class="slides">${Vs.slides.map(([c, n, cap]) => `<figure data-src="/slides/${c}/${n}.jpg" data-cap="${esc(cap)}">
          <img loading="lazy" src="/slides/${c}/${n}.jpg" alt="${esc(cap)}"><figcaption>${esc(cap)}<small>Course ${c.slice(1)} · slide ${n}</small></figcaption></figure>`).join("")}</div>` : ""}` : "";
  const learnCard = Ls
    ? `<div class="card lesson"><h3>📘 Step 1 — Read & learn</h3>${visualHtml}<div class="learn">${md(Ls.read)}</div>
         ${opened ? "" : `<div class="btns"><button class="go" id="readBtn">✅ I've read this — show me the task</button></div>`}</div>`
    : (s.explain.trim() ? `<div class="card"><h3>📘 Learn</h3><div class="learn">${md(s.explain)}</div></div>` : "");
  const detail = Ls && s.explain.trim()
    ? `<details><summary>🔍 More detail: real Databricks syntax vs this lab</summary><div class="card learn" style="margin-top:6px">${md(s.explain)}</div></details>` : "";
  $("#main").innerHTML = `<div class="wrap">
    <div class="hero">
      <div class="crumb"><span class="pill">${theme(lab).icon} ${lab.label}</span> Step ${idx} of ${lab.steps.length}
        ${lessonTag(s.title) ? `<span class="pill ghost">Lesson ${lessonTag(s.title)}</span>` : ""}
        ${s.done ? `<span class="pill ok">${CHECK_SVG} Completed</span>` : ""}</div>
      <h1>${esc(cleanTitle(s.title))}</h1>
    </div>
    ${learnCard}
    <div id="taskArea" ${opened ? "" : "hidden"}>
    ${detail}
    ${Ls ? `<div class="card todo"><h3>🛠 Step 2 — Do it</h3>
      ${/<FILL-IN/.test(s.starter) ? `<div class="howto"><b>How to fill in the gaps</b>
        <ol><li>In the editor, find <code>&lt;FILL-IN 1&gt;</code>, <code>&lt;FILL-IN 2&gt;</code> and so on — each number matches one item below.</li>
        <li>Delete the <b>whole</b> marker, including the <code>&lt;</code> and <code>&gt;</code> signs, and type the answer in its place.</li>
        <li>Each item shows the <b>finished line</b>. Make your line look exactly like it — same quotes, brackets and commas.</li>
        <li>If a marker is already between quotes (<code>"&lt;FILL-IN 1&gt;"</code>), keep those quotes and type only inside them.</li></ol></div>` : ""}
      <div class="learn">${md(Ls.do)}</div></div>` : ""}
    ${s.prep ? `<details><summary>⚙️ Setup code for this step (already ran for you)</summary><pre>${esc(s.prep)}</pre></details>` : ""}
    <div class="card">
      <div class="task-head"><h3>${isInfo ? "▶ Demo code" : isFile ? `✏️ Editor — <code>${esc(s.file)}</code>` : "✏️ Editor"}</h3>
        <span class="hint">${isInfo ? "" : "Replace every &lt;FILL-IN&gt; · Ctrl/⌘+Enter = Run"}</span></div>
      <div id="editorHost"></div>
      <div class="btns">
        ${isFile ? "" : `<button id="runBtn">▶ Run</button>`}
        <button class="primary" id="checkBtn">${isInfo ? "✓ Mark as done" : isFile ? "💾 Save & check" : "✔ Check my answer"}</button>
        ${isInfo ? "" : `<button id="solBtn">💡 Show solution</button><button class="ghost" id="resetBtn">↺ Reset code</button>`}
      </div>
    </div>
    <div id="solution"></div>
    ${s.after ? `<details><summary>⏭ After your code, this runs automatically when you check</summary><pre>${esc(s.after)}</pre></details>` : ""}
    <div class="termwin"><div class="termbar"><i></i><i></i><i></i><span>terminal — python · spark</span></div>
      <div class="terminal" id="term"><div class="lbl">OUTPUT</div><pre class="muted">Run your code to see the output here.</pre></div></div>
    <div id="result"></div>
    <div id="learnmore"></div>
    <div class="card scratch"><h3>🧪 Scratch terminal — try anything (Python, use <code>spark.sql("…")</code>)</h3>
      <textarea id="scratch" placeholder='e.g.  show(spark.sql("SHOW TABLES IN ${lab.id.startsWith("lab4") ? "default" : "lab" + lab.id[3]}"))'></textarea>
      <div class="btns"><button id="scratchBtn">▶ Run scratch</button></div></div>
    </div>
  </div>`;
  const start = saved ?? s.starter;
  if (window.CodeMirror) {
    S.editor = CodeMirror($("#editorHost"), { value: start, mode: s.file && s.file.endsWith(".yml") ? "yaml" : "python", lineNumbers: true, indentUnit: 4,
      viewportMargin: Infinity, extraKeys: { "Ctrl-Enter": run, "Cmd-Enter": run, Tab: (cm) => cm.replaceSelection("    ") } });
    S.editor.on("change", () => store.set(`code:${lab.id}:${s.key}`, S.editor.getValue()));
  } else {
    $("#editorHost").innerHTML = `<textarea class="fallback" id="fallback">${esc(start)}</textarea>`;
    S.editor = { getValue: () => $("#fallback").value, setValue: (v) => ($("#fallback").value = v) };
  }
  document.querySelectorAll(".slides figure").forEach((f) => (f.onclick = () => {
    const lb = $("#lightbox"); lb.querySelector("img").src = f.dataset.src; lb.querySelector("p").textContent = f.dataset.cap; lb.hidden = false;
  }));
  if (window.mermaid) {
    const draw = () => { try { mermaid.run({ querySelector: ".mermaid" }); } catch (e) {} };
    (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(draw);
  }
  $("#readBtn") && ($("#readBtn").onclick = () => {
    store.set(readKey, true);
    $("#readBtn").parentElement.remove();
    $("#taskArea").hidden = false;
    S.editor.refresh && S.editor.refresh();
    $("#taskArea").scrollIntoView({ behavior: "smooth", block: "start" });
  });
  $("#runBtn") && ($("#runBtn").onclick = run);
  $("#checkBtn").onclick = check;
  $("#solBtn") && ($("#solBtn").onclick = showSolution);
  $("#resetBtn") && ($("#resetBtn").onclick = () => { if (confirm("Reset the editor to the starting code?")) S.editor.setValue(s.starter); });
  $("#scratchBtn").onclick = runScratch;
  $("#scratch").onkeydown = (e) => { if ((e.metaKey || e.ctrlKey) && e.key === "Enter") runScratch(); };
  if (s.done) showLearn(true);
}

// ---------------------------------------------------------------- terminal
function termShow(outputs, error, label = "TERMINAL OUTPUT") {
  const parts = (outputs || []).map((o) => o.type === "html" ? `<div class="html">${o.html}</div>` : `<pre>${esc(o.text)}</pre>`);
  if (error) parts.push(`<pre class="err">${esc(error.ename)}: ${esc(error.evalue)}${error.traceback ? "\n\n" + esc(shortTb(error.traceback)) : ""}</pre>`);
  if (!parts.length) parts.push(`<pre>(no output)</pre>`);
  $("#term").innerHTML = `<div class="lbl">${esc(label)}</div>${parts.join("")}`;
  $("#term").scrollTop = 0;
}
function shortTb(tb) {
  const lines = tb.split("\n").filter((l) => !/site-packages|py4j|^\s*$/.test(l));
  return lines.slice(-12).join("\n");
}

async function run() {
  busy("Running your code…");
  try { const r = await api("/api/run", { lab: S.lab.id, code: S.editor.getValue() }); termShow(r.outputs, r.error); }
  catch (e) { termShow([], { ename: "Error", evalue: e.message }); }
  idle();
}

async function runScratch() {
  const code = $("#scratch").value.trim();
  if (!code) return;
  busy("Running…");
  try { const r = await api("/api/run", { lab: S.lab.id, code }); termShow(r.outputs, r.error, "SCRATCH OUTPUT"); }
  catch (e) { termShow([], { ename: "Error", evalue: e.message }, "SCRATCH OUTPUT"); }
  idle();
}

async function check() {
  const s = S.step;
  if (s.type !== "info" && /<FILL-IN/.test(S.editor.getValue())) {
    $("#result").innerHTML = `<div class="result bad">There is still a &lt;FILL-IN&gt; in your code. Replace it first.</div>`;
    return;
  }
  busy(s.type === "file" ? "Saving and running the checks… (tests can take ~30 s)" : "Checking your answer…");
  try {
    const r = await api("/api/check", { lab: S.lab.id, step: s.key, code: S.editor.getValue() });
    termShow(r.outputs, r.error);
    $("#result").innerHTML = `<div class="result ${r.passed ? "ok" : "bad"}">${esc(r.message || (r.passed ? "✅ Passed" : "Not yet"))}</div>`;
    if (r.passed) { s.done = true; renderTabs(); renderSteps(); showLearn(false); }
  } catch (e) {
    $("#result").innerHTML = `<div class="result bad">${esc(e.message)}</div>`;
  }
  idle();
}

async function showSolution() {
  if (!confirm("Try it yourself first! 🙂\nShow the solution anyway?")) return;
  const r = await api("/api/solution", { lab: S.lab.id, step: S.step.key });
  $("#solution").innerHTML = `<div class="card"><h3>💡 Solution</h3><pre class="learn" style="white-space:pre-wrap">${esc(r.code)}</pre>
    <div class="btns"><button id="useSol">Copy into editor</button></div>
    <p class="hint">Read it line by line and make sure you understand <b>why</b> it works — then press Check.</p></div>`;
  $("#useSol").onclick = () => S.editor.setValue(r.code);
}

// ---------------------------------------------------------------- learn + quiz + next
function nextStepKey() {
  const i = S.lab.steps.indexOf(S.step);
  return S.lab.steps[i + 1]?.key;
}
function nextButton() {
  const k = nextStepKey();
  if (k) return `<div class="next"><button class="go" id="nextBtn">Next step →</button></div>`;
  const li = S.labs.indexOf(S.lab);
  return S.labs[li + 1] ? `<div class="next"><button class="go" id="nextLabBtn">🎉 Lab finished — start ${S.labs[li + 1].label} →</button></div>` : `<div class="result ok">🎉 You finished every lab!</div>`;
}
function wireNext() {
  $("#nextBtn") && ($("#nextBtn").onclick = () => openStep(nextStepKey()));
  $("#nextLabBtn") && ($("#nextLabBtn").onclick = () => openLab(S.labs[S.labs.indexOf(S.lab) + 1].id));
}

function showLearn(already) {
  const s = S.step, L = s.learn;
  const lastPart = !!s.check || s.type === "info";
  if (!L || !lastPart) { $("#learnmore").innerHTML = nextButton(); wireNext(); return; }
  $("#learnmore").innerHTML = `
    <div class="card"><h3>🧠 How it works</h3><div class="learn">${md(L.why)}</div></div>
    <div class="card quiz"><h3>❓ Exam question</h3><div class="learn">${md(L.q)}</div>
      ${L.opts.map((o, i) => `<button class="opt" data-i="${i}">${"ABCD"[i]}. ${md(o).replace(/^<p>|<\/p>\s*$/g, "")}</button>`).join("")}
      <div class="fb" id="fb"></div></div>
    <div id="after"></div>`;
  const finish = () => { $("#after").innerHTML = nextButton(); wireNext(); };
  document.querySelectorAll(".quiz .opt").forEach((b) => (b.onclick = async () => {
    const r = await api("/api/answer", { lab: S.lab.id, gid: s.gid, choice: +b.dataset.i });
    document.querySelectorAll(".quiz .opt").forEach((x) => (x.disabled = true));
    document.querySelector(`.quiz .opt[data-i="${r.answer}"]`).classList.add("right");
    if (!r.correct) b.classList.add("wrong");
    $("#fb").innerHTML = `${r.correct ? "✅ Correct!" : "❌ Not quite."} ${md(r.explain)}`;
    finish();
  }));
  if (already || s.quiz_done) finish();
}

// ---------------------------------------------------------------- init
$("#restartBtn").onclick = async () => {
  if (!confirm("Restart the Python/Spark kernel? Finished steps are replayed automatically.")) return;
  busy("Restarting kernel…"); await api("/api/restart", {}); idle(); openStep(S.step.key, true);
};
$("#resetLabBtn").onclick = async () => {
  if (!confirm(`Uncheck all steps of ${S.lab.label} and start it again?`)) return;
  await api("/api/reset_lab", { lab: S.lab.id });
  S.lab.steps.forEach((s) => { s.done = false; try { localStorage.removeItem(`code:${S.lab.id}:${s.key}`); } catch {} });
  openStep(S.lab.steps[0].key, true);
};

if (window.mermaid) mermaid.initialize({ startOnLoad: false, theme: "base", securityLevel: "loose",
  flowchart: { curve: "basis", htmlLabels: true, padding: 14, nodeSpacing: 40, rankSpacing: 50, wrappingWidth: 260 },
  themeVariables: { fontFamily: "Inter, sans-serif", fontSize: "14px", primaryColor: "#eef3ff", primaryBorderColor: "#9db5f0",
    primaryTextColor: "#141826", lineColor: "#8a93a8", secondaryColor: "#eafaf0", tertiaryColor: "#fff7e8" } });
$("#lightbox").onclick = () => ($("#lightbox").hidden = true);

(async function init() {
  S.labs = await api("/api/labs");
  openLab(store.get("lab", S.labs[0].id));
})();
