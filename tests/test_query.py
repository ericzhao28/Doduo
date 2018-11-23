"""
tests/test_query.py

Test Doduo's Query class. Validate query tree build process.
"""

import unittest

from Doduo.query import parse_query


class TestQuery(unittest.TestCase):
    def test_sentence_frag(self):
        parsed = parse_query(
            "Hello there General Kenobi. This should be two sentences."
        )
        self.assertEqual(len(parsed), 2)

    def test_attrs(self):
        kenobi_node = parse_query(
            "Hello there General Kenobi. This should be two sentences."
        )[0][0]
        hello_node = None
        for child in kenobi_node.children:
            if child.text == "Hello":
                hello_node = child
        self.assertNotEqual(hello_node, None)
        self.assertEqual(hello_node.pos, "intj")
        self.assertEqual(hello_node.ner, ["", "intj"])
        self.assertEqual(hello_node.text, "Hello")
        self.assertEqual(hello_node.rel, "intj")

        self.assertEqual(kenobi_node.pos, "propn")
        self.assertEqual(kenobi_node.ner, ["person", "propn"])
        self.assertEqual(kenobi_node.text, "Kenobi")

        general_node = None
        for child in kenobi_node.children:
            if child.text == "General":
                general_node = child
        self.assertNotEqual(general_node, None)

    def test_get_compound(self):
        kenobi_node = parse_query(
            "Hello there General Kenobi. This should be two sentences."
        )[0][0]
        hello_node = None
        for child in kenobi_node.children:
            if child.text == "Hello":
                hello_node = child

        self.assertEqual(hello_node.text, "Hello")
        self.assertEqual(hello_node.get_compound(), "Hello")
        self.assertTrue(
            "there" in [child.text for child in hello_node.children]
        )

        self.assertNotEqual(kenobi_node, None)
        self.assertEqual(kenobi_node.get_compound(), "General Kenobi")

    def test_get_phrase(self):
        parsed = parse_query(
            "Hello there General Kenobi. This should be two sentences."
        )[1][0]
        main_child = None
        for child in parsed.children:
            if child.text == "sentences":
                main_child = child
        self.assertNotEqual(main_child, None)
        self.assertEqual(main_child.get_phrase(), "two sentences")
        self.assertEqual(main_child.get_compound(), "sentences")


if __name__ == "__main__":
    unittest.main()
