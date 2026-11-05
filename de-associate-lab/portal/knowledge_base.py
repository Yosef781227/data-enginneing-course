"""Learning paths built from the manually assigned question topics and local course notes."""
from pathlib import Path
from portal.study_topics import TOPICS
from portal.study_content import FOUNDATIONS, INTRO, LESSONS
from portal.exam_sections import SECTIONS

ROOT=Path(__file__).resolve().parents[1]
NOTES={1:['notes/c1-ingestion.md','notes/extra-exam-topics.md'],2:['notes/c1-ingestion.md'],
       3:['notes/c3-pipelines.md','notes/extra-exam-topics.md'],4:['notes/c2-jobs.md'],
       5:['notes/c4-devops.md'],6:['notes/extra-exam-topics.md','notes/c2-jobs.md'],7:['notes/extra-exam-topics.md']}
REFERENCES={
 'outline':'https://www.databricks.com/learn/certification/data-engineer-associate',
 'guide':'https://www.databricks.com/sites/default/files/2026-05/databricks-certified-data-engineer-associate-exam-guide-may-2026.pdf',
 'autoloader':'https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/schema',
 'sharing':'https://docs.databricks.com/aws/en/delta-sharing/',
}
QUESTION_NOTES={
 109:{'text':'The bank gives a different rationale from the near-duplicate Q58. Parquet carries schema metadata; do not memorize this conflicting source key as established fact.', 'url':'https://spark.apache.org/docs/latest/sql-data-sources-parquet.html'},
 149:{'text':'The closest offered choice describes a local environment, but the important technical point is remote Spark execution through Databricks Connect. Do not learn that Connect reproduces a complete cluster on your laptop.', 'url':'https://docs.databricks.com/aws/en/dev-tools/databricks-connect/'},
 153:{'text':'This question asks for a platform output-size limit. Such limits depend on the execution/output context and can change. Verify the relevant current limit rather than memorizing the number from this bank.', 'url':None},
 255:{'text':'This answer skips an operational detail: under default addNewColumns behaviour Auto Loader can update the schema, stop with UnknownFieldException, then resume after restart. The configured evolution mode matters.', 'url':REFERENCES['autoloader']},
 279:{'text':'Option A in the imported source is printed with a malformed spaced operator. The null-safe equality operator is <=>, without spaces inside it. The example needs this correction before it is executable.', 'url':'https://spark.apache.org/docs/latest/sql-ref-null-semantics.html'},
}

def concept(topic):
    section,title,numbers,lab,gid=TOPICS[topic]
    analogy,decision,example,trap,recall,recall_answer=LESSONS[topic]
    return dict(id=topic,section=section,title=title,numbers=numbers,lab=lab,gid=gid,
                analogy=analogy,decision=decision,example=example,trap=trap,recall=recall,recall_answer=recall_answer)

def overview():
    return {'title':'Understand first. Practise second. Remember through review.', 'read':FOUNDATIONS,
            'verified_on':'2026-11-03', 'references':REFERENCES,
            'allocation':[3,9,10,7,5,4,7], 'sections':SECTIONS}

def section_guide(section,progress):
    if section not in range(1,8):
        raise ValueError('Unknown study section')
    headline,explanation,readiness=INTRO[section]
    topics=[]
    for key,values in TOPICS.items():
        if values[0]!=section:continue
        item=concept(key)
        item['self_checked']=bool(progress.get('study_topics',{}).get(key,{}).get('understood'))
        topics.append(item)
    notes=[{'path':p,'text':(ROOT/p).read_text()} for p in NOTES[section] if (ROOT/p).exists()]
    return {**SECTIONS[section-1], 'headline':headline,'introduction':explanation,'readiness':readiness,
            'topics':topics,'course_notes':notes,'references':REFERENCES}

def export_knowledge_base():
    folder=ROOT/'notes/knowledge-base';folder.mkdir(exist_ok=True)
    (folder/'00-start-here.md').write_text(FOUNDATIONS)
    for section in range(1,8):
        g=section_guide(section,{})
        text=[f"# Section {section}: {g['name']} — {g['weight']}%",g['headline'],g['introduction'],g['readiness']]
        for t in g['topics']:
            text += [f"\n## {t['title']}",f"**Questions:** {', '.join(map(str,t['numbers']))}",
                     f"**Think of it like this:** {t['analogy']}",f"**What the question tests:** {t['decision']}",
                     f"**Example:** {t['example']}",f"**Common trap:** {t['trap']}",
                     f"**Try the lab:** {t['lab']} / {t['gid']} (some platform features are simulated)",
                     f"**Explain without looking:** {t['recall']}",f"**Self-check:** {t['recall_answer']}"]
        text+=['\n## Sources','Local curriculum: ../../curriculum.md; official objective map: ../exam-guide-map.md',
               'Current exam outline: '+REFERENCES['outline'],'Post-May 2026 guide: '+REFERENCES['guide'],
               'These learning explanations do not independently certify the third-party answer key.']
        (folder/f'{section:02}-section.md').write_text('\n\n'.join(text)+'\n')
    from portal.study_topics import topic_index
    rows=['# Question-by-question learning map','',
          'All 280 questions are assigned by the concept/decision being tested. This is a study crosswalk, not an official question-to-domain mapping or answer-key certification.','',
          '| PDF question | Current section | Learning topic | Related lab |','|---|---|---|---|']
    rows += [f"| {n} | {t['section']} | {t['title']} | {t['lab']} / {t['gid']} |" for n,t in sorted(topic_index().items())]
    (ROOT/'notes/examice-section-map.md').write_text('\n'.join(rows)+'\n')
