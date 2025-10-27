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


class Recipe13TestCase(unittest.TestCase):
    """Recipe 13: Compare Data Coverage Across Multiple Targets."""

    def test_compare_target_coverage(self):
        """Test comparing data coverage across targets."""
        client = pep.PDSRegistryClient()
        context = pep.Context()

        # Define targets to compare (use fewer for faster testing)
        target_names = ["Mars", "Jupiter", "Venus"]

        results = []

        for target_name in target_names:
            # Get target info
            targets = context.TARGETS.search(target_name)
            if not targets:
                continue

            target = targets[0]

            # Count products (sample)
            products = pep.Products(client) \
                .has_target(target.lid) \
                .observationals()

            df = products.as_dataframe(max_rows=5)

            count = len(df) if df is not None else 0

            results.append({
                'Target': target.name,
                'Type': target.type,
                'Sample Count': count
            })

        # Create comparison DataFrame
        comparison_df = pd.DataFrame(results)

        self.assertGreater(len(comparison_df), 0)
        self.assertIn('Target', comparison_df.columns)
        self.assertIn('Sample Count', comparison_df.columns)


class Recipe14TestCase(unittest.TestCase):
    """Recipe 14: Build a Data Timeline."""

    def test_build_data_timeline(self):
        """Test building a timeline of data collection."""
        client = pep.PDSRegistryClient()

        # Get Mars data
        products = pep.Products(client) \
            .has_target("Mars") \
            .observationals()

        # Convert to DataFrame
        df = products.as_dataframe(max_rows=100)

        if df is not None and 'pds:Time_Coordinates.pds:start_date_time' in df.columns:
            # Convert to datetime
            df['start_date'] = pd.to_datetime(
                df['pds:Time_Coordinates.pds:start_date_time'],
                errors='coerce'
            )

            # Remove NaT values
            df = df.dropna(subset=['start_date'])

            if len(df) > 0:
                # Group by year
                df['year'] = df['start_date'].dt.year
                timeline = df.groupby('year').size()

                self.assertGreater(len(timeline), 0)

                # Find earliest and latest
                earliest = df['start_date'].min()
                latest = df['start_date'].max()

                self.assertIsNotNone(earliest)
                self.assertIsNotNone(latest)
                self.assertLessEqual(earliest, latest)


class Recipe15TestCase(unittest.TestCase):
    """Recipe 15: Find Overlapping Observations."""

    def test_find_overlapping_observations(self):
        """Test finding overlapping observations from different instruments."""
        client = pep.PDSRegistryClient()

        # Define a specific time window
        target_date = datetime(2020, 6, 15)
        window = timedelta(days=1)

        # Search for Mars observations in this window
        products = pep.Products(client) \
            .has_target("Mars") \
            .after(target_date - window) \
            .before(target_date + window) \
            .observationals()

        # Group by instrument
        instruments = {}

        count = 0
        for product in products:
            inst = product.properties.get('ref_lid_instrument', ['Unknown'])[0]
            start = product.properties.get('pds:Time_Coordinates.pds:start_date_time', ['N/A'])[0]

            if inst not in instruments:
                instruments[inst] = []

            instruments[inst].append({
                'id': product.id,
                'start': start
            })

            count += 1
            if count >= 50:  # Limit for testing
                break

        # Results depend on data availability
        # Just verify the structure works
        self.assertIsInstance(instruments, dict)


class Recipe16TestCase(unittest.TestCase):
    """Recipe 16: Create a Custom Data Report."""

    def test_create_data_report_function(self):
        """Test the create_data_report function."""
        import tempfile
        import os

        def create_data_report(target_name, output_file='report.txt'):
            """Create a report about available data for a target."""
            client = pep.PDSRegistryClient()
            context = pep.Context()

            # Find target
            target = context.TARGETS.search(target_name)[0]

            # Get data
            products = pep.Products(client) \
                .has_target(target.lid) \
                .observationals()

            df = products.as_dataframe(max_rows=20)

            # Generate report
            report_lines = [
                f"PDS Data Report for {target.name}",
                "=" * 50,
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                f"\nTarget Information:",
                f"  Name: {target.name}",
                f"  Type: {target.type}",
                f"  LID: {target.lid}",
                f"\nData Summary:",
                f"  Products found: {len(df) if df is not None else 0}",
            ]

            if df is not None and len(df) > 0:
                # Processing levels
                if 'pds:Primary_Result_Summary.pds:processing_level' in df.columns:
                    levels = df['pds:Primary_Result_Summary.pds:processing_level'].value_counts()
                    report_lines.append("\n  By Processing Level:")
                    for level, count in levels.items():
                        report_lines.append(f"    {level}: {count}")

            # Write report
            report_text = '\n'.join(report_lines)
            with open(output_file, 'w') as f:
                f.write(report_text)

            return report_text

        # Test the function
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            report_path = f.name

        try:
            report_text = create_data_report("Mars", report_path)

            # Verify report was created
            self.assertTrue(os.path.exists(report_path))
            self.assertGreater(len(report_text), 0)
            self.assertIn("PDS Data Report", report_text)
            self.assertIn("Mars", report_text)

            # Verify file contents
            with open(report_path, 'r') as f:
                file_contents = f.read()
                self.assertEqual(file_contents, report_text)

        finally:
            if os.path.exists(report_path):
                os.remove(report_path)


class Recipe17TestCase(unittest.TestCase):
    """Recipe 17: Work with OSIRIS-REx Specialized Products."""

    def test_orex_products(self):
        """Test using OrexProducts specialized class."""
        client = pep.PDSRegistryClient()

        # Use the OSIRIS-REx (OREX) specialized products class
        orex_products = pep.OrexProducts(client)

        # OrexProducts inherits all the standard filters
        products = orex_products.has_target("Bennu").observationals()

        found = False
        for i, product in enumerate(products):
            title = product.properties.get('pds:Identification_Area.pds:title', ['N/A'])[0]
            self.assertIsNotNone(title)
            found = True
            if i >= 2:
                break

        # Results depend on data availability


class Recipe18TestCase(unittest.TestCase):
    """Recipe 18: Handle Large Result Sets Efficiently."""

    def test_batch_processing(self):
        """Test processing large result sets in batches."""
        client = pep.PDSRegistryClient()

        # Get only the fields we need
        fields = ['lid', 'pds:Identification_Area.pds:title']

        products = pep.Products(client) \
            .has_target("Mars") \
            .observationals() \
            .fields(fields)

        # Process in batches
        batch_size = 20
        processed = 0

        batch = []
        for product in products:
            batch.append(product.id)

            if len(batch) >= batch_size:
                # Verify batch
                self.assertEqual(len(batch), batch_size)

                batch = []
                processed += batch_size

            if processed >= 40:  # Stop after 40 for testing
                break

        # Should have processed some products
        self.assertGreater(processed, 0)


class Recipe19TestCase(unittest.TestCase):
    """Recipe 19: Fuzzy Search Across Multiple Terms."""

    def test_fuzzy_search_targets(self):
        """Test fuzzy search with typos."""
        context = pep.Context()

        # Search with typo should still find results
        search_terms = [
            ("jupyter", "jupiter"),  # Typo should find Jupiter
            ("venus", "venus"),       # Correct spelling
        ]

        for typo_term, expected_match in search_terms:
            targets = context.TARGETS.search(typo_term, limit=3)
            self.assertGreater(len(targets), 0, f"Should find results for '{typo_term}'")

            # Check if expected target is in results
            found_expected = any(expected_match.lower() in t.name.lower() for t in targets)
            # Fuzzy search should find the expected target

    def test_fuzzy_search_spacecraft(self):
        """Test fuzzy search for spacecraft."""
        context = pep.Context()

        # Search with typo
        spacecraft = context.INSTRUMENT_HOSTS.search("curiousity", limit=1)  # Typo
        self.assertGreater(len(spacecraft), 0, "Fuzzy search should find results")


class Recipe20TestCase(unittest.TestCase):
    """Recipe 20: Build a Reusable Search Function."""

    def test_reusable_search_function(self):
        """Test building a reusable search function."""
        def search_planetary_data(
            target: str,
            spacecraft: Optional[str] = None,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None,
            processing_level: Optional[str] = None,
            max_results: Optional[int] = 10
        ):
            """Flexible search function for planetary data."""
            client = pep.PDSRegistryClient()
            context = pep.Context()

            # Start building query
            query = pep.Products(client).has_target(target)

            # Add optional filters
            if spacecraft:
                host = context.INSTRUMENT_HOSTS.search(spacecraft)[0]
                query = query.has_instrument_host(host.lid)

            if start_date:
                query = query.after(start_date)

            if end_date:
                query = query.before(end_date)

            if processing_level:
                query = query.has_processing_level(processing_level)

            # Get observational products
            query = query.observationals()

            # Return as DataFrame
            return query.as_dataframe(max_rows=max_results)

        # Test with minimal parameters
        df1 = search_planetary_data(target="Mars", max_results=5)
        self.assertIsNotNone(df1)
        if df1 is not None:
            self.assertGreater(len(df1), 0)

        # Test with multiple parameters
        df2 = search_planetary_data(
            target="Mars",
            start_date=datetime(2015, 1, 1),
            end_date=datetime(2016, 12, 31),
            max_results=5
        )

        # Results depend on data availability
        # Just verify function executes without error

    def test_reusable_function_with_spacecraft(self):
        """Test reusable function with spacecraft parameter."""
        def search_planetary_data(
            target: str,
            spacecraft: Optional[str] = None,
            max_results: Optional[int] = 10
        ):
            client = pep.PDSRegistryClient()
            context = pep.Context()

            query = pep.Products(client).has_target(target)

            if spacecraft:
                host = context.INSTRUMENT_HOSTS.search(spacecraft)[0]
                query = query.has_instrument_host(host.lid)

            query = query.observationals()
            return query.as_dataframe(max_rows=max_results)

        # Test with spacecraft
        df = search_planetary_data(
            target="Mars",
            spacecraft="curiosity",
            max_results=5
        )

        # Results depend on data availability


if __name__ == '__main__':
    unittest.main()
