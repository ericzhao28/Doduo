"""
tests/test_beer.py

Test Doduo end to end on the beer sample.
"""

import unittest

from Doduo.matcher import Matcher


M = Matcher("beer.yml")


class TestBeer(unittest.TestCase):
    def test_what_color_are_your_chocolate_ales(self):
        self.assertEqual(
            list(M.match("What color are your chocolate ales?", None)),
            [
                {
                    "__alternatives__": {},
                    "__sentence__": "What color are your chocolate ales?",
                    "attribute_question": {
                        "attribute": ["color"],
                        "product": ["your chocolate ales"],
                    },
                }
            ],
        )

        self.assertEqual(
            list(
                M.match(
                    "What color are your chocolate ales?",
                    ["attribute_question"],
                )
            ),
            [
                {
                    "__alternatives__": {},
                    "__sentence__": "What color are your chocolate ales?",
                    "attribute_question": {
                        "attribute": ["color"],
                        "product": ["your chocolate ales"],
                    },
                }
            ],
        )

        self.assertEqual(
            list(
                M.match(
                    "What color are your chocolate ales?",
                    ["preference_statement"],
                )
            ),
            [
                {
                    "__alternatives__": {},
                    "__sentence__": "What color are your chocolate ales?",
                }
            ],
        )

        self.assertEqual(
            list(
                M.match(
                    "What color are your chocolate ales?",
                    ["attribute_question", "preference_statement"],
                )
            ),
            [
                {
                    "__alternatives__": {},
                    "__sentence__": "What color are your chocolate ales?",
                    "attribute_question": {
                        "attribute": ["color"],
                        "product": ["your chocolate ales"],
                    },
                }
            ],
        )

    def test_what_flavor_stout(self):
        self.assertEqual(
            list(M.match("What flavor is the stout?", None)),
            [
                {
                    "__alternatives__": {},
                    "__sentence__": "What flavor is the stout?",
                    "attribute_question": {
                        "attribute": ["flavor"],
                        "product": ["the stout"],
                    },
                }
            ],
        )

        self.assertEqual(
            list(M.match("What flavor is the stout?", ["attribute_question"])),
            [
                {
                    "__alternatives__": {},
                    "__sentence__": "What flavor is the stout?",
                    "attribute_question": {
                        "attribute": ["flavor"],
                        "product": ["the stout"],
                    },
                }
            ],
        )

        self.assertEqual(
            list(
                M.match("What flavor is the stout?", ["preference_statement"])
            ),
            [
                {
                    "__alternatives__": {},
                    "__sentence__": "What flavor is the stout?",
                }
            ],
        )

        self.assertEqual(
            list(
                M.match(
                    "What flavor is the stout?",
                    ["attribute_question", "preference_statement"],
                )
            ),
            [
                {
                    "__alternatives__": {},
                    "__sentence__": "What flavor is the stout?",
                    "attribute_question": {
                        "attribute": ["flavor"],
                        "product": ["the stout"],
                    },
                }
            ],
        )

    def test_i_dont_drink_ale(self):
        self.assertEqual(
            list(M.match("I don't drink chocolate ale.", None)),
            [
                {
                    "__alternatives__": {
                        "preference_statement": [
                            {"opinion": ["drink"], "product": ["chocolate ale"]}
                        ]
                    },
                    "__sentence__": "I don't drink chocolate ale.",
                    "preference_statement": {
                        "opinion": ["drink"],
                        "opinion negation": ["n't"],
                        "product": ["chocolate ale"],
                    },
                }
            ],
        )

        self.assertEqual(
            list(
                M.match(
                    "I don't drink chocolate ale.", ["preference_statement"]
                )
            ),
            [
                {
                    "__alternatives__": {
                        "preference_statement": [
                            {"opinion": ["drink"], "product": ["chocolate ale"]}
                        ]
                    },
                    "__sentence__": "I don't drink chocolate ale.",
                    "preference_statement": {
                        "opinion": ["drink"],
                        "opinion negation": ["n't"],
                        "product": ["chocolate ale"],
                    },
                }
            ],
        )

        self.assertEqual(
            list(
                M.match("I don't drink chocolate ale.", ["attribute_question"])
            ),
            [
                {
                    "__alternatives__": {},
                    "__sentence__": "I don't drink chocolate ale.",
                }
            ],
        )

        self.assertEqual(
            list(
                M.match(
                    "I don't drink chocolate ale.",
                    ["attribute_question", "preference_statement"],
                )
            ),
            [
                {
                    "__alternatives__": {
                        "preference_statement": [
                            {"opinion": ["drink"], "product": ["chocolate ale"]}
                        ]
                    },
                    "__sentence__": "I don't drink chocolate ale.",
                    "preference_statement": {
                        "opinion": ["drink"],
                        "opinion negation": ["n't"],
                        "product": ["chocolate ale"],
                    },
                }
            ],
        )

    def test_i_hate_ale(self):
        self.assertEqual(
            list(M.match("I hate ale.", None)),
            [
                {
                    "__alternatives__": {},
                    "__sentence__": "I hate ale.",
                    "preference_statement": {
                        "opinion": ["hate"],
                        "product": ["ale"],
                    },
                }
            ],
        )

        self.assertEqual(
            list(M.match("I hate ale.", ["preference_statement"])),
            [
                {
                    "__alternatives__": {},
                    "__sentence__": "I hate ale.",
                    "preference_statement": {
                        "opinion": ["hate"],
                        "product": ["ale"],
                    },
                }
            ],
        )

        self.assertEqual(
            list(M.match("I hate ale.", ["attribute_question"])),
            [{"__alternatives__": {}, "__sentence__": "I hate ale."}],
        )

        self.assertEqual(
            list(
                M.match(
                    "I hate ale.",
                    ["attribute_question", "preference_statement"],
                )
            ),
            [
                {
                    "__alternatives__": {},
                    "__sentence__": "I hate ale.",
                    "preference_statement": {
                        "opinion": ["hate"],
                        "product": ["ale"],
                    },
                }
            ],
        )

    def test_do_you_have_any_porters(self):
        self.assertEqual(
            list(M.match("Do you have any really old porters?", None)),
            [
                {
                    "__alternatives__": {},
                    "__sentence__": "Do you have any really old porters?",
                    "action_request": {
                        "action": ["have"],
                        "product": ["any really old porters"],
                    },
                }
            ],
        )

        self.assertEqual(
            list(
                M.match(
                    "Do you have any really old porters?", ["action_request"]
                )
            ),
            [
                {
                    "__alternatives__": {},
                    "__sentence__": "Do you have any really old porters?",
                    "action_request": {
                        "action": ["have"],
                        "product": ["any really old porters"],
                    },
                }
            ],
        )

        self.assertEqual(
            list(
                M.match(
                    "Do you have any really old porters?",
                    ["preference_statement"],
                )
            ),
            [
                {
                    "__alternatives__": {},
                    "__sentence__": "Do you have any really old porters?",
                }
            ],
        )

        self.assertEqual(
            list(
                M.match(
                    "Do you have any really old porters?",
                    ["action_request", "preference_statement"],
                )
            ),
            [
                {
                    "__alternatives__": {},
                    "__sentence__": "Do you have any really old porters?",
                    "action_request": {
                        "action": ["have"],
                        "product": ["any really old porters"],
                    },
                }
            ],
        )

    def test_do_you_recommend_ales(self):
        self.assertEqual(
            list(M.match("Do you recommend any ales?", None)),
            [
                {
                    "__alternatives__": {},
                    "__sentence__": "Do you recommend any ales?",
                    "action_request": {
                        "action": ["recommend"],
                        "product": ["any ales"],
                    },
                }
            ],
        )

        self.assertEqual(
            list(M.match("Do you recommend any ales?", ["action_request"])),
            [
                {
                    "__alternatives__": {},
                    "__sentence__": "Do you recommend any ales?",
                    "action_request": {
                        "action": ["recommend"],
                        "product": ["any ales"],
                    },
                }
            ],
        )

        self.assertEqual(
            list(
                M.match("Do you recommend any ales?", ["preference_statement"])
            ),
            [
                {
                    "__alternatives__": {},
                    "__sentence__": "Do you recommend any ales?",
                }
            ],
        )

        self.assertEqual(
            list(
                M.match(
                    "Do you recommend any ales?",
                    ["action_request", "preference_statement"],
                )
            ),
            [
                {
                    "__alternatives__": {},
                    "__sentence__": "Do you recommend any ales?",
                    "action_request": {
                        "action": ["recommend"],
                        "product": ["any ales"],
                    },
                }
            ],
        )
