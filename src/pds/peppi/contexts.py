"""Module handling target related objects."""
from dataclasses import dataclass

from .context_base import ContextObject
from .context_base import ContextObjects
from .products import Products
from .query_builder import PDSRegistryClient


class Context:
    """Aggregation of all the context products  (targets, investigations, instruments...) known in the PDS."""

    # We make this class a singleton.
    def __new__(cls):
        """Singleton management."""
        if not hasattr(cls, "instance"):
            cls.instance = super(Context, cls).__new__(cls)
        return cls.instance

    def __init__(self, client: PDSRegistryClient = None):
        """Constructor."""
        self.__targets__ = Targets()
        self.__instrument_hosts__ = InstrumentHosts()

        if client is None:
            client = PDSRegistryClient()
        context_products = Products(client).contexts()

        for api_item in context_products:
            if "pds:Target.pds:name" in api_item.properties:
                self.__targets__.add(api_item)
            elif "pds:Instrument_Host.pds:name" in api_item.properties:
                self.__instrument_hosts__.add(api_item)

    @property
    def TARGETS(self):  # noqa
        """Targets dynamically populated from the RESTFul API."""
        return self.__targets__

    @property
    def INSTRUMENT_HOSTS(self):  # noqa
        """Instrument hosts dynamically populated from the RESTFul API."""
        return self.__instrument_hosts__


@dataclass
class Target(ContextObject):
    """Simple object describing a target."""

    pass


class InstrumentHost(ContextObject):
    """Simple objet descirbing an instrument host, spacecraft, orbiter, rover..."""

    pass


class Targets(ContextObjects):
    """Searchable enumeration of the planetary bodies, called targets, described in the Planetary Data System.

    When the code of the target is know it can be accessed with the code:

        context = pep.Context()
        context.TARGETS.JUPITER

    When the code is not known yet, search with line:

        jupiter = context.TARGETS.search("jupiter")

    Or supported with a typo:

        jupiter = context.TARGETS.search("jupyter")

    """

    @staticmethod
    def api_to_obj(d: dict) -> Target:
        """Transform the RESTFul API product object into the Target object."""
        code = d.properties["pds:Target.pds:name"][0].upper().replace(" ", "_")
        return Target(
            lid=d.properties["lid"][0],
            code=code,
            name=d.properties["pds:Target.pds:name"][0],
            type=d.properties["pds:Target.pds:type"][0],
            description=d.properties["pds:Target.pds:description"][0],
        )


class InstrumentHosts(ContextObjects):
    """Searchable enumeration of the spacecrafts or rovers, called instrument hosts, described in the Planetary Data System.

    When the code of the instrument host is know it can be accessed with the code:

        context = pep.Context()
        context.INSTRUMENT_HOSTS.MSL

    When the code is not known yet, search with line:

        jupiter = context.TARGETS.search("curiosity")

    Or supported with a typo:

        jupiter = context.TARGETS.search("cruiosity")

    """

    @staticmethod
    def api_to_obj(instrument_host: dict) -> InstrumentHost:
        """Transform the RESTFul API product object into the Target object."""
        code = instrument_host.properties["pds:Instrument_Host.pds:name"][0].upper().replace(" ", "_")
        # TODO use this value as an alias when it exists
        # code = instrument_host.properties["pds:Instrument_Host.pds:naif_host_id"][0].upper().replace(" ", "_")
        return InstrumentHost(
            lid=instrument_host.properties["lid"][0],
            code=code,
            name=instrument_host.properties["pds:Instrument_Host.pds:name"][0],
            type=instrument_host.properties["pds:Instrument_Host.pds:type"][0],
            description=instrument_host.properties["pds:Instrument_Host.pds:description"][0],
        )
