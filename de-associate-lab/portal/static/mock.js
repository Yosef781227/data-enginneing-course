const Mock={exam:null,index:0,timer:null,busy:false};
async function mockStart(){
  try{
    const id=store.get('active-mock',null);
    let exam=null;
    if(id){try{const prior=await api(`/api/mock?id=${encodeURIComponent(id)}`);if(!prior.finished)exam=prior;}catch{}}
    if(!exam){
      if(!confirm('Start a 45-question, 90-minute closed-book practice? Answers and lesson hints appear only after you finish. It is scored against the unverified imported key, not a prediction of the real exam.'))return;
      exam=await api('/api/mock/start',{});store.set('active-mock',exam.id);
    }
    Mock.exam=exam;Mock.index=0;++Practice.request;practiceShell();
    if(Mock.timer)clearInterval(Mock.timer);
    Mock.timer=setInterval(mockTick,1000);mockRender();mockTick();
  }catch(e){alert(e.message);}
}
function mockTick(){
  const el=$('#mockClock');
  if(!el){clearInterval(Mock.timer);return;}
  const remaining=Math.max(0,Math.ceil(Mock.exam.expires-Date.now()/1000));
  el.textContent=`${Math.floor(remaining/60)}:${String(remaining%60).padStart(2,'0')} left`;
  if(!remaining&&!Mock.busy)mockFinish(true);
}
function mockRender(){
  const exam=Mock.exam,q=exam.questions[Mock.index],selected=exam.answers[q.id]||[];
  const answered=Object.values(exam.answers).filter(a=>a.length).length;
  $('#main').innerHTML=`<div class="wrap practice-wrap"><div class="practice-controls"><button id="mockPauseView">Leave view · timer keeps running</button><strong class="mock-timer" id="mockClock" role="timer"></strong></div><p class="eyebrow">CLOSED-BOOK REHEARSAL · NO HINTS OR ANSWER FEEDBACK</p><h1>Question ${Mock.index+1} of 45</h1><p>${answered} answered · ${45-answered} unanswered. Returning to this view resumes the same timer.</p><div class="card">${q.images.map(src=>`<img class="question-source" src="${esc(src)}" alt="Practice question ${Mock.index+1}">`).join('')}<details><summary>Question text</summary><pre class="question-text">${esc(q.q)}</pre></details></div><div class="card quiz"><p>${q.multiple?'Choose all applicable options.':'Choose one option.'}</p>${q.choices.map(c=>`<button type="button" class="opt" data-mock-answer="${c.label}" aria-pressed="${selected.includes(c.label)}"><b>${c.label}</b><span>${esc(c.text)}</span></button>`).join('')}<p id="mockSaveState" role="status">${selected.length?'Answer saved':'Not answered yet'}</p></div><div class="practice-controls"><button id="mockPrev" ${Mock.index===0?'disabled':''}>← Previous</button><button id="mockNext" ${Mock.index===44?'disabled':''}>Next →</button><button id="mockFinish" class="go">Finish and review</button></div></div>`;
  document.querySelectorAll('[data-mock-answer]').forEach(b=>b.onclick=async()=>{
    if(Mock.busy)return;
    const old=exam.answers[q.id]||[];const values=q.multiple?new Set(old):new Set();
    if(q.multiple&&values.has(b.dataset.mockAnswer))values.delete(b.dataset.mockAnswer);else values.add(b.dataset.mockAnswer);
    Mock.busy=true;
    try{
      await api('/api/mock/save',{id:exam.id,question:q.id,choices:[...values]});exam.answers[q.id]=[...values];
      document.querySelectorAll('[data-mock-answer]').forEach(x=>x.setAttribute('aria-pressed',String(values.has(x.dataset.mockAnswer))));
      $('#mockSaveState').textContent='Answer saved';
    }catch(e){$('#mockSaveState').textContent=e.message;}finally{Mock.busy=false;}
  });
  $('#mockPrev').onclick=()=>{if(!Mock.busy){Mock.index--;mockRender();mockTick();}};
  $('#mockNext').onclick=()=>{if(!Mock.busy){Mock.index++;mockRender();mockTick();}};
  $('#mockFinish').onclick=()=>mockFinish(false);
  $('#mockPauseView').onclick=practiceHome;
  mockTick();$('#main').scrollTop=0;
}
async function mockFinish(expired){
  if(Mock.busy)return;
  if(!expired&&!confirm('Finish now? Unanswered questions will be counted as missed.'))return;
  Mock.busy=true;
  try{
    const result=await api('/api/mock/finish',{id:Mock.exam.id});clearInterval(Mock.timer);store.set('active-mock',null);
    $('#main').innerHTML=`<div class="wrap practice-wrap"><button id="mockResultBack">← Learning sections</button><h1>${expired?'Time is up':'Practice complete'}</h1><h2>${result.correct} / ${result.total} matched the source key</h2><p class="practice-notice">${esc(result.notice)}</p><p>Review missed concepts, explain the rule in your own words, then retry after a delay.</p>${result.results.map((r,i)=>`<details class="card"><summary>${i+1}. PDF question ${r.number} · ${r.skipped?'Not answered':r.correct?'Matched source key':'Review needed'}</summary><p>Your choices: ${r.choices.join(', ')||'none'}. Source suggested: ${r.answers.join(', ')}.</p><pre class="question-text">${esc(r.explanation)}</pre><button data-mock-learn="${r.section}" data-topic="${r.topic}">Relearn this concept →</button></details>`).join('')}</div>`;
    $('#mockResultBack').onclick=practiceHome;
    document.querySelectorAll('[data-mock-learn]').forEach(b=>b.onclick=async()=>{await studySection(+b.dataset.mockLearn);const t=document.getElementById(`topic-${b.dataset.topic}`);if(t){t.open=true;t.scrollIntoView({block:'start'});}});
  }catch(e){alert(e.message);}finally{Mock.busy=false;}
}
