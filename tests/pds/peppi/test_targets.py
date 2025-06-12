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


if __name__ == "__main__":
    unittest.main()
