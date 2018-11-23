"""
Doduo/Doduo.template

A tree structure for easily comparing against
Query trees.
"""

import copy

from Doduo import intersect
from Doduo.soft_match import build_soft_model


class Template:
    def __init__(
        self,
        children=None,
        exact_match=None,
        soft_match=None,
        pos_match=None,
        ner_match=None,
        rels=None,
        optional=False,
        case_sensitive=False,
        slot_name=None,
        slot_is_not_compound=False,
        slot_is_full_phrase=False,
    ):
        """
        Args:
            children (list):              child Template objects.
            exact_match (list):           strings to exactly match against.
            soft_match (list):            strings to train the soft matcher.
            pos_match (list):             valid part of sentence tags.
            ner_match (list):             valid named entity tags.
            rels_match (list):            valid relationships with parents.
            optional (bool):              is this child
            case_sensitive (bool):        enforce be case sensitivity?
            slot_name (str):              slot name of vertex.
            slot_is_not_compound (bool):  should slot value be compound
            slot_is_full_phrase (bool):   should slot value be full phrase
        """

        self.children = children or []
        self.slot_name = slot_name
        self.slot_is_full_phrase = slot_is_full_phrase
        self.slot_is_not_compound = slot_is_not_compound
        self.optional = optional
        self.case_sensitive = case_sensitive
        self.soft_match = soft_match
        self.rels = rels or []
        self.exact_match = exact_match or []
        self.pos_match = pos_match or []
        self.ner_match = ner_match or []

        # Enforce lowercase on POS/NER/exact_match (if case insensitive)
        self.pos_match = [x.lower() for x in self.pos_match]
        self.ner_match = [x.lower() for x in self.ner_match]
        if not self.case_sensitive:
            self.exact_match = [x.lower() for x in self.exact_match]

        # Build soft match model.
        if self.soft_match is not None:
            self.soft_match = build_soft_model(self.soft_match)

    def match(self, candidate):
        """
        Match and obtain slot values for comparison of self
        and a provided candidate tree.
        Args:
            candidate (Query): query tree object.
        Returns:
            List of dictionaries, each of which is a feasible
            assignment of slot values.
        """

        # If relationship is enforced and we do not have equivalence,
        # this match is a failure.
        if self.rels and candidate.rel not in self.rels:
            return False

        # If match parameters are specified, enforce that at least one
        # of them aligns.
        if (
            self.exact_match
            or self.soft_match
            or self.ner_match
            or self.pos_match
        ):
            matched = False
            if not self.case_sensitive:
                matched = matched or candidate.text.lower() in self.exact_match
            else:
                matched = matched or candidate.text in self.exact_match
            matched = matched or intersect(candidate.ner, self.ner_match)
            matched = matched or (candidate.pos in self.pos_match)
            if self.soft_match is not None:
                matched = matched or self.soft_match(candidate.text)
            if not matched:
                return False

        # The match for this vertex is succesful. We now begin
        # the slotting task and validating that children are matches.

        # Set our current hypothesis using this vertice's slot value.
        # The hypotheses list is composed of a list of dictionaries.
        # The unmatched key is a list of candidate.children that have
        # not been aligned for the hypothesis and are available for
        # matching. The slots key is a dictionary containing the
        # filled in slot values for the hypothesis.
        hypotheses = [{"unmatched": candidate.children[:], "slots": {}}]
        if self.slot_name is not None:
            if self.slot_is_full_phrase:
                slot_value = candidate.get_phrase()
            elif self.slot_is_not_compound:
                slot_value = candidate.text
            else:
                slot_value = candidate.get_compound()
            hypotheses[0]["slots"] = {self.slot_name: [slot_value]}

        # For each hypothesis, we want to make sure that
        # there is a proper alignment with each one of the enforced
        # children of this tree.
        for template_child in self.children:
            new_hypotheses = []
            for hyp in hypotheses:
                for cand_child in hyp["unmatched"]:
                    # Check if this candidate-template pair is valid.
                    result = template_child.match(cand_child)
                    if result is False:
                        continue

                    # If so, we update our hypothesis.
                    unmatched = [x for x in hyp["unmatched"] if x != cand_child]
                    assert len(unmatched) == len(hyp["unmatched"]) - 1

                    # For each hypothesis of the child's match:
                    # we create a combination of that hypothesis and our
                    # current hypothesis to add to our hypotheses list.
                    for child_slots in result:
                        slots = copy.deepcopy(hyp["slots"])
                        for key, slot_value in child_slots.items():
                            if key not in slots:
                                slots[key] = []
                            slots[key] += slot_value
                        new_hypotheses.append(
                            {"unmatched": unmatched, "slots": slots}
                        )

            # If this child is optional, we consider the case where
            # we don't actually match this child.
            if template_child.optional:
                new_hypotheses += hypotheses

            # If we no longer have any more valid hypotheses, we have failed.
            hypotheses = new_hypotheses
            if not hypotheses:
                return False

        # Return the feasible slot values.
        return [x["slots"] for x in hypotheses]
