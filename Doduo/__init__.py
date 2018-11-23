"""
Doduo/Doduo

Doduo library: reads configs from Doduo/configs/ and models
from Doduo/dumps/ to serve a Flask API at port 5000.
"""

from gensim.models import KeyedVectors
import numpy as np
import spacy

from Doduo.config import ROOT_DIR, EMB_MODEL_FILE


# Model imports
nlp = spacy.load("en_core_web_md")
word_model = KeyedVectors.load_word2vec_format(
    ROOT_DIR + "dumps/" + EMB_MODEL_FILE, binary=False
)


def intersect(a, b):
    """
    Compute if intersection exists between two
    arbitrary sets.
    """
    for aa in a:
        if aa in b:
            return True
    return False


class InvalidUsage(Exception):
    """
    Catches invalid API calls.
    """

    pass


class ConfigException(Exception):
    """
    Catches invalid Doduo config formats.
    """

    pass
