"""
tests/test_matcher.py

Test Doduo's Matcher class. Validate Matcher's side
of template/pattern matching logic.
"""

import unittest

from Doduo.matcher import Matcher
from Doduo import ConfigException


class DummyTemplate:
    def __init__(self, exact_match=None, children=None):
        self.exact_match = exact_match
        self.children = children or []

    def match(self, candidate):
        if self.exact_match is not None and self.exact_match != candidate.text:
            return False
        for child in self.children:
            matched = False
            for other_child in candidate.children:
                if child.match(other_child) is not None:
                    matched = True
                    break
            if not matched:
                return False
        return [True]


class TestMatcher(unittest.TestCase):
    def test_config_not_found(self):
        failed = False
        try:
            Matcher("does_not_exist.yml")
        except ConfigException as e:
            failed = True
            self.assertEqual(
                str(e),
                "Config file 'does_not_exist.yml' not found or invalid YAML.",
            )
        self.assertTrue(failed)
        failed = False
        try:
            Matcher("beer.yml")
        except ConfigException as e:
            failed = True
        self.assertFalse(failed)

    def test_config_invalid_action(self):
        failed = False
        try:
            Matcher("bad_tests.yml")
        except ConfigException as e:
            failed = True
            self.assertEqual(str(e), "Invalid config option provided.")
        self.assertTrue(failed)

    def test_match(self):
        M = Matcher()

        dummy_root = DummyTemplate(
            "like", [DummyTemplate("I"), DummyTemplate("chocolate")]
        )
        M.templates["test_template"] = [dummy_root]
        self.assertTrue(
            "test_template"
            in next(M.match("I like chocolate", ["test_template"]))
        )
        dummy_root = DummyTemplate(
            "like", [DummyTemplate("chocolate"), DummyTemplate("I")]
        )
        M.templates["test_template"] = [dummy_root]
        self.assertTrue(
            "test_template"
            in next(M.match("I like chocolate", ["test_template"]))
        )
        dummy_root = DummyTemplate("chocolate")
        M.templates["test_template"] = [dummy_root]
        self.assertTrue(
            "test_template"
            in next(M.match("I like chocolate", ["test_template"]))
        )
        dummy_root = DummyTemplate("like")
        M.templates["test_template"] = [dummy_root]
        self.assertTrue(
            "test_template"
            in next(M.match("I like chocolate", ["test_template"]))
        )
        dummy_root = DummyTemplate("asdf")
        M.templates["test_template"] = [dummy_root]
        self.assertFalse(
            "test_template"
            in next(M.match("I like chocolate", ["test_template"]))
        )

        dummy_root = DummyTemplate(
            "I", [DummyTemplate("like"), DummyTemplate("chocolate")]
        )
        M.templates["test_template"] = [dummy_root]
        self.assertFalse(
            "test_template"
            in next(M.match("I like chocolate", ["test_template"]))
        )
        dummy_root = DummyTemplate(
            "chocolate", [DummyTemplate("I"), DummyTemplate("like")]
        )
        M.templates["test_template"] = [dummy_root]
        self.assertFalse(
            "test_template"
            in next(M.match("I like chocolate", ["test_template"]))
        )

    def test_multipattern_match(self):
        dummy_one = DummyTemplate("friend", [DummyTemplate("Hello")])
        dummy_two = DummyTemplate("friend", [DummyTemplate("my")])
        M = Matcher()
        M.templates["test_template"] = [dummy_one, dummy_two]
        self.assertTrue(
            "test_template"
            in next(M.match("Hello my friend", ["test_template"]))
        )
        self.assertTrue(
            "test_template"
            in next(M.match("Hello my friend", ["test_template"]))[
                "__alternatives__"
            ]
        )
        self.assertEqual(
            len(
                next(M.match("Hello my friend", ["test_template"]))[
                    "__alternatives__"
                ]["test_template"]
            ),
            1,
        )

        dummy_one = DummyTemplate("friend", [DummyTemplate("Hello")])
        M = Matcher()
        M.templates["test_template"] = [dummy_one]
        self.assertTrue(
            "test_template"
            in next(M.match("Hello my friend", ["test_template"]))
        )
        self.assertFalse(
            "test_template"
            in next(M.match("Hello my friend", ["test_template"]))[
                "__alternatives__"
            ]
        )

    def test_multiloc_match(self):
        dummy_one = DummyTemplate()
        M = Matcher()
        M.templates["test_template"] = [dummy_one]
        self.assertTrue(
            "test_template"
            in next(M.match("Hello my friend", ["test_template"]))
        )
        self.assertTrue(
            "test_template"
            in next(M.match("Hello my friend", ["test_template"]))[
                "__alternatives__"
            ]
        )
        self.assertEqual(
            len(
                next(M.match("Hello my friend", ["test_template"]))[
                    "__alternatives__"
                ]["test_template"]
            ),
            2,
        )


if __name__ == "__main__":
    unittest.main()
