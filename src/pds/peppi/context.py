"""Module for Context product aggregation (targets, investigations, ...)."""
from cachetools import cached

from .products import Products
from .query_builder import PDSRegistryClient
from .targets import Targets


class Context:
    """Aggregation of all the context products  (targets, investigations, instruments...) known in the PDS."""

    def __init__(self, client: PDSRegistryClient):
        """Contructor."""
        client = PDSRegistryClient()
        self.__context_products__ = Products(client).contexts()

    @property
    @cached
    def TARGETS(self):  # noqa
        """Targets dynimcally populated from the RESTFul API."""
        targets = Targets()
        for api_target in self.__context_products__:
            if "pds:Target.pds:name" in api_target.properties:
                targets.add_target(api_target)
        return targets
