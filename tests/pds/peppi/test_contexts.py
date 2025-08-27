import unittest

import pds.peppi as pep


class TargetsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        context = pep.Context()
        self.targets = context.TARGETS

    def test_targets(self):
        assert hasattr(self.targets, "SETEBOS") == True
        assert self.targets.SETEBOS.name == "Setebos"
        assert self.targets.SETEBOS.lid == "urn:nasa:pds:context:target:satellite.uranus.setebos"

    def test_search(self):
        result = self.targets.search("jupiter")
        assert result[0][0].lid == "urn:nasa:pds:context:target:planet.jupiter"

        # with typo
        result = self.targets.search("jupyter")
        assert result[0][0].lid == "urn:nasa:pds:context:target:planet.jupiter"


class InstrumentHostsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        context = pep.Context()
        self.instrument_hosts = context.INSTRUMENT_HOSTS

    def test_instrument_hosts(self):
        assert hasattr(self.instrument_hosts, "THE_MARS_SCIENCE_LABORATORY_CURIOSITY_ROVER") == True
        assert (
            self.instrument_hosts.THE_MARS_SCIENCE_LABORATORY_CURIOSITY_ROVER.name
            == "The Mars Science Laboratory Curiosity Rover"
        )
        assert (
            self.targets.THE_MARS_SCIENCE_LABORATORY_CURIOSITY_ROVER.lid
            == "urn:nasa:pds:context:instrument_host:spacecraft.msl"
        )

    @unittest.skip("not implemented yet")
    def test_instrument_hosts_alias(self):
        assert hasattr(self.instrument_hosts, "MSL") == True
        assert self.instrument_hosts.MSL.name == "The Mars Science Laboratory Curiosity Rover"
        assert self.targets.MSL.lid == "urn:nasa:pds:context:instrument_host:spacecraft.msl"
        assert self.instrument_hosts.MSL.alias_of == self.instrument_hosts.THE_MARS_SCIENCE_LABORATORY_CURIOSITY_ROVER

    def test_search(self):
        result = self.targets.search("curiosity")
        assert result[0][0].lid == "urn:nasa:pds:context:instrument_host:spacecraft.msl"

        # with typo
        result = self.targets.search("cruiosity")
        assert result[0][0].lid == "urn:nasa:pds:context:instrument_host:spacecraft.msl"

        # TODO
        # result = self.targets.search("msl")
        # assert result[0][0].lid == "urn:nasa:pds:context:instrument_host:spacecraft.msl"


if __name__ == "__main__":
    unittest.main()
