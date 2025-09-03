"""Module for Context product aggregation (targets, investigations, ...)."""
from dataclasses import dataclass

from pds.peppi.client import PDSRegistryClient
from rapidfuzz.distance import Levenshtein


@dataclass
class ContextObject:
    """Simple object describing a context object, target, instrument, instrument_host, etc...."""

    lid: str
    code: str
    name: str
    type: str
    description: str

    @property
    def uri(self):
        """Get the URI where the full object can be retrieved."""
        base_url = PDSRegistryClient.get_base_url()
        return base_url + "/products/" + self.lid

    def keywords(self) -> str:
        """Specialized as needed to return the keywords used for text search on this object.

        :return: the keywords to match for search query
        """
        return self.name.lower()


class ContextObjects:
    """Base object for searchable context products, e.g. Instruments, Targets...."""

    def __init__(self):
        """Constructor. Creates an empty aggegation of context objects."""
        self.__objects__: list[ContextObject] = []
        self.__keyword_map__ = {}

    @staticmethod
    def api_to_obj(d: dict) -> ContextObject:
        """Must be implemented in the specilized objects, Targets, InstrumentHosts, ...."""
        pass

    def add(self, api_object: dict):
        """For internal use, adds target from the API response's objects into the enumeration."""
        obj = self.api_to_obj(api_object)
        self.__objects__.append(obj)
        setattr(self, obj.code, obj)

    @staticmethod
    def _custom_similarity(s1: str, s2: str) -> float:
        """Similarity where s(a, a) > s(a', a) > s(a, 'a b'), where a' is a with a typo and b is an extra token.

        :param s1: input string the one the user is searching for
        :param s2: string or keywords found in the objects
        :return: similarity from 0.0 to 1.0, 1.0 is perfect match

        """
        s2_tokens = s2.split()
        s1_token_number = len(s1.split())
        # build the combination of tokens which could match the user request
        candidate_match = []
        for length in range(1, s1_token_number + 1):
            for start in range(0, len(s2_tokens) + 1 - length):
                candidate_match.append(" ".join(s2_tokens[start : start + length]))

        edit_scores = [
            (Levenshtein.distance(s1, candidate) / max(len(s1), len(candidate)), candidate)
            for candidate in candidate_match
        ]
        best_match = min(edit_scores, key=lambda x: x[0])
        best_levenshtein_score = 1.0 - best_match[0]  # 0-1 value, 1 is best match

        token_coverage = 1.0 - abs(len(s2_tokens) - len(best_match[1].split())) / len(
            s2_tokens
        )  # 0-1 value, 0 is all the tokens were compared, 1 none

        return (2 * best_levenshtein_score + token_coverage) / 3

    def search(self, term: str, limit=10, with_scores=False):
        """Search entries in the enumeration. Tolerates typos.

        :param term: name to search for.
        :param limit: number of matching products returned
        :return: a list of mathing context products sorted from the best match to the not-as-best matches.
        """
        scored_objs = []
        for obj in self.__objects__:
            search_score = self._custom_similarity(term.lower(), obj.keywords())
            scored_objs.append((obj, search_score))

        sorted_matching_objs = sorted(scored_objs, key=lambda x: x[1], reverse=True)[0:limit]
        if with_scores:
            return sorted_matching_objs
        else:
            return [o[0] for o in sorted_matching_objs]
