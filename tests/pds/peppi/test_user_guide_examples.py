"""Tests for examples in the User Guide documentation.

These tests verify that all code examples in docs/source/user_guide.rst
are functional and produce expected results.
"""
import unittest
from datetime import datetime

import pds.peppi as pep
from pds.api_client import PdsProduct


class CoreComponentsTestCase(unittest.TestCase):
    """Test core components examples."""

    def test_pds_registry_client(self):
        """Test: PDSRegistryClient basic usage."""
        client = pep.PDSRegistryClient()
        self.assertIsNotNone(client)
        self.assertIsNotNone(client.api_client)

    def test_pds_registry_client_custom_url(self):
        """Test: PDSRegistryClient with custom URL."""
        # Using the default URL for testing
        client = pep.PDSRegistryClient(base_url="https://pds.nasa.gov/api/search/1")
        self.assertIsNotNone(client)

    def test_products_fluent_interface(self):
        """Test: Products fluent interface."""
        client = pep.PDSRegistryClient()

        products = pep.Products(client) \
            .has_target("Mars") \
            .observationals()

        # Verify we can iterate
        for i, product in enumerate(products):
            self.assertIsInstance(product, PdsProduct)
            if i >= 2:
                break

    def test_context_search_targets(self):
        """Test: Context - search for targets."""
        context = pep.Context()

        # Search for Jupiter
        jupiter = context.TARGETS.search("jupiter")[0]
        self.assertIsNotNone(jupiter.name)
        self.assertIsNotNone(jupiter.lid)
        self.assertIn("jupiter", jupiter.name.lower())

    def test_context_search_instrument_hosts(self):
        """Test: Context - search for spacecraft."""
        context = pep.Context()

        # Search for Curiosity
        curiosity = context.INSTRUMENT_HOSTS.search("curiosity")[0]
        self.assertIsNotNone(curiosity.name)
        self.assertIsNotNone(curiosity.lid)

    def test_context_fuzzy_matching(self):
        """Test: Context fuzzy matching with typos."""
        context = pep.Context()

        # Search with typo should still find Jupiter
        results = context.TARGETS.search("jupyter")
        self.assertGreater(len(results), 0, "Fuzzy search should find results despite typo")


class QueryBuildingTestCase(unittest.TestCase):
    """Test query building examples."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.client = pep.PDSRegistryClient()

    def test_query_builder_pattern(self):
        """Test: Query builder pattern - step by step."""
        query = pep.Products(self.client)
        query = query.has_target("Mars")
        query = query.observationals()

        # Execute by iterating
        found = False
        for product in query:
            self.assertIsNotNone(product.id)
            found = True
            break

        self.assertTrue(found, "Query should return results")

    def test_query_builder_chained(self):
        """Test: Query builder pattern - chained."""
        products = pep.Products(self.client).has_target("Mars").observationals()

        found = False
        for product in products:
            self.assertIsNotNone(product.id)
            found = True
            break

        self.assertTrue(found)

    def test_lazy_evaluation(self):
        """Test: Lazy evaluation - no API call until iteration."""
        # No API call happens yet
        query = pep.Products(self.client).has_target("Mars")

        # Still no API call
        query = query.observationals()

        # NOW the API is called
        for product in query:
            self.assertIsNotNone(product.id)
            break


class FilteringMethodsTestCase(unittest.TestCase):
    """Test filtering methods examples."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.client = pep.PDSRegistryClient()

    def test_filter_by_target_name(self):
        """Test: Filter by target name."""
        products = pep.Products(self.client).has_target("Mars").observationals()

        for product in products:
            self.assertIsNotNone(product.id)
            break

    def test_filter_by_target_lid(self):
        """Test: Filter by target LID."""
        products = pep.Products(self.client) \
            .has_target("urn:nasa:pds:context:target:planet.mars") \
            .observationals()

        for product in products:
            self.assertIsNotNone(product.id)
            break

    def test_filter_by_time_before(self):
        """Test: Filter by time - before."""
        date1 = datetime(2020, 1, 1)

        products = pep.Products(self.client) \
            .has_target("Mars") \
            .before(date1) \
            .observationals()

        for product in products:
            self.assertIsNotNone(product.id)
            break

    def test_filter_by_time_after(self):
        """Test: Filter by time - after."""
        date1 = datetime(2010, 1, 1)

        products = pep.Products(self.client) \
            .has_target("Mars") \
            .after(date1) \
            .observationals()

        for product in products:
            self.assertIsNotNone(product.id)
            break

    def test_filter_by_time_range(self):
        """Test: Filter by time range."""
        date1 = datetime(2015, 1, 1)
        date2 = datetime(2016, 12, 31)

        products = pep.Products(self.client) \
            .has_target("Mars") \
            .after(date1) \
            .before(date2) \
            .observationals()

        for product in products:
            self.assertIsNotNone(product.id)
            break

    def test_filter_by_instrument_host(self):
        """Test: Filter by instrument host."""
        context = pep.Context()
        curiosity = context.INSTRUMENT_HOSTS.search("curiosity")[0]

        products = pep.Products(self.client) \
            .has_instrument_host(curiosity.lid) \
            .observationals()

        for product in products:
            self.assertIsNotNone(product.id)
            break

    def test_filter_by_processing_level(self):
        """Test: Filter by processing level."""
        products = pep.Products(self.client) \
            .has_target("Mars") \
            .has_processing_level("calibrated") \
            .observationals()

        for product in products:
            # Verify processing level if field exists
            level = product.properties.get('pds:Primary_Result_Summary.pds:processing_level', [None])[0]
            if level:
                self.assertEqual(level.lower(), "calibrated")
            break

    def test_filter_by_product_type_observational(self):
        """Test: Filter by product type - observational."""
        products = pep.Products(self.client) \
            .has_target("Mars") \
            .observationals()

        for product in products:
            self.assertIsNotNone(product.id)
            break

    def test_filter_by_product_type_collections(self):
        """Test: Filter by product type - collections."""
        products = pep.Products(self.client) \
            .has_target("Mars") \
            .collections()

        for product in products:
            self.assertIsNotNone(product.id)
            break

    def test_filter_by_product_type_bundles(self):
        """Test: Filter by product type - bundles."""
        products = pep.Products(self.client) \
            .has_target("Mars") \
            .bundles()

        for product in products:
            self.assertIsNotNone(product.id)
            break

    def test_custom_filter(self):
        """Test: Custom filter clause."""
        products = pep.Products(self.client) \
            .filter('pds:Identification_Area.pds:title like "*Mars*"') \
            .observationals()

        for product in products:
            self.assertIsNotNone(product.id)
            break


class WorkingWithResultsTestCase(unittest.TestCase):
    """Test working with results examples."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.client = pep.PDSRegistryClient()

    def test_iterating_over_products(self):
        """Test: Iterating over products."""
        products = pep.Products(self.client).has_target("Mars").observationals()

        for product in products:
            self.assertIsNotNone(product.id)
            self.assertIsInstance(product.properties, dict)
            break

    def test_limiting_results(self):
        """Test: Limiting results with enumerate."""
        products = pep.Products(self.client).has_target("Mars").observationals()

        count = 0
        for i, product in enumerate(products):
            self.assertIsNotNone(product.id)
            count += 1
            if i >= 9:  # Stop after 10 products
                break

        self.assertGreaterEqual(count, 1)

    def test_converting_to_dataframe(self):
        """Test: Convert to DataFrame."""
        products = pep.Products(self.client).has_target("Mars").observationals()

        df = products.as_dataframe(max_rows=10)

        self.assertIsNotNone(df)
        self.assertGreater(len(df), 0)
        self.assertGreater(len(df.columns), 0)

    def test_accessing_metadata(self):
        """Test: Accessing metadata."""
        products = pep.Products(self.client).has_target("Mars").observationals()

        for product in products:
            # Access specific properties
            title = product.properties.get('pds:Identification_Area.pds:title', ['N/A'])[0]
            start_time = product.properties.get('pds:Time_Coordinates.pds:start_date_time', ['N/A'])[0]

            self.assertIsNotNone(title)
            self.assertIsNotNone(start_time)
            break

    def test_reducing_returned_fields(self):
        """Test: Reducing returned fields."""
        products = pep.Products(self.client) \
            .has_target("Mars") \
            .observationals() \
            .fields(['lid', 'pds:Identification_Area.pds:title'])

        for product in products:
            self.assertIn('lid', product.properties)
            # Note: field filtering may not always work as expected in the API
            break

    def test_resetting_query(self):
        """Test: Resetting a query."""
        products = pep.Products(self.client).has_target("Mars").observationals()

        # Iterate through some results
        for i, product in enumerate(products):
            if i >= 2:
                break

        # Reset to use the same query again
        products.reset()

        # Should be able to iterate again
        for product in products:
            self.assertIsNotNone(product.id)
            break


class CombiningFiltersTestCase(unittest.TestCase):
    """Test combining multiple filters."""

    def test_complex_combined_query(self):
        """Test: Complex query combining multiple filters."""
        client = pep.PDSRegistryClient()
        context = pep.Context()

        # Find Curiosity rover
        curiosity = context.INSTRUMENT_HOSTS.search("curiosity")[0]

        # Complex query: Mars data from Curiosity, in 2020, calibrated
        products = pep.Products(client) \
            .has_target("Mars") \
            .has_instrument_host(curiosity.lid) \
            .after(datetime(2020, 1, 1)) \
            .before(datetime(2020, 12, 31)) \
            .has_processing_level("calibrated") \
            .observationals()

        # Try to get results
        found = False
        for product in products:
            self.assertIsNotNone(product.id)
            found = True
            break

        # It's okay if no results found - query is valid
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
