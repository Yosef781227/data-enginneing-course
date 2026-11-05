// The teaching layer: orientation -> concept -> lab -> recall -> question practice.
async function studyStart(){
  ++Practice.request;practiceShell();
  try{
    const data=await api('/api/study/overview');
    $('#main').innerHTML=`<div class="wrap practice-wrap"><button id="studyBack">← Sections</button><p class="eyebrow">YOUR BEGINNER KNOWLEDGE BASE</p><h1>Understand first. Practise second.</h1><div class="study-flow"><span>1 · Learn the idea</span><span>2 · Try the lab</span><span>3 · Explain it</span><span>4 · Answer questions</span><span>5 · Review later</span></div><article class="card learn">${md(data.read)}</article><div class="card"><h2>Your seven learning sections</h2><div class="btns">${data.sections.map(s=>`<button data-study-section="${s.id}">${s.id}. ${esc(s.name)} · ${s.weight}%</button>`).join('')}</div></div><p>Exam outline checked ${esc(data.verified_on)}. <a href="${data.references.outline}" target="_blank" rel="noopener">Official exam page</a> · <a href="${data.references.guide}" target="_blank" rel="noopener">Post-May 2026 guide</a></p></div>`;
    $('#studyBack').onclick=practiceHome;wireStudySections();
  }catch(e){alert(e.message);}
}
function wireStudySections(){document.querySelectorAll('[data-study-section]').forEach(b=>b.onclick=()=>studySection(+b.dataset.studySection));}
function openStudyLab(labId,gid){
  const lab=S.labs.find(l=>l.id===labId);if(!lab)return;
  document.querySelector('aside').hidden=false;document.querySelector('.layout').classList.remove('practice-layout');
  S.lab=lab;const step=lab.steps.find(s=>s.gid===gid);openStep(step?step.key:lab.steps[0].key,true);
}
async function studySection(id){
  ++Practice.request;practiceShell();
  try{
    const g=await api(`/api/study/section?id=${id}`);
    $('#main').innerHTML=`<div class="wrap practice-wrap"><div class="practice-controls"><button id="guideBack">← All sections</button><button id="guideStart">Beginner introduction</button></div><p class="eyebrow">SECTION ${g.id} · ${g.weight}% OF THE EXAM</p><h1>${esc(g.name)}</h1><div class="card"><h2>${esc(g.headline)}</h2><p>${esc(g.introduction)}</p><h3>Before you practise, you should be able to…</h3><p>${esc(g.readiness)}</p></div><p>Work through one topic at a time. The numbers below are your PDF question numbers, not predicted live-exam questions.</p>
    ${g.topics.map((t,i)=>`<details class="card study-topic" ${i===0?'open':''} id="topic-${t.id}"><summary>${i+1}. ${esc(t.title)} <small>· ${t.numbers.length} linked questions${t.self_checked?' · self-checked':''}</small></summary><div class="analogy"><div class="analogy-icon">💡</div><p>${esc(t.analogy)}</p></div><h3>What these questions are testing</h3><p>${esc(t.decision)}</p><h3>A small example</h3><p>${esc(t.example)}</p><h3>A common wrong turn</h3><p>${esc(t.trap)}</p><div class="btns"><button data-study-lab="${t.lab}" data-gid="${t.gid}">Try the related lab →</button></div><p class="muted">These labs may simulate Databricks-only features. Follow the lab notes for real-platform practice. Lab steps still unlock in order.</p><h3>Close the explanation and say it yourself</h3><p>${esc(t.recall)}</p><textarea class="recall-note" data-reflection="${t.id}" placeholder="Explain it in your own words. This note stays in this browser." aria-label="Your explanation of ${esc(t.title)}"></textarea><details><summary>Compare with a short explanation</summary><p>${esc(t.recall_answer)}</p></details><label class="study-check"><input type="checkbox" data-understood="${t.id}" ${t.self_checked?'checked':''}> I can explain this without looking <span role="status" data-save-state="${t.id}"></span></label><p>PDF questions: ${t.numbers.join(', ')}.</p><button class="go" data-topic-practice="${t.id}" data-section="${g.id}">Practise these ${t.numbers.length} questions →</button></details>`).join('')}
    <details class="card"><summary>Full supporting course notes</summary><p>These are your existing course notes, not a new answer key.</p>${g.course_notes.map(n=>`<details><summary>${esc(n.path)}</summary><div class="learn">${md(n.text)}</div></details>`).join('')}</details><div class="card"><h2>Ready for this section?</h2><p>Practise the questions after you can explain the ideas. Match the requirement to the behaviour—not the option letter.</p><button id="guidePractice" class="go">Practise the whole section →</button></div></div>`;
    $('#guideBack').onclick=practiceHome;$('#guideStart').onclick=studyStart;
    $('#guidePractice').onclick=()=>{Practice.legacy=false;Practice.topic=null;practiceSection(id);};
    document.querySelectorAll('[data-study-lab]').forEach(b=>b.onclick=()=>openStudyLab(b.dataset.studyLab,b.dataset.gid));
    document.querySelectorAll('[data-topic-practice]').forEach(b=>b.onclick=async()=>{Practice.legacy=false;await practiceSection(+b.dataset.section);Practice.topic=b.dataset.topicPractice;Practice.index=0;practiceQuestion();});
    document.querySelectorAll('[data-understood]').forEach(c=>c.onchange=async()=>{
      const status=document.querySelector(`[data-save-state="${c.dataset.understood}"]`);
      try{await api('/api/study/topic',{topic:c.dataset.understood,understood:c.checked});status.textContent='Saved';}
      catch(e){c.checked=!c.checked;status.textContent=e.message;}
    });
    document.querySelectorAll('[data-reflection]').forEach(t=>{t.value=store.get(`reflection:${t.dataset.reflection}`,'');t.oninput=()=>store.set(`reflection:${t.dataset.reflection}`,t.value);});
    $('#main').scrollTop=0;
  }catch(e){alert(e.message);}
}
