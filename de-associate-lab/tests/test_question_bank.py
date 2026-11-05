import unittest
from pathlib import Path
from portal.question_bank import load_bank, public_question, check_answer, catalog
from portal.exam_sections import SECTIONS
from portal.steps import all_labs
from scripts.import_examice import parse_question

class QuestionBankTests(unittest.TestCase):
    def test_complete_import_and_answers(self):
        questions = load_bank()
        self.assertEqual([q["number"] for q in questions], list(range(1, 281)))
        for q in questions:
            self.assertIn(q["section"], range(1,8))
            self.assertTrue(q["answers"], q["id"])
            self.assertTrue(set(q["answers"]) <= {c["label"] for c in q["choices"]}, q["id"])
            self.assertTrue(q["images"], q["id"])
            for image in q["images"]:
                self.assertTrue((Path("portal/static") / image.lstrip("/")).is_file())

    def test_no_answer_leak_in_question_payload(self):
        for q in load_bank():
            public = public_question(q, {})
            self.assertNotIn("answers", public)
            self.assertNotIn("explanation", public)
            self.assertNotIn("CORRECT", public["q"])
            self.assertFalse(any("CORRECT" in c["text"] for c in public["choices"]))

    def test_answer_validation(self):
        q = {"choices":[{"label":"A"},{"label":"B"},{"label":"C"}], "answers":["A","C"], "explanation":"Source explanation", "answer_status":"unverified"}
        self.assertTrue(check_answer(q,["C","A"])["correct"])
        self.assertFalse(check_answer(q,["A"])["correct"])
        for value in ([], ["X"], ["A","A"], None, "A"):
            with self.assertRaises(ValueError):
                check_answer(q,value)

    def test_section_links_and_totals(self):
        labs={l["id"]:l for l in all_labs()}
        for s in SECTIONS:
            for lab,gid,*_ in s["links"]:
                self.assertTrue(any(step["gid"]==gid for step in labs[lab]["steps"]))
        self.assertEqual(sum(s["weight"] for s in SECTIONS),100)
        data=catalog({})
        self.assertEqual(sum(s["count"] for s in data["sections"]),280)
        self.assertEqual(sum(s["attempted"] for s in data["sections"]),0)
        self.assertEqual(catalog({"question_bank":{load_bank()[0]["id"]:{"correct":True}}})["sections"][load_bank()[0]["section"]-1]["correct"],1)

    def test_multi_answer_parser(self):
        q=parse_question(1,[(0,0,"QUESTION 1\nChoose two options.\nA\nFirst\nB\nSecond\nC\nThird\nSUGGESTED ANSWER\nThe suggested answer is A and C.\nExplanation.")])
        self.assertEqual(q["answers"],["A","C"])
        self.assertEqual([c["text"] for c in q["choices"]],["First","Second","Third"])

    def test_article_a_is_not_an_answer_label(self):
        q=parse_question(9,[(0,0,"QUESTION 9\nA data engineer wants to join tables.\nWhich join?\nA\nInner join\nB\nLeft join\nSUGGESTED ANSWER\nThe suggested answer is A.")])
        self.assertTrue(q["q"].startswith("A data engineer"))
        self.assertEqual(len(q["choices"]),2)

if __name__ == "__main__":
    unittest.main()
