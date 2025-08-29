"""PDS Registry Client related classes."""
import logging

from pds.api_client import ApiClient
from pds.api_client import Configuration


logger = logging.getLogger(__name__)

_DEFAULT_API_BASE_URL = "https://pds.nasa.gov/api/search/1"
"""Default URL used when querying PDS API"""


class PDSRegistryClient:
    """Used to connect and interface with the PDS Registry.

    Attributes
    ----------
    api_client : pds.api_client.ApiClient
        Object used to interact with the PDS Registry API

    """

    _instances = []

    def __init__(self, base_url=_DEFAULT_API_BASE_URL):
        """Creates a new instance of PDSRegistryClient.

        Parameters
        ----------
        base_url: str, optional
            The base endpoint URL of the PDS Registry API. The default value is
             the official production server, can be specified otherwise.

        """
        self._base_url = base_url
        PDSRegistryClient._instances.append(self)
        configuration = Configuration()
        configuration.host = base_url
        self.api_client = ApiClient(configuration)

    @classmethod
    def get_base_url(cls) -> str:
        """Find the PDS API URL used in this context. If multiple ones were used only the first found is returned."""
        if len(cls._instances) == 1:
            return cls._instances[0]._base_url
        elif len(cls._instances) > 1:
            logger.warning("Multiple instances found, using first one.")
            return cls._instances[0]._base_url
        else:
            logger.error("No instances found. Cannot find the base URL")
            return None
