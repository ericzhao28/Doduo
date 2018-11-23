"""
Doduo/Doduo.soft_match

Build models for handling soft word matching:
using a set of sample words, determine if a
query word belongs to the same unknown class.
The main difficulty is determining membership
with no negative samples.
"""

from scipy.spatial.distance import cosine
from scipy.stats import tstd
import numpy as np
import re

from Doduo import word_model
from Doduo import ConfigException
from Doduo.config import SLACK_DEFAULT


def embed(word):
    """
    Convert a word to a norm-1 Numberbatch word vector.
    If the word is not in vocabulary, aa ConfigException will be raised.

    Args:
        word (str): string word to embed.
    Returns:
        1-dimensional numpy array that is the word vector. Raises
        ValueError if the word is out of vocabulary.
    """
    word = re.compile("[^a-zA-Z0-9_]").sub("", str(word)).lower().strip()
    if word in word_model:
        norm = np.linalg.norm(word_model[word])
        return word_model[word] / norm
    else:
        raise ValueError("Invalid words...")


def build_soft_model(sample_words):
    """
    Build a soft model for determining membership in an unknown
    class from which sample_words is drawn. We compute a
    slack value based on the variance of the word embeddings
    of the sample words. We then return a boolean function
    that computes the minimum distance of a word's embedding
    and checks if it is smaller than the slack value.

    Args:
        sample_words (list): list of sample words.
    Returns:
        Unnamed function that takes in a word and returns a boolean
        of whether the word belongs to the same unnamed class as the
        sample_words.
    """

    # Attempt to embed sample words into sample_vecs.
    sample_vecs = []
    for word in sample_words:
        try:
            sample_vecs.append(embed(word))
        except ValueError:
            raise ConfigException(
                "Soft match sample uses word '{}' not in model".format(word)
            )
    if len(sample_vecs) is 0:
        raise ConfigException("No soft match samples provided.")
    if len(sample_vecs) > 15:
        raise NotImplementedError(
            "Currently do not support > 15 options " "for soft matching."
        )

    # Compute a slack value based on the standard deviation of the
    # sample's distance from their mean.
    distances = [
        cosine(vec, np.mean(sample_vecs, axis=0)) for vec in sample_vecs
    ]
    if np.mean(distances) == 0:
        slack = SLACK_DEFAULT
    else:
        slack = max(distances) + tstd(distances)

    # Add the mean to the samples.
    sample_vecs.append(np.mean(sample_vecs, axis=0))

    # Boolean function to determine word membership: does_belong.
    def does_belong(word):
        try:
            word_vec = embed(word)
        except ValueError:
            return False
        return min([cosine(word_vec, vec) for vec in sample_vecs]) <= slack

    # Return our function.
    return does_belong
