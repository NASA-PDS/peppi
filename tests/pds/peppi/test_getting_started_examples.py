"""Tests for examples in the Getting Started documentation.

These tests verify that all code examples in docs/source/getting_started.rst
are functional and produce expected results.
"""
import unittest

import pds.peppi as pep
from pds.api_client import PdsProduct


class GettingStartedExamplesTestCase(unittest.TestCase):
    """Test cases for Getting Started guide examples."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.client = pep.PDSRegistryClient()

    def test_basic_import(self):
        """Test: Import Peppi."""
        # This is tested by the import at the top of the file
        self.assertIsNotNone(pep)

    def test_create_client(self):
        """Test: Connect to the PDS."""
        client = pep.PDSRegistryClient()
        self.assertIsNotNone(client)
        self.assertIsNotNone(client.api_client)

    def test_find_products_about_mars(self):
        """Test: Find products about Mars."""
        client = pep.PDSRegistryClient()

        # Search for observational products targeting Mars
        products = pep.Products(client).has_target("Mars").observationals()

        # Verify we can iterate and get results
        found_products = 0
        for product in products:
            self.assertIsInstance(product, PdsProduct)
            self.assertIsNotNone(product.id)
            found_products += 1
            if found_products >= 5:
                break

        self.assertGreater(found_products, 0, "Should find at least one Mars product")

    def test_look_at_results(self):
        """Test: Look at the first 5 results."""
        client = pep.PDSRegistryClient()
        products = pep.Products(client).has_target("Mars").observationals()

        # Print information about the first 5 products
        for i, product in enumerate(products):
            self.assertIsNotNone(product.id)
            # Verify product has properties
            self.assertIsInstance(product.properties, dict)

            # Try to get title (may not always exist)
            title = product.properties.get('pds:Identification_Area.pds:title', ['N/A'])[0]
            self.assertIsNotNone(title)

            if i >= 4:  # Stop after 5 products (0-4)
                break

        self.assertTrue(True)  # If we got here, the example works

    def test_complete_first_example(self):
        """Test: Complete first example from Getting Started."""
        # Connect to PDS
        client = pep.PDSRegistryClient()

        # Search for Mars observational data
        products = pep.Products(client).has_target("Mars").observationals()

        # Print information about the first 5 products
        product_count = 0
        for i, product in enumerate(products):
            self.assertIsNotNone(product.id)
            title = product.properties.get('pds:Identification_Area.pds:title', ['N/A'])[0]
            self.assertIsNotNone(title)

            product_count += 1

            if i >= 4:  # Stop after 5 products
                break

        self.assertGreaterEqual(product_count, 1, "Should have found at least 1 product")


class ProductMetadataTestCase(unittest.TestCase):
    """Test understanding product metadata examples."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.client = pep.PDSRegistryClient()

    def test_product_attributes(self):
        """Test: Understanding what you got - product attributes."""
        products = pep.Products(self.client).has_target("Mars").observationals()

        for product in products:
            # Verify product.id exists
            self.assertIsNotNone(product.id)
            self.assertIsInstance(product.id, str)

            # Verify product.properties exists and is a dict
            self.assertIsNotNone(product.properties)
            self.assertIsInstance(product.properties, dict)

            # Verify product.type exists
            self.assertIsNotNone(product.type)

            break  # Just test first product


if __name__ == '__main__':
    unittest.main()
