"""Module handling target related objects."""
import difflib
from dataclasses import dataclass


@dataclass
class Target:
    """Simple object describing a target."""

    lid: str
    code: str
    code: str
    name: str
    type: str
    description: str

    @property
    def tokens(self):
        """Not used.

        Was proposed to search against all text available in the object
        but it is not efficient as it created false match when the description
        contains something like "unlike jupiter", it matches with jupiter
        unless we had a semantically aware search, which we don't know.
        :return:
        """
        tokens = set()
        for value in vars(self).values():
            for token in str(value).lower().split(" "):
                tokens.add(token)
        return tokens


class Targets:
    """Searchable enumeration of the planetary bodies, called targets, described in the Planetary Data System.

    When the code of the target is know it can be accessed with the code:

        context = pep.Context()
        context.TARGETS.JUPITER

    When the code is not known yet, search with line:

        jupiter = context.TARGETS.search("jupiter")

    Or supported with a typo:

        jupiter = context.TARGETS.search("jupyter")

    """

    def __init__(self):
        """Constructor. Creates an empty aggegation of targets."""
        self.__targets__: list[Target] = []
        self.__keywords_target_map__ = {}

    @staticmethod
    def target_dict_to_obj(target: dict):
        """Transform the RESTFul API product object into the Target object."""
        code = target.properties["pds:Target.pds:name"][0].upper().replace(" ", "_")
        return Target(
            lid=target.properties["lid"][0],
            code=code,
            name=target.properties["pds:Target.pds:name"][0],
            type=target.properties["pds:Target.pds:type"][0],
            description=target.properties["pds:Target.pds:description"][0],
        )

    def add_target(self, api_target: dict):
        """For internal use, adds target from the API response's objects into the enumeration."""
        target_obj = self.target_dict_to_obj(api_target)
        self.__targets__.append(target_obj)
        setattr(self, target_obj.code, target_obj)

    def search(self, term: str, threshold=0.8):
        """Search entries in the enumeration. Tolerates typos.

        :param term: name to search for.
        :param threshold: from 0 to 1, lower gives more results, higher only the exact match.
        :return: a list of mathing targets sorted from the best match to the not-as-best matches.
        """
        matching_targets = []
        for target in self.__targets__:
            search_score = difflib.SequenceMatcher(None, term.lower(), target.name.lower()).ratio()
            if search_score >= threshold:
                matching_targets.append((target, search_score))
        return sorted(matching_targets, key=lambda x: x[1], reverse=True)
