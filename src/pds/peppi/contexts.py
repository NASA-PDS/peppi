"""Module handling target related objects."""
import logging
from dataclasses import dataclass

from .context_base import ContextObject
from .context_base import ContextObjects
from .products import Products
from .query_builder import PDSRegistryClient


logger = logging.getLogger(__name__)

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
        self.__instruments__ = Instruments()

        if client is None:
            client = PDSRegistryClient()
        context_products = Products(client).contexts()

        for api_item in context_products:
            if Targets.NAME_PROPERTY in api_item.properties:
                self.__targets__.add(api_item)
            elif InstrumentHosts.NAME_PROPERTY in api_item.properties:
                self.__instrument_hosts__.add(api_item)
            elif Instruments.NAME_PROPERTY in api_item.properties:
                self.__instruments__.add(api_item)


    @property
    def TARGETS(self):  # noqa
        """Targets or Planetary Objects context products: planets, satellites, asteroids or comets.

        Dynamically populated from the RESTFul API.
        """
        return self.__targets__

    @property
    def INSTRUMENT_HOSTS(self):  # noqa
        """Instrument hosts context products: spacecrafts, orbiter or rovers.

        Dynamically populated from the RESTFul API.
        """
        return self.__instrument_hosts__

    @property
    def INSTRUMENTS(self):  # noqa
        """Instruments context products: instruments on board the instrument hosts.

        Dynamically populated from the RESTFul API.
        """
        return self.__instruments__


@dataclass
class Target(ContextObject):
    """Simple object describing a target."""

    pass


class InstrumentHost(ContextObject):
    """Simple objet describing an instrument host, spacecraft, orbiter, rover..."""

    pass

class Instrument(ContextObject):
    """Simple objet describing an instrument."""

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

    NAME_PROPERTY = "pds:Target.pds:name"
    TYPE_PROPERTY = "pds:Target.pds:type"
    DESCRIPTION_PROPERTY = "pds:Target.pds:description"

    @staticmethod
    def api_to_obj(d: dict) -> Target:
        """Transform the RESTFul API product object into the Target object."""
        code = d.properties[Targets.NAME_PROPERTY][0].upper().replace(" ", "_")
        return Target(
            lid=d.properties["lid"][0],
            code=code,
            name=d.properties[Targets.NAME_PROPERTY][0],
            type=d.properties[Targets.TYPE_PROPERTY][0],
            description=d.properties[Targets.DESCRIPTION_PROPERTY][0],
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

    NAME_PROPERTY = "pds:Instrument_Host.pds:name"
    TYPE_PROPERTY = "pds:Instrument_Host.pds:type"
    DESCRIPTION_PROPERTY = "pds:Instrument_Host.pds:description"

    @staticmethod
    def api_to_obj(instrument_host: dict) -> InstrumentHost:
        """Transform the RESTFul API product object into the Target object."""
        code = instrument_host.properties[InstrumentHosts.NAME_PROPERTY][0].upper().replace(" ", "_")
        # TODO use the following value as an alias when it exists
        # code = instrument_host.properties["pds:Instrument_Host.pds:naif_host_id"][0].upper().replace(" ", "_")
        return InstrumentHost(
            lid=instrument_host.properties["lid"][0],
            code=code,
            name=instrument_host.properties[InstrumentHosts.NAME_PROPERTY][0],
            type=instrument_host.properties[InstrumentHosts.TYPE_PROPERTY][0],
            description=instrument_host.properties[InstrumentHosts.DESCRIPTION_PROPERTY][0],
        )


class Instruments(ContextObjects):
    """Searchable enumeration of the instruments described in the Planetary Data System.

    When the code of the instrument is know it can be accessed with the code:

        context = pep.Context()
        context.INSTRUMENTS.MSI

    When the code is not known yet, search with line:

        msi = context.INSTRUMENTS.search("msi")

    Or supported with a typo:

        msi = context.INSTRUMENTS.search("msl")

    """

    NAME_PROPERTY = "pds:Instrument.pds:name"
    TYPE_PROPERTY = "ctli:Type_List.ctli:type"
    DESCRIPTION_PROPERTY = "pds:Instrument.pds:description"

    @staticmethod
    def api_to_obj(instrument: dict) -> Instrument:
        """Transform the RESTFul API product object into the Target object."""
        lidvid = instrument.properties["lidvid"][0]
        code = lidvid.split(":")[5].replace(".", "_").upper()
        if Instruments.TYPE_PROPERTY in instrument.properties:
            type = instrument.properties[Instruments.TYPE_PROPERTY][0]
        else:
            logger.warning("type missing for instrument %s, set to None", code)
            type = None
        return Instrument(
            lid=instrument.properties["lid"][0],
            code=code,
            name=instrument.properties[Instruments.NAME_PROPERTY][0],
            type=type,
            description=instrument.properties[Instruments.DESCRIPTION_PROPERTY][0],
        )
