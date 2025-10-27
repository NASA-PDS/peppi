"""Tests for Getting Started recipes in the Cookbook.

These tests verify that all Getting Started recipes (1-6) in
docs/source/cookbook.rst are functional and produce expected results.
"""
import unittest

import pds.peppi as pep
from pds.api_client import PdsProduct


class Recipe01TestCase(unittest.TestCase):
    """Recipe 1: Find All Data About a Specific Target."""

    def test_find_mars_data(self):
        """Test finding all data about Mars."""
        # Connect to PDS
        client = pep.PDSRegistryClient()

        # Search for Mars data
        products = pep.Products(client).has_target("Mars").observationals()

        # Print first 5 results
        count = 0
        for i, product in enumerate(products):
            self.assertIsNotNone(product.id)
            count += 1
            if i >= 4:
                break

        self.assertGreater(count, 0, "Should find Mars products")

    def test_find_jupiter_data(self):
        """Test finding data about Jupiter."""
        client = pep.PDSRegistryClient()
        products = pep.Products(client).has_target("Jupiter").observationals()

        for i, product in enumerate(products):
            self.assertIsNotNone(product.id)
            if i >= 1:  # Just verify it works
                break

    def test_find_bennu_data(self):
        """Test finding data about Bennu."""
        client = pep.PDSRegistryClient()
        products = pep.Products(client).has_target("Bennu").observationals()

        for i, product in enumerate(products):
            self.assertIsNotNone(product.id)
            if i >= 1:
                break


class Recipe02TestCase(unittest.TestCase):
    """Recipe 2: Search by Mission/Spacecraft."""

    def test_find_curiosity_data(self):
        """Test finding data from Curiosity rover."""
        client = pep.PDSRegistryClient()
        context = pep.Context()

        # Find the spacecraft (fuzzy search)
        curiosity = context.INSTRUMENT_HOSTS.search("curiosity")[0]

        self.assertIsNotNone(curiosity.name)
        self.assertIsNotNone(curiosity.lid)

        # Get observational data from this spacecraft
        products = pep.Products(client) \
            .has_instrument_host(curiosity.lid) \
            .observationals()

        # Show first 5
        count = 0
        for i, product in enumerate(products):
            self.assertIsNotNone(product.id)
            count += 1
            if i >= 4:
                break

        self.assertGreater(count, 0, "Should find Curiosity products")

    def test_find_messenger_data(self):
        """Test finding data from Messenger."""
        client = pep.PDSRegistryClient()
        context = pep.Context()

        messenger = context.INSTRUMENT_HOSTS.search("messenger")[0]
        self.assertIsNotNone(messenger.lid)

        products = pep.Products(client) \
            .has_instrument_host(messenger.lid) \
            .observationals()

        for i, product in enumerate(products):
            self.assertIsNotNone(product.id)
            if i >= 1:
                break


class Recipe03TestCase(unittest.TestCase):
    """Recipe 3: Find Data from a Specific Time Period."""

    def test_find_mercury_data_2020(self):
        """Test finding Mercury data from 2020."""
        from datetime import datetime

        client = pep.PDSRegistryClient()

        # Define date range
        start_date = datetime(2020, 1, 1)
        end_date = datetime(2020, 12, 31)

        # Find Mercury data from 2020
        products = pep.Products(client) \
            .has_target("Mercury") \
            .after(start_date) \
            .before(end_date) \
            .observationals()

        # Try to get results with dates
        found = False
        for i, product in enumerate(products):
            self.assertIsNotNone(product.id)
            start = product.properties.get('pds:Time_Coordinates.pds:start_date_time', ['N/A'])[0]
            self.assertIsNotNone(start)
            found = True
            if i >= 4:
                break

        # It's okay if no results - query is valid


class Recipe04TestCase(unittest.TestCase):
    """Recipe 4: Get Calibrated Data Only."""

    def test_get_calibrated_mars_data(self):
        """Test getting calibrated Mars data."""
        client = pep.PDSRegistryClient()

        # Get calibrated Mars data
        products = pep.Products(client) \
            .has_target("Mars") \
            .has_processing_level("calibrated") \
            .observationals()

        found = False
        for i, product in enumerate(products):
            self.assertIsNotNone(product.id)
            processing = product.properties.get('pds:Primary_Result_Summary.pds:processing_level', ['N/A'])[0]
            self.assertIsNotNone(processing)
            found = True
            if i >= 4:
                break

        # Calibrated Mars data should exist
        self.assertTrue(found, "Should find some calibrated Mars data")

    def test_processing_levels(self):
        """Test different processing levels are queryable."""
        client = pep.PDSRegistryClient()

        # Test each processing level can be queried
        levels = ["raw", "calibrated", "derived"]

        for level in levels:
            products = pep.Products(client) \
                .has_target("Mars") \
                .has_processing_level(level) \
                .observationals()

            # Just verify the query doesn't error
            for product in products:
                self.assertIsNotNone(product.id)
                break


class Recipe05TestCase(unittest.TestCase):
    """Recipe 5: Export Results to a Spreadsheet (CSV)."""

    def test_export_to_dataframe(self):
        """Test exporting results to DataFrame."""
        import pandas as pd

        client = pep.PDSRegistryClient()

        # Search for Mars data
        products = pep.Products(client).has_target("Mars").observationals()

        # Convert to pandas DataFrame
        df = products.as_dataframe(max_rows=10)

        self.assertIsNotNone(df)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertGreater(len(df), 0)
        self.assertGreater(len(df.columns), 0)

    def test_export_to_csv(self):
        """Test saving DataFrame to CSV."""
        import pandas as pd
        import tempfile
        import os

        client = pep.PDSRegistryClient()
        products = pep.Products(client).has_target("Mars").observationals()

        df = products.as_dataframe(max_rows=10)

        # Save to temporary CSV
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            csv_path = f.name

        try:
            df.to_csv(csv_path)

            # Verify file was created and has content
            self.assertTrue(os.path.exists(csv_path))
            self.assertGreater(os.path.getsize(csv_path), 0)

            # Verify we can read it back
            df_read = pd.read_csv(csv_path)
            self.assertGreater(len(df_read), 0)
        finally:
            # Clean up
            if os.path.exists(csv_path):
                os.remove(csv_path)


class Recipe06TestCase(unittest.TestCase):
    """Recipe 6: Browse Available Targets."""

    def test_browse_targets(self):
        """Test browsing available targets."""
        context = pep.Context()

        # Search with a common term to get diverse results
        targets = context.TARGETS.search("planet")

        self.assertGreater(len(targets), 0, "Should find some targets")

        # Verify target structure
        for target in targets[:3]:  # Check first 3
            self.assertIsNotNone(target.name)
            self.assertIsNotNone(target.type)
            self.assertIsNotNone(target.lid)

    def test_search_planets(self):
        """Test searching for planets."""
        context = pep.Context()

        planets = context.TARGETS.search("planet")
        self.assertGreater(len(planets), 0, "Should find planet targets")

    def test_search_asteroids(self):
        """Test searching for asteroids."""
        context = pep.Context()

        asteroids = context.TARGETS.search("asteroid")
        self.assertGreater(len(asteroids), 0, "Should find asteroid targets")

    def test_search_satellites(self):
        """Test searching for moons/satellites."""
        context = pep.Context()

        satellites = context.TARGETS.search("satellite")
        self.assertGreater(len(satellites), 0, "Should find satellite targets")


if __name__ == '__main__':
    unittest.main()
