"""Local closed-book rehearsal. No correctness/answer key until finish."""
import random
import secrets
import time
from portal.question_bank import load_bank, public_question, check_answer, record_attempt
from portal.knowledge_base import QUESTION_NOTES

ALLOCATION={1:3,2:9,3:10,4:7,5:5,6:4,7:7}

def begin(progress,now=None):
    now=time.time() if now is None else now
    bank=load_bank();rng=random.SystemRandom();questions=[]
    for section,count in ALLOCATION.items():
        pool=[q for q in bank if q['section']==section and q['number'] not in QUESTION_NOTES]
        if len(pool)<count:raise ValueError('Not enough imported questions for this section')
        questions.extend(rng.sample(pool,count))
    rng.shuffle(questions);identifier=secrets.token_urlsafe(18)
    progress.setdefault('mock_exams',{})[identifier]={'ids':[q['id'] for q in questions],
        'answers':{},'started':now,'expires':now+90*60,'finished':False}
    return identifier

def payload(progress,identifier):
    exam=progress.get('mock_exams',{}).get(identifier)
    if exam is None:raise ValueError('Practice exam not found')
    if exam['finished']:return {'id':identifier,'finished':True,'result':exam['result']}
    bank={q['id']:q for q in load_bank()}
    questions=[]
    for key in exam['ids']:
        q=public_question(bank[key],{})
        # A rehearsal supplies no lesson, hints, past attempt or explanation.
        questions.append({k:q[k] for k in ('id','number','q','choices','images','multiple')})
    return {'id':identifier,'finished':False,'expires':exam['expires'],'questions':questions,'answers':exam['answers']}

def save(progress,identifier,key,choices,now=None):
    exam=progress.get('mock_exams',{}).get(identifier)
    if not exam or exam['finished']:raise ValueError('No active practice exam')
    if (time.time() if now is None else now)>=exam['expires']:raise ValueError('Time is over; finish to review your results')
    if key not in exam['ids']:raise ValueError('Question is not part of this practice exam')
    question=next(q for q in load_bank() if q['id']==key)
    if choices!=[]:check_answer(question,choices)
    exam['answers'][key]=choices

def finish(progress,identifier):
    exam=progress.get('mock_exams',{}).get(identifier)
    if not exam:raise ValueError('Practice exam not found')
    if exam['finished']:return exam['result']
    bank={q['id']:q for q in load_bank()};results=[]
    for key in exam['ids']:
        q=bank[key];choices=exam['answers'].get(key,[])
        result=check_answer(q,choices) if choices else {'correct':False,'answers':q['answers'],'explanation':q['explanation']}
        record_attempt(progress,q,choices,result)
        results.append({'id':key,'number':q['number'],'section':q['section'],'topic':q['topic'],
                        'choices':choices,'skipped':not choices,**result})
    exam['finished']=True;exam['finished_at']=time.time()
    exam['result']={'correct':sum(r['correct'] for r in results),'total':45,'results':results,
        'notice':'Scored against the imported suggested key, not a verified Databricks key. This is not a prediction of your certification result.'}
    return exam['result']
