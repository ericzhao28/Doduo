"""
Doduo/Doduo.query

Wraps natural language sentences into tree structures for
easier comparison against Template objects.
"""

from uuid import uuid4
from copy import copy

from Doduo import nlp


def parse_query(query):
    """
    Parse a natural language query into a list
    of Query trees.

    Args:
        query (str): natural language string.
    Returns:
        A list of Query objects.
    """

    def __build_subtree(token):
        """ Build the Query tree for a given token. """
        children = [__build_subtree(t) for t in token.lefts]
        children += [__build_subtree(t) for t in token.rights]
        return Query(token, children)

    # Use Spacy to parse the natural language string
    # and build subtrees for each sentence's root.
    doc = nlp(query)
    parsed_list = [(__build_subtree(s.root), s.text) for s in doc.sents]

    return parsed_list


class Query:
    """
    Query class.

    Wraps a query sentence into a tree with a structure paralleling
    the sentence's dependency parse tree.
    """

    def __init__(self, token, children=None):
        """
        Args:
            token (Spacy.token): the token corresponding to this vertex
                                 in the tree.
            children (list):     list of Query objects.
        """
        self.ner = [token.ent_type_.lower(), token.pos_.lower()]
        self.pos = token.pos_.lower()
        self.text = token.text.strip()
        self.token = token
        self.rel = token.dep_.lower()
        self.children = children or []

    def get_compound(self):
        """
        Get the string composing of this tree and all it's
        `compound` related children.
        """

        def __collapse(token):
            compound_str = token.text
            for t in token.lefts:
                if t.dep_ == "compound":
                    compound_str = __collapse(t) + " " + compound_str
            for t in token.rights:
                if t.dep_ == "compound":
                    compound_str = compound_str + " " + __collapse(t)
            return compound_str

        return __collapse(self.token)

    def get_phrase(self):
        """
        Get the string composing all the vertices downstream
        of this tree.
        """

        def __get_phrase(token):
            lefts = [__get_phrase(t) for t in token.lefts]
            rights = [__get_phrase(t) for t in token.rights]
            return " ".join(lefts + [token.text] + rights)

        return __get_phrase(self.token)
