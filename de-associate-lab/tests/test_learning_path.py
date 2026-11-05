import copy
import unittest
from datetime import date,timedelta
from collections import Counter
from portal.study_topics import topic_index,TOPICS
from portal.study_content import LESSONS
from portal.knowledge_base import section_guide,QUESTION_NOTES
from portal.question_bank import load_bank,record_attempt
from portal.steps import all_labs
from portal import mock_exam

class LearningPathTests(unittest.TestCase):
    def test_every_question_has_a_real_lesson_and_lab(self):
        index=topic_index();self.assertEqual(len(index),280)
        labs={l['id']:l for l in all_labs()}
        for n,t in index.items():
            self.assertIn(t['id'],LESSONS)
            self.assertTrue(all(LESSONS[t['id']]))
            self.assertTrue(any(s['gid']==t['gid'] for s in labs[t['lab']]['steps']),n)
        for section in range(1,8):
            guide=section_guide(section,{})
            self.assertTrue(guide['topics']);self.assertTrue(guide['course_notes'])
        self.assertEqual(load_bank()[83]['topic'],'jobs') # owner is not a permissions question
        self.assertEqual(load_bank()[207]['topic'],'bundles') # permissions word does not override CI/CD

    def test_review_intervals_preserve_existing_progress(self):
        q=load_bank()[0];p={'portal':{'steps':{'saved':{'done':True}}},'lessons':{'old':{'status':'done'}}}
        original=copy.deepcopy(p)
        for days in (1,3,7,14):
            record_attempt(p,q,['C'],{'correct':True})
            self.assertEqual(p['question_bank'][q['id']]['next_review'],(date.today()+timedelta(days=days)).isoformat())
        record_attempt(p,q,['A'],{'correct':False})
        self.assertEqual(p['question_bank'][q['id']]['streak'],0)
        self.assertEqual(p['portal'],original['portal']);self.assertEqual(p['lessons'],original['lessons'])

    def test_mock_blueprint_and_no_feedback_before_finish(self):
        p={};identifier=mock_exam.begin(p,now=1000)
        data=mock_exam.payload(p,identifier)
        self.assertEqual(len(data['questions']),45)
        self.assertEqual(len({q['id'] for q in data['questions']}),45)
        bank={q['id']:q for q in load_bank()}
        self.assertEqual(Counter(bank[q['id']]['section'] for q in data['questions']),Counter(mock_exam.ALLOCATION))
        for q in data['questions']:
            self.assertFalse({'answers','explanation','concept','attempt'}&set(q))
            self.assertNotIn(q['number'],QUESTION_NOTES)
        first=data['questions'][0]
        mock_exam.save(p,identifier,first['id'],bank[first['id']]['answers'],now=1010)
        self.assertNotIn('question_bank',p)
        with self.assertRaises(ValueError):mock_exam.save(p,identifier,first['id'],['A'],now=10000)
        result=mock_exam.finish(p,identifier)
        self.assertEqual(result['correct'],1);self.assertEqual(result['total'],45)
        snapshot=copy.deepcopy(p['question_bank']);mock_exam.finish(p,identifier)
        self.assertEqual(p['question_bank'],snapshot)
        self.assertTrue(mock_exam.payload(p,identifier)['finished'])

if __name__=='__main__':unittest.main()
