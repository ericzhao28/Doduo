"""
tests/test_template.py

Test Doduo's Template class. Validate pattern matching and slot parsing logic.
"""

import unittest
import pdb

from Doduo.template import Template
from Doduo.matcher import Matcher


class TestTemplate(unittest.TestCase):
    def test_children(self):
        M = Matcher()
        t = Template(
            children=[Template(exact_match=["friend"])], exact_match=["Hello"]
        )
        M.templates["test_template"] = [t]
        self.assertTrue(
            "test_template"
            in next(M.match("Hello my friend", ["test_template"]))
        )

        t = Template(
            children=[Template(exact_match=["Hello"])], exact_match=["friend"]
        )
        M.templates["test_template"] = [t]
        self.assertFalse(
            "test_template"
            in next(M.match("Hello my friend", ["test_template"]))
        )

    def test_optional_match(self):
        M = Matcher()
        t = Template(
            children=[
                Template(exact_match=["friend"]),
                Template(exact_match=["asdf"], optional=False),
            ],
            exact_match=["Hello"],
        )
        M.templates["test_template"] = [t]
        self.assertFalse(
            "test_template"
            in next(M.match("Hello my friend", ["test_template"]))
        )
        t = Template(
            children=[
                Template(exact_match=["friend"]),
                Template(exact_match=["asdf"], optional=True),
            ],
            exact_match=["Hello"],
        )
        M.templates["test_template"] = [t]
        self.assertTrue(
            "test_template"
            in next(M.match("Hello my friend", ["test_template"]))
        )

    def test_pos_match(self):
        M = Matcher()
        t = Template(
            children=[Template(exact_match=["friend"])], exact_match=["Goodbye"]
        )
        M.templates["test_template"] = [t]
        self.assertFalse(
            "test_template"
            in next(M.match("Hello my friend", ["test_template"]))
        )

        t = Template(
            children=[Template(exact_match=["friend"])],
            exact_match=["Goodbye"],
            pos_match=["noun"],
        )
        M.templates["test_template"] = [t]
        self.assertFalse(
            "test_template"
            in next(M.match("Hello my friend", ["test_template"]))
        )

        t = Template(
            children=[Template(exact_match=["friend"])],
            exact_match=["Goodbye"],
            pos_match=["noun", "intj"],
        )
        M.templates["test_template"] = [t]
        self.assertTrue(
            "test_template"
            in next(M.match("Hello my friend", ["test_template"]))
        )

        t = Template(
            children=[Template(exact_match=["friend"])],
            exact_match=["Goodbye"],
            pos_match=["intj"],
        )
        M.templates["test_template"] = [t]
        self.assertTrue(
            "test_template"
            in next(M.match("Hello my friend", ["test_template"]))
        )

        t = Template(
            children=[Template(exact_match=["friend"])], pos_match=["noun"]
        )
        M.templates["test_template"] = [t]
        self.assertFalse(
            "test_template"
            in next(M.match("Hello my friend", ["test_template"]))
        )

        t = Template(
            children=[Template(exact_match=["friend"])], pos_match=["intj"]
        )
        M.templates["test_template"] = [t]
        self.assertTrue(
            "test_template"
            in next(M.match("Hello my friend", ["test_template"]))
        )

    def test_ner_match(self):
        M = Matcher()
        t = Template(children=[Template()], exact_match=["friend"])
        M.templates["test_template"] = [t]
        self.assertTrue(
            "test_template"
            in next(M.match("Hello my friend", ["test_template"]))
        )

        t = Template(
            children=[Template(exact_match=["bleh"])], exact_match=["friend"]
        )
        M.templates["test_template"] = [t]
        self.assertFalse(
            "test_template"
            in next(M.match("Hello my friend", ["test_template"]))
        )

    def test_case_sensitive(self):
        M = Matcher()
        t = Template(
            children=[Template(exact_match=["friend"])], exact_match=["hello"]
        )
        M.templates["test_template"] = [t]
        self.assertTrue(
            "test_template"
            in next(M.match("Hello my friend", ["test_template"]))
        )

        M = Matcher()
        t = Template(
            children=[Template(exact_match=["friend"])],
            exact_match=["hello"],
            case_sensitive=True,
        )
        M.templates["test_template"] = [t]
        self.assertFalse(
            "test_template"
            in next(M.match("Hello my friend", ["test_template"]))
        )

        M = Matcher()
        t = Template(
            children=[Template(exact_match=["friend"])], exact_match=["HELLO"]
        )
        M.templates["test_template"] = [t]
        self.assertTrue(
            "test_template"
            in next(M.match("Hello my friend", ["test_template"]))
        )

        t = Template(
            children=[Template(exact_match=["friend"])],
            exact_match=["HELLO"],
            case_sensitive=True,
        )
        M.templates["test_template"] = [t]
        self.assertFalse(
            "test_template"
            in next(M.match("Hello my friend", ["test_template"]))
        )

    def test_rel_match(self):
        M = Matcher()
        t = Template(children=[Template(rels=["nsubj"])], exact_match=["hello"])
        M.templates["test_template"] = [t]
        self.assertFalse(
            "test_template"
            in next(M.match("Hello my friend", ["test_template"]))
        )

        t = Template(children=[Template(rels=["intj"])], exact_match=["hello"])
        M.templates["test_template"] = [t]
        self.assertTrue(
            "test_template"
            in next(M.match("Hello my friend", ["test_template"]))
        )

        t = Template(
            children=[Template(rels=["nsubj"], exact_match=["friend"])],
            exact_match=["hello"],
        )
        M.templates["test_template"] = [t]
        self.assertFalse(
            "test_template"
            in next(M.match("Hello my friend", ["test_template"]))
        )

        t = Template(
            children=[Template(rels=["intj"], exact_match=["friend"])],
            exact_match=["hello"],
        )
        M.templates["test_template"] = [t]
        self.assertTrue(
            "test_template"
            in next(M.match("Hello my friend", ["test_template"]))
        )

        t = Template(
            children=[Template(rels=["nsubj"], exact_match=["friends"])],
            exact_match=["hello"],
        )
        M.templates["test_template"] = [t]
        self.assertFalse(
            "test_template"
            in next(M.match("Hello my friend", ["test_template"]))
        )

        t = Template(
            children=[Template(rels=["intj"], exact_match=["friends"])],
            exact_match=["hello"],
        )
        M.templates["test_template"] = [t]
        self.assertFalse(
            "test_template"
            in next(M.match("Hello my friend", ["test_template"]))
        )

    def test_soft_match(self):
        M = Matcher()
        t = Template(
            children=[Template(exact_match=["friend"])],
            soft_match=["goodbye", "hey", "hi", "bye"],
        )
        M.templates["test_template"] = [t]
        self.assertTrue(
            "test_template"
            in next(M.match("Hello my friend", ["test_template"]))
        )

        t = Template(
            children=[Template(exact_match=["friend"])],
            soft_match=["fruit", "apple"],
        )
        M.templates["test_template"] = [t]
        self.assertFalse(
            "test_template"
            in next(M.match("Hello my friend", ["test_template"]))
        )

    def test_ner_match(self):
        M = Matcher()
        t = Template(
            children=[Template(exact_match=["eh"], ner_match=["language"])],
            exact_match=["speak"],
        )
        M.templates["test_template"] = [t]
        self.assertTrue(
            "test_template"
            in next(M.match("Do you speak English?", ["test_template"]))
        )

        t = Template(
            children=[Template(exact_match=["eh"], ner_match=["person"])],
            exact_match=["speak"],
        )
        M.templates["test_template"] = [t]
        self.assertFalse(
            "test_template"
            in next(M.match("Do you speak English?", ["test_template"]))
        )

        t = Template(
            children=[Template(ner_match=["person"])], exact_match=["speak"]
        )
        M.templates["test_template"] = [t]
        self.assertFalse(
            "test_template"
            in next(M.match("Do you speak English?", ["test_template"]))
        )

        t = Template(
            children=[Template(ner_match=["language"])], exact_match=["speak"]
        )
        M.templates["test_template"] = [t]
        self.assertTrue(
            "test_template"
            in next(M.match("Do you speak English?", ["test_template"]))
        )

        t = Template(children=[Template()], exact_match=["speak"])
        M.templates["test_template"] = [t]
        self.assertTrue(
            "test_template"
            in next(M.match("Do you speak English?", ["test_template"]))
        )

    def test_slotting(self):
        M = Matcher()
        t = Template(
            children=[Template(slot_name="lang", ner_match=["language"])],
            exact_match=["speak"],
        )
        M.templates["test_template"] = [t]
        self.assertTrue(
            "test_template"
            in next(M.match("Do you speak English?", ["test_template"]))
        )
        self.assertEqual(
            next(M.match("Do you speak English?", ["test_template"]))[
                "test_template"
            ]["lang"],
            ["English"],
        )
        self.assertEqual(
            next(M.match("Do you speak English?", ["test_template"]))[
                "__alternatives__"
            ],
            {},
        )

    def test_multiple_slot_values(self):
        M = Matcher()
        t = Template(
            children=[Template(slot_name="lang", ner_match=["language"])],
            exact_match=["speak"],
            slot_name="lang",
        )
        M.templates["test_template"] = [t]
        self.assertTrue(
            "test_template"
            in next(
                M.match(
                    "Do you speak English or do you speak Chinese?",
                    ["test_template"],
                )
            )
        )
        self.assertEqual(
            next(
                M.match(
                    "Do you speak English or do you speak Chinese?",
                    ["test_template"],
                )
            )["test_template"]["lang"],
            ["speak", "English"],
        )
        self.assertEqual(
            next(
                M.match(
                    "Do you speak English or do you speak Chinese?",
                    ["test_template"],
                )
            )["__alternatives__"],
            {"test_template": [{"lang": ["speak", "Chinese"]}]},
        )
        self.assertTrue(
            "test_template"
            in next(M.match("Do you speak English?", ["test_template"]))
        )
        self.assertEqual(
            next(M.match("Do you speak English?", ["test_template"]))[
                "test_template"
            ]["lang"],
            ["speak", "English"],
        )
        self.assertEqual(
            next(M.match("Do you speak English?", ["test_template"]))[
                "__alternatives__"
            ],
            {},
        )

    def test_multimatch_slot_alts(self):
        M = Matcher()
        t = Template(
            children=[Template(slot_name="lang", ner_match=["language"])],
            exact_match=["speak"],
        )
        M.templates["test_template"] = [t]
        self.assertTrue(
            "test_template"
            in next(
                M.match(
                    "Do you speak English or do you speak Chinese?",
                    ["test_template"],
                )
            )
        )
        self.assertEqual(
            next(
                M.match(
                    "Do you speak English or do you speak Chinese?",
                    ["test_template"],
                )
            )["test_template"]["lang"],
            ["English"],
        )
        self.assertEqual(
            next(
                M.match(
                    "Do you speak English or do you speak Chinese?",
                    ["test_template"],
                )
            )["__alternatives__"],
            {"test_template": [{"lang": ["Chinese"]}]},
        )

    def test_optional_slot_alts(self):
        M = Matcher()
        t = Template(
            children=[
                Template(
                    slot_name="lang", ner_match=["language"], optional=True
                )
            ],
            exact_match=["speak"],
            slot_name="lang",
        )
        M.templates["test_template"] = [t]
        # pdb.set_trace()
        self.assertTrue(
            "test_template"
            in next(M.match("Do you speak English?", ["test_template"]))
        )
        self.assertEqual(
            next(M.match("Do you speak English?", ["test_template"]))[
                "test_template"
            ]["lang"],
            ["speak", "English"],
        )
        self.assertEqual(
            next(M.match("Do you speak English?", ["test_template"]))[
                "__alternatives__"
            ],
            {"test_template": [{"lang": ["speak"]}]},
        )

    def test_multi_optional_slot_alts(self):
        M = Matcher()
        t = Template(
            children=[
                Template(
                    slot_name="lang", ner_match=["language"], optional=True
                )
            ],
            exact_match=["speak"],
            slot_name="lang",
        )
        M.templates["test_template"] = [t]
        self.assertTrue(
            "test_template"
            in next(
                M.match(
                    "Do you speak English or do you speak Chinese?",
                    ["test_template"],
                )
            )
        )
        self.assertEqual(
            next(
                M.match(
                    "Do you speak English or do you speak Chinese?",
                    ["test_template"],
                )
            )["test_template"]["lang"],
            ["speak", "English"],
        )
        self.assertEqual(
            next(
                M.match(
                    "Do you speak English or do you speak Chinese?",
                    ["test_template"],
                )
            )["__alternatives__"],
            {
                "test_template": [
                    {"lang": ["speak"]},
                    {"lang": ["speak", "Chinese"]},
                    {"lang": ["speak"]},
                ]
            },
        )


if __name__ == "__main__":
    unittest.main()
