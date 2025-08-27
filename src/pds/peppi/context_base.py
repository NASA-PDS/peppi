"""Module for Context product aggregation (targets, investigations, ...)."""
import difflib
from dataclasses import dataclass


@dataclass
class ContextObject:
    """Simple object describing a context object, target, instrument, instrument_host, etc...."""

    lid: str
    code: str
    name: str
    type: str
    description: str

    def keywords(self) -> str:
        """Specialized as needed to return the keywords used for text search on this object.

        :return: the keywords to match for search query
        """
        return self.name


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

    def search(self, term: str, threshold=0.8):
        """Search entries in the enumeration. Tolerates typos.

        :param term: name to search for.
        :param threshold: from 0 to 1, lower gives more results, higher only the exact match.
        :return: a list of mathing targets sorted from the best match to the not-as-best matches.
        """
        matching_objs = []
        for obj in self.__objects__:
            search_score = difflib.SequenceMatcher(None, term.lower(), obj.keywords()).ratio()
            if search_score >= threshold:
                matching_objs.append((obj, search_score))
        return sorted(matching_objs, key=lambda x: x[1], reverse=True)
