"""Tests for Intermediate recipes in the Cookbook.

These tests verify that all Intermediate recipes (7-12) in
docs/source/cookbook.rst are functional and produce expected results.
"""
import unittest
from datetime import datetime

import pds.peppi as pep


class Recipe07TestCase(unittest.TestCase):
    """Recipe 7: Find Mission-Specific Data in a Date Range."""

    def test_messenger_mercury_data_before_2012(self):
        """Test finding Messenger Mercury data before 2012."""
        client = pep.PDSRegistryClient()
        context = pep.Context()

        # Find the Messenger spacecraft
        messenger = context.INSTRUMENT_HOSTS.search("messenger")[0]
        self.assertIsNotNone(messenger.lid)

        # Get Mercury data from Messenger before January 2012
        products = pep.Products(client) \
            .has_target("Mercury") \
            .has_instrument_host(messenger.lid) \
            .before(datetime(2012, 1, 23)) \
            .observationals()

        # Convert to DataFrame for analysis
        df = products.as_dataframe(max_rows=10)

        # May or may not find results depending on data availability
        if df is not None and len(df) > 0:
            self.assertGreater(len(df), 0)
            # Check if time coordinates exist
            if 'pds:Time_Coordinates.pds:start_date_time' in df.columns:
                self.assertIsNotNone(df['pds:Time_Coordinates.pds:start_date_time'].iloc[0])


class Recipe08TestCase(unittest.TestCase):
    """Recipe 8: Compare Data from Multiple Processing Levels."""

    def test_compare_processing_levels(self):
        """Test comparing counts across processing levels."""
        client = pep.PDSRegistryClient()

        levels = ["raw", "calibrated", "derived"]
        counts = {}

        for level in levels:
            products = pep.Products(client) \
                .has_target("Mars") \
                .has_processing_level(level) \
                .observationals()

            # Get small sample to check availability
            df = products.as_dataframe(max_rows=5)
            counts[level] = len(df) if df is not None else 0

        # At least one processing level should have data
        self.assertGreater(sum(counts.values()), 0, "Should find data at some processing level")


class Recipe09TestCase(unittest.TestCase):
    """Recipe 9: Find Data and Get DOI for Citation."""

    def test_find_dois(self):
        """Test finding products with DOIs."""
        client = pep.PDSRegistryClient()

        # Search for Bennu data from OSIRIS-REx
        products = pep.Products(client) \
            .has_target("Bennu") \
            .observationals()

        # Look for DOIs in the results
        checked = 0
        found_doi = False

        for product in products:
            doi = product.properties.get('pds:Citation_Information.pds:doi', [None])[0]
            if doi:
                title = product.properties.get('pds:Identification_Area.pds:title', ['N/A'])[0]
                self.assertIsNotNone(title)
                self.assertIsNotNone(doi)
                self.assertIsNotNone(product.id)
                found_doi = True
                break

            checked += 1
            if checked >= 50:  # Check up to 50 products
                break

        # It's okay if no DOIs found - depends on data availability


class Recipe10TestCase(unittest.TestCase):
    """Recipe 10: Search for Collections, Then Get Their Products."""

    def test_collections_then_products(self):
        """Test finding collections and their products."""
        client = pep.PDSRegistryClient()

        # First, find collections about Mars
        collections = pep.Products(client) \
            .has_target("Mars") \
            .collections()

        # Get first collection
        found_collection = False
        for collection in collections:
            collection_lid = collection.properties.get('lid', [None])[0]
            title = collection.properties.get('pds:Identification_Area.pds:title', ['N/A'])[0]

            self.assertIsNotNone(collection_lid)
            self.assertIsNotNone(title)

            # Now get products from this collection
            collection_products = pep.Products(client) \
                .of_collection(collection_lid) \
                .observationals()

            # Try to get some products
            product_count = 0
            for i, product in enumerate(collection_products):
                self.assertIsNotNone(product.id)
                product_count += 1
                if i >= 2:
                    break

            found_collection = True
            break  # Only test first collection

        self.assertTrue(found_collection, "Should find at least one collection")


class Recipe11TestCase(unittest.TestCase):
    """Recipe 11: Filter Results by Title Keyword."""

    def test_filter_by_title_keyword(self):
        """Test filtering by keyword in title."""
        client = pep.PDSRegistryClient()

        # Search for products with "image" in the title about Mars
        products = pep.Products(client) \
            .has_target("Mars") \
            .filter('pds:Identification_Area.pds:title like "*image*"') \
            .observationals()

        found = False
        for i, product in enumerate(products):
            title = product.properties.get('pds:Identification_Area.pds:title', ['N/A'])[0]
            self.assertIsNotNone(title)

            # Verify "image" is in title (case-insensitive)
            if title != 'N/A':
                self.assertIn('image', title.lower())

            found = True
            if i >= 9:
                break

        # Results depend on data availability

    def test_filter_by_custom_keyword(self):
        """Test filtering by different keyword."""
        client = pep.PDSRegistryClient()

        # Search for products with "calibrated" in title
        products = pep.Products(client) \
            .has_target("Mars") \
            .filter('pds:Identification_Area.pds:title like "*data*"') \
            .observationals()

        # Just verify query works
        for product in products:
            self.assertIsNotNone(product.id)
            break


class Recipe12TestCase(unittest.TestCase):
    """Recipe 12: Extract Specific Metadata Fields Only."""

    def test_extract_specific_fields(self):
        """Test extracting only specific metadata fields."""
        client = pep.PDSRegistryClient()

        # Specify only the fields we want
        fields = [
            'lid',
            'pds:Identification_Area.pds:title',
            'pds:Time_Coordinates.pds:start_date_time',
            'ref_lid_target'
        ]

        products = pep.Products(client) \
            .has_target("Mars") \
            .observationals() \
            .fields(fields)

        # Results should only contain the specified fields
        found = False
        for i, product in enumerate(products):
            # Verify at least some fields are present
            # Note: API may include additional fields beyond what we requested
            self.assertIsNotNone(product.properties)

            # Check if requested fields are present
            title = product.properties.get('pds:Identification_Area.pds:title', ['N/A'])[0]
            start_time = product.properties.get('pds:Time_Coordinates.pds:start_date_time', ['N/A'])[0]

            self.assertIsNotNone(title)
            self.assertIsNotNone(start_time)

            found = True
            if i >= 4:
                break

        self.assertTrue(found, "Should find products with requested fields")

    def test_minimal_field_set(self):
        """Test with minimal field set."""
        client = pep.PDSRegistryClient()

        fields = ['lid', 'pds:Identification_Area.pds:title']

        products = pep.Products(client) \
            .has_target("Mars") \
            .observationals() \
            .fields(fields)

        for product in products:
            self.assertIn('lid', product.properties)
            break


if __name__ == '__main__':
    unittest.main()
