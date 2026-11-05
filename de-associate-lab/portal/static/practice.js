// Section practice stays independent of lab completion and the Spark kernel.
const Practice = { catalog: null, questions: [], index: 0, selected: new Set(), section: null, legacy: false, filter: "all", result: null, busy: false, request: 0,topic:null };
const LAB_SECTIONS = {lab1_ingestion:[2,3],lab2_jobs:[4],lab3_pipelines:[3],lab4_devops:[5],lab5_delta_sql_streaming:[3,6],lab6_transform_tuning:[3],lab7_troubleshooting:[1,6],lab8_cicd_bundles:[5],lab9_governance:[7]};

function practiceShell() {
  document.querySelector("aside").hidden = true;
  document.querySelector(".layout").classList.add("practice-layout");
  document.querySelectorAll("#labtabs .active").forEach(b => b.classList.remove("active"));
}

async function practiceHome() {
  const request = ++Practice.request;
  practiceShell();
  $("#main").innerHTML = '<div class="wrap"><p role="status">Loading section practice…</p></div>';
  try {
    const data = await api("/api/exam/sections");
    if (request !== Practice.request) return;
    Practice.catalog = data;
    const legacy = Practice.legacy;
    const sections = legacy ? data.legacy.map((name, i) => {
      const children = data.sections.filter(s => s.legacy === i + 1);
      return { id:i+1, name, count:children.reduce((n,s)=>n+s.count,0), attempted:children.reduce((n,s)=>n+s.attempted,0), correct:children.reduce((n,s)=>n+s.correct,0), children };
    }) : data.sections;
    $("#main").innerHTML = `<div class="wrap practice-wrap">
      <p class="eyebrow">LEARN → TRY THE LAB → PRACTISE</p><h1>Practise by exam section</h1>
      <p>Learn the ideas behind each question, try the lab, then practise recall.</p>
      <div class="card study-welcome"><h2>New to data engineering? Start here.</h2><p>Begin with the whole picture. Then follow a learning path through each section.</p><div class="btns"><button id="beginnerStart" class="go">Read the beginner introduction →</button><button id="mockStart">45-question closed-book rehearsal</button></div></div>
      <div class="practice-notice">${esc(data.source_notice)} Your PDF has ${data.total} questions. It is a practice bank, not a verified live exam.</div>
      <div class="practice-controls"><label>Group questions by <select id="outlineMode"><option value="current" ${!legacy?'selected':''}>Current exam · 7 sections</option><option value="legacy" ${legacy?'selected':''}>Older outline · 5 sections</option></select></label></div>
      <p>${legacy ? 'The older grouping is a study crosswalk. It does not have current official weights.' : 'Official section percentages describe the exam—not how many questions this imported bank contains.'}</p>
      <div class="section-grid">${sections.map(s=>`<article class="card section-card"><div class="section-label">SECTION ${s.id}${legacy?'':` · ${s.weight}% of the exam`}</div><h2>${esc(s.name)}</h2><p>${s.count} practice questions · ${s.attempted} tried · ${s.correct} last matched the source key${!legacy?` · ${s.due} due for review`:''}</p><progress value="${s.attempted}" max="${s.count||1}" aria-label="Section ${s.id} attempted questions"></progress><div class="btns">${!legacy?`<button class="go" data-study-section="${s.id}">Learn this section first →</button>`:''}<button data-section="${s.id}" ${!s.count?'disabled':''}>Practise this section →</button></div>${legacy?`<small>Maps to current sections ${s.children.map(c=>c.id).join(', ')}.</small>`:''}</article>`).join('')}</div>
      ${!data.total?'<p>No questions imported yet. Run the PDF importer described in README.md.</p>':''}</div>`;
    $("#outlineMode").onchange = e => { Practice.legacy = e.target.value === "legacy"; practiceHome(); };
    document.querySelectorAll("[data-section]").forEach(b=>b.onclick=()=>practiceSection(+b.dataset.section));
    $('#beginnerStart').onclick=studyStart;$('#mockStart').onclick=mockStart;wireStudySections();
  } catch(e) { $("#main").innerHTML=`<div class="wrap"><p role="alert">${esc(e.message)}</p><button id="practiceRetry">Try again</button></div>`; $("#practiceRetry").onclick=practiceHome; }
}

async function practiceSection(section) {
  const request = ++Practice.request;
  try {
    if (!Practice.catalog) Practice.catalog = await api('/api/exam/sections');
    const questions = await api(`/api/exam/questions?${Practice.legacy?'legacy':'section'}=${section}`);
    if (request !== Practice.request) return;
    Practice.section=section; Practice.questions=questions; Practice.filter='all';Practice.topic=null;
    Practice.index=Math.max(0, questions.findIndex(q=>!q.attempt));
    Practice.selected=new Set(); Practice.result=null;
    practiceShell(); practiceQuestion();
  } catch(e) { alert(e.message); }
}

function filteredQuestions() {
  return Practice.questions.filter(q=>(!Practice.topic||q.topic===Practice.topic)&&(Practice.filter==='all'||(Practice.filter==='new'?!q.attempt:Practice.filter==='due'?(q.attempt&&q.attempt.next_review&&q.attempt.next_review<=new Date().toLocaleDateString('en-CA')):q.attempt&&!q.attempt.correct)));
}

function practiceQuestion() {
  const items=filteredQuestions();
  Practice.index=Math.min(Practice.index,Math.max(0,items.length-1));
  const q=items[Practice.index];
  Practice.activeId=q?q.id:null;
  const controls=`<div class="practice-controls"><button id="sectionBack">← All sections</button><label>Show <select id="questionFilter"><option value="all">${Practice.topic?'This topic':'All questions'}</option><option value="new">Not tried yet</option><option value="missed">Last answer missed</option><option value="due">Due for review</option></select></label></div>`;
  if(!q){$("#main").innerHTML=`<div class="wrap">${controls}<div class="card"><h2>No questions in this view</h2><p>Choose All questions to practise again.</p></div></div>`;wirePracticeControls();return;}
  const section=Practice.catalog.sections.find(s=>s.id===q.section);
  $("#main").innerHTML=`<div class="wrap practice-wrap">${controls}
    <p class="eyebrow">SECTION ${q.section} · ${esc(section.name)} · ${section.weight}%</p>
    <h1>Question ${q.number}</h1><p>${Practice.index+1} of ${items.length} in this view · PDF page${q.pages.length>1?'s':''} ${q.pages.join(', ')}${q.attempt?` · Last try: ${q.attempt.correct?'matched the source key':'missed'}`:''}</p>
    ${q.review_note?`<div class="practice-notice"><b>Understand this before memorizing the source answer</b><p>${esc(q.review_note.text)}</p>${q.review_note.url?`<a href="${q.review_note.url}" target="_blank" rel="noopener">Check official documentation</a>`:''}</div>`:''}
    <div class="card concept-brief"><h2>What idea is being tested?</h2><p><b>${esc(q.concept.title)}</b></p><p>${esc(q.concept.decision)}</p><button id="questionLesson">Learn this idea before answering →</button></div>
    <details class="card"><summary>Review the lesson or try the lab first</summary><p>Course references are from your curriculum. Lab steps unlock in order.</p><div class="btns">${section.links.map(([lab,gid,title,lesson])=>`<button data-review-lab="${lab}" data-gid="${gid}">${esc(title)} · lesson ${esc(lesson)}</button>`).join('')}</div></details>
    <div class="card source-question"><h2>Read the question</h2><p class="muted">Original question images preserve code and tables. Answer badges are hidden.</p>${q.images.map(src=>`<img class="question-source" src="${esc(src)}" alt="Original question ${q.number}, including code, tables and answer options">`).join('')}<details><summary>Text version</summary><pre class="question-text">${esc(q.q)}\n\n${q.choices.map(c=>`${c.label}. ${c.text}`).join('\n\n')}</pre></details></div>
    <div class="card quiz"><h2>Your answer</h2><p>${q.multiple?'Choose all correct options.':'Choose one option.'}</p><div id="sourceChoices">${q.choices.map(c=>`<button class="opt" type="button" aria-pressed="${Practice.selected.has(c.label)}" data-answer="${c.label}"><b>${c.label}</b><span>${esc(c.text||'See the question image')}</span></button>`).join('')}</div>
    <button id="checkSourceAnswer" class="go" ${!Practice.selected.size?'disabled':''}>Check answer</button><div id="sourceFeedback" aria-live="polite"></div></div>
    <p class="practice-notice">Suggested answer from Examice, not independently verified. Mapping: ${esc(q.mapping)}. Older outline section ${q.legacy_section}.</p>
    <div class="practice-controls"><button id="previousQuestion" ${!Practice.index?'disabled':''}>← Previous</button><button id="nextQuestion" ${Practice.index===items.length-1?'disabled':''}>Next question →</button></div></div>`;
  wirePracticeControls();
  document.querySelectorAll('[data-answer]').forEach(b=>b.onclick=()=>{
    if(Practice.busy||Practice.result)return;
    const letter=b.dataset.answer;
    if(!q.multiple)Practice.selected.clear();
    if(Practice.selected.has(letter))Practice.selected.delete(letter);else Practice.selected.add(letter);
    document.querySelectorAll('[data-answer]').forEach(x=>x.setAttribute('aria-pressed',String(Practice.selected.has(x.dataset.answer))));
    $('#checkSourceAnswer').disabled=!Practice.selected.size;
  });
  $('#checkSourceAnswer').onclick=async()=>{
    if(Practice.busy)return;
    Practice.busy=true; $('#checkSourceAnswer').disabled=true;
    try{
      const result=await api('/api/exam/answer',{id:q.id,choices:[...Practice.selected]});
      q.attempt={correct:result.correct,next_review:result.next_review};Practice.result=result;
      if(Practice.activeId!==q.id||!$('#sourceFeedback'))return;
      showSourceFeedback(result);
    }catch(e){$('#sourceFeedback').textContent=e.message;$('#checkSourceAnswer').disabled=false;}
    finally{Practice.busy=false;}
  };
  $('#previousQuestion').onclick=()=>movePractice(-1);
  $('#nextQuestion').onclick=()=>movePractice(1);
  $('#questionLesson').onclick=async()=>{await studySection(q.section);const topic=document.getElementById(`topic-${q.topic}`);if(topic){topic.open=true;topic.scrollIntoView({block:'start'});}};
  document.querySelectorAll('[data-review-lab]').forEach(b=>b.onclick=()=>{
    ++Practice.request;
    const lab=S.labs.find(l=>l.id===b.dataset.reviewLab);if(!lab)return;
    document.querySelector('aside').hidden=false;document.querySelector('.layout').classList.remove('practice-layout');
    S.lab=lab;const step=lab.steps.find(s=>s.gid===b.dataset.gid);
    openStep(step?step.key:lab.steps[0].key,true);
  });
}

function showSourceFeedback(result) {
  document.querySelectorAll('[data-answer]').forEach(b=>{
    b.disabled=true;
    if(result.answers.includes(b.dataset.answer))b.classList.add('right');
    else if(Practice.selected.has(b.dataset.answer))b.classList.add('wrong');
  });
  const q=filteredQuestions().find(q=>q.id===Practice.activeId)||Practice.questions.find(q=>q.id===Practice.activeId);
  $('#sourceFeedback').innerHTML=`<h3>${result.correct?'✓ Matches the suggested answer':'Not the source’s suggested answer'}</h3><p>Suggested option${result.answers.length>1?'s':''}: ${result.answers.join(', ')}.</p>${explainedHtml(result)}<h4>Reason through it</h4><p>${esc(q.concept.example)}</p><h4>Why tempting choices can fail</h4><p>${esc(q.concept.trap)}</p><details><summary>Original source explanation · unverified</summary><pre class="question-text">${esc(result.explanation)}</pre></details><p>${esc(q.concept.recall)}</p><p>Next scheduled review: ${esc(result.next_review||'tomorrow')}. Source-key matches measure recall; they do not certify mastery.</p>`;
}
function wirePracticeControls(){
  $('#sectionBack').onclick=practiceHome;
  $('#questionFilter').value=Practice.filter;
  $('#questionFilter').onchange=e=>{Practice.filter=e.target.value;Practice.index=0;Practice.selected=new Set();Practice.result=null;practiceQuestion();};
}
function movePractice(delta){if(Practice.busy)return;const at=filteredQuestions().findIndex(q=>q.id===Practice.activeId);Practice.index=at<0?Practice.index+(delta<0?-1:0):at+delta;Practice.selected=new Set();Practice.result=null;practiceQuestion();$('#main').scrollTop=0;}
$('#practiceBtn').onclick=practiceHome;
window.addSectionPracticeLink=()=>{
  const sections=LAB_SECTIONS[S.lab.id]||[];
  const card=document.createElement('div');card.className='card practice-shortcut';
  card.innerHTML=`<b>Practise this topic</b><div class="btns">${sections.map(n=>`<button data-practise="${n}">Exam section ${n} questions →</button>`).join('')}</div>`;
  const wrap=$('#main .wrap');if(wrap)wrap.prepend(card);
  card.querySelectorAll('button').forEach(b=>b.onclick=()=>{Practice.legacy=false;practiceSection(+b.dataset.practise);});
};

// Plain-language explanation: the idea, why the answer is right, why each other option is wrong.
function explainedHtml(result) {
  const x = result.explained; if (!x) return "";
  const mdi = (t) => (window.marked ? marked.parseInline(t || "") : esc(t));
  const wrong = Object.entries(x.wrong || {}).sort().map(([k, v]) =>
    `<li><span class="opt-badge bad">${esc(k)}</span><span>${mdi(v)}</span></li>`).join("");
  return `<div class="explained">
    <div class="ex-idea"><span>💡</span><div><b>The idea being tested</b><p>${mdi(x.idea)}</p></div></div>
    <div class="ex-why"><span class="opt-badge good">${esc(result.answers.join(", "))}</span><div><b>Why this is the answer</b><p>${mdi(x.why)}</p></div></div>
    ${wrong ? `<div class="ex-wrong"><b>Why the other options are wrong</b><ul>${wrong}</ul></div>` : ""}
    ${x.flag ? `<div class="ex-flag">⚠ <b>Check this:</b> ${mdi(x.flag)}</div>` : ""}
  </div>`;
}
