import unittest

from pds.peppi.context_base import ContextObjects


class ContextObjectsTestCase(unittest.TestCase):
    def test_similarity_jupyter(self):
        # from perfect match to not as good
        jupiter_similarities = ["jupiter", "jupyter", "	jupiter laboratory analog", "saturn"]

        jupyter_scores = [ContextObjects._custom_similarity(s, jupiter_similarities[0]) for s in jupiter_similarities]
        assert jupyter_scores[0] == 1
        assert jupyter_scores[1] > jupyter_scores[2]
        assert jupyter_scores[2] > jupyter_scores[3]

    def test_similarity_curiosity(self):
        # from perfect match to not as good
        curiosity_similarities = ["the mars science laboratory curiosity rover", "curiosity", "cruiosity", "juno"]

        curiosity_scores = [
            ContextObjects._custom_similarity(s, curiosity_similarities[0]) for s in curiosity_similarities
        ]
        assert curiosity_scores[0] == 1
        assert curiosity_scores[1] > curiosity_scores[2]
        assert curiosity_scores[2] > curiosity_scores[3]


if __name__ == "__main__":
    unittest.main()
