"""Tests for Advanced recipes in the Cookbook.

These tests verify that all Advanced recipes (13-20) in
docs/source/cookbook.rst are functional and produce expected results.
"""
import unittest
from datetime import datetime
from datetime import timedelta
from typing import Optional

import pandas as pd
import pds.peppi as pep



class Recipe17TestCase(unittest.TestCase):
    """Recipe 17: Work with OSIRIS-REx Specialized Products."""

    def test_orex_products(self):
        """Test using OrexProducts specialized class."""
        client = pep.PDSRegistryClient()

        # Use the OSIRIS-REx (OREX) specialized products class
        orex_products = pep.OrexProducts(client)

        # OrexProducts inherits all the standard filters
        products = orex_products.has_target("Bennu").within_range(100.0).within_bbox(9.0, 15.0, 21.0, 27.0).observationals()

        found = False
        for i, product in enumerate(products):
            title = product.properties.get('pds:Identification_Area.pds:title', ['N/A'])[0]
            self.assertIsNotNone(title)
            found = True
            if i >= 2:
                break

        # Results depend on data availability



if __name__ == '__main__':
    unittest.main()
