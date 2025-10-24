========
Cookbook
========

This cookbook provides ready-to-use recipes for common tasks with Peppi. Copy and customize these examples for your own needs.

The recipes are organized by experience level:

- **Getting Started Recipes** - Simple, single-task examples for beginners
- **Intermediate Recipes** - Combining multiple filters and working with results
- **Advanced Recipes** - Complex queries and data processing

.. contents:: Recipe Index
   :local:
   :depth: 2

Getting Started Recipes
=======================

These recipes are perfect if you're new to Peppi or just want to accomplish a simple task quickly.

Recipe 1: Find All Data About a Specific Target
------------------------------------------------

**Goal:** Search for all observational data about a specific planetary body.

.. code-block:: python

    import pds.peppi as pep

    # Connect to PDS
    client = pep.PDSRegistryClient()

    # Search for Mars data
    products = pep.Products(client).has_target("Mars").observationals()

    # Print first 5 results
    for i, product in enumerate(products):
        print(f"{i+1}. {product.id}")
        if i >= 4:
            break

**Try it with other targets:**

- "Jupiter"
- "Moon"
- "Bennu"
- "Enceladus"
- "Venus"

Recipe 2: Search by Mission/Spacecraft
---------------------------------------

**Goal:** Find data from a specific mission or spacecraft.

.. code-block:: python

    import pds.peppi as pep

    client = pep.PDSRegistryClient()
    context = pep.Context()

    # Find the spacecraft (fuzzy search)
    curiosity = context.INSTRUMENT_HOSTS.search("curiosity")[0]

    print(f"Found: {curiosity.name}")
    print(f"LID: {curiosity.lid}")

    # Get observational data from this spacecraft
    products = pep.Products(client) \
        .has_instrument_host(curiosity.lid) \
        .observationals()

    # Show first 5
    for i, product in enumerate(products):
        print(f"{i+1}. {product.id}")
        if i >= 4:
            break

**Other spacecraft to try:**

- "Perseverance"
- "Juno"
- "Cassini"
- "Messenger"
- "New Horizons"

Recipe 3: Find Data from a Specific Time Period
------------------------------------------------

**Goal:** Search for data collected within a specific date range.

.. code-block:: python

    import pds.peppi as pep
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

    # Print results with dates
    for i, product in enumerate(products):
        start = product.properties.get('pds:Time_Coordinates.pds:start_date_time', ['N/A'])[0]
        print(f"{i+1}. {product.id}")
        print(f"   Start: {start}")
        if i >= 4:
            break

Recipe 4: Get Calibrated Data Only
-----------------------------------

**Goal:** Find only calibrated (processed) data, not raw measurements.

.. code-block:: python

    import pds.peppi as pep

    client = pep.PDSRegistryClient()

    # Get calibrated Mars data
    products = pep.Products(client) \
        .has_target("Mars") \
        .has_processing_level("calibrated") \
        .observationals()

    for i, product in enumerate(products):
        processing = product.properties.get('pds:Primary_Result_Summary.pds:processing_level', ['N/A'])[0]
        print(f"{i+1}. {product.id}")
        print(f"   Processing Level: {processing}")
        if i >= 4:
            break

**Processing levels:**

- ``"telemetry"`` - Raw transmission
- ``"raw"`` - Unprocessed data
- ``"partially-processed"`` - Some processing
- ``"calibrated"`` - Fully calibrated
- ``"derived"`` - Higher-level products

Recipe 5: Export Results to a Spreadsheet (CSV)
------------------------------------------------

**Goal:** Save search results to a CSV file for use in Excel, Google Sheets, etc.

.. code-block:: python

    import pds.peppi as pep

    client = pep.PDSRegistryClient()

    # Search for Mars data
    products = pep.Products(client).has_target("Mars").observationals()

    # Convert to pandas DataFrame
    df = products.as_dataframe(max_rows=100)  # Limit to 100 rows for testing

    # Save to CSV
    df.to_csv('mars_data.csv')

    print(f"Saved {len(df)} products to mars_data.csv")
    print(f"Columns: {list(df.columns)}")

Recipe 6: Browse Available Targets
-----------------------------------

**Goal:** See what planetary bodies have data available in the PDS.

.. code-block:: python

    import pds.peppi as pep

    context = pep.Context()

    # Search with a broad term to see diverse targets
    # (Searching with empty string can cause issues with fuzzy matching)
    targets = context.TARGETS.search("planet")

    print("Available targets:")
    for target in targets:
        print(f"  {target.name} ({target.type})")
        print(f"    LID: {target.lid}")
        print()

**Search for specific types:**

.. code-block:: python

    # Find planets
    planets = context.TARGETS.search("planet")

    # Find asteroids
    asteroids = context.TARGETS.search("asteroid")

    # Find moons
    moons = context.TARGETS.search("satellite")

Intermediate Recipes
====================

These recipes combine multiple filters and show you how to work with results more effectively.

Recipe 7: Find Mission-Specific Data in a Date Range
-----------------------------------------------------

**Goal:** Get data from a specific spacecraft about a specific target during a specific time period.

.. code-block:: python

    import pds.peppi as pep
    from datetime import datetime

    client = pep.PDSRegistryClient()
    context = pep.Context()

    # Find the Messenger spacecraft
    messenger = context.INSTRUMENT_HOSTS.search("messenger")[0]

    # Get Mercury data from Messenger before January 2012
    products = pep.Products(client) \
        .has_target("Mercury") \
        .has_instrument_host(messenger.lid) \
        .before(datetime(2012, 1, 23)) \
        .observationals()

    # Convert to DataFrame for analysis
    df = products.as_dataframe(max_rows=50)

    if df is not None:
        print(f"Found {len(df)} products")
        print("\nSample:")
        print(df[['title', 'pds:Time_Coordinates.pds:start_date_time']].head())
    else:
        print("No products found")

Recipe 8: Compare Data from Multiple Processing Levels
-------------------------------------------------------

**Goal:** See how many products are available at different processing levels.

.. code-block:: python

    import pds.peppi as pep

    client = pep.PDSRegistryClient()

    levels = ["raw", "calibrated", "derived"]
    counts = {}

    for level in levels:
        products = pep.Products(client) \
            .has_target("Mars") \
            .has_processing_level(level) \
            .observationals()

        # Count by converting to DataFrame with small limit
        df = products.as_dataframe(max_rows=1)
        counts[level] = len(df) if df is not None else 0

    print("Mars data by processing level:")
    for level, count in counts.items():
        print(f"  {level}: {count} products (sample)")

Recipe 9: Find Data and Get DOI for Citation
---------------------------------------------

**Goal:** Find data products and get their DOI for proper citation in papers.

.. code-block:: python

    import pds.peppi as pep

    client = pep.PDSRegistryClient()

    # Search for Bennu data from OSIRIS-REx
    products = pep.Products(client) \
        .has_target("Bennu") \
        .observationals()

    # Look for DOIs in the results
    print("Products with DOIs:")
    found = 0
    for product in products:
        doi = product.properties.get('pds:Citation_Information.pds:doi', [None])[0]
        if doi:
            title = product.properties.get('pds:Identification_Area.pds:title', ['N/A'])[0]
            print(f"\nTitle: {title}")
            print(f"DOI: {doi}")
            print(f"Product: {product.id}")
            found += 1
            if found >= 5:
                break

    if found == 0:
        print("No products with DOIs found in initial results")

Recipe 10: Search for Collections, Then Get Their Products
-----------------------------------------------------------

**Goal:** Find collections of data, then search within a specific collection.

.. code-block:: python

    import pds.peppi as pep

    client = pep.PDSRegistryClient()

    # First, find collections about Mars
    collections = pep.Products(client) \
        .has_target("Mars") \
        .collections()

    # Get first collection
    for collection in collections:
        collection_lid = collection.properties.get('lid', [None])[0]
        title = collection.properties.get('pds:Identification_Area.pds:title', ['N/A'])[0]

        print(f"Collection: {title}")
        print(f"LID: {collection_lid}")

        # Now get products from this collection
        collection_products = pep.Products(client) \
            .of_collection(collection_lid) \
            .observationals()

        print(f"\nFirst 3 products in this collection:")
        for i, product in enumerate(collection_products):
            print(f"  {i+1}. {product.id}")
            if i >= 2:
                break

        break  # Only show first collection

Recipe 11: Filter Results by Title Keyword
-------------------------------------------

**Goal:** Use custom filters to search by keywords in the title.

.. code-block:: python

    import pds.peppi as pep

    client = pep.PDSRegistryClient()

    # Search for products with "image" in the title about Mars
    products = pep.Products(client) \
        .has_target("Mars") \
        .filter('pds:Identification_Area.pds:title like "*image*"') \
        .observationals()

    print("Products with 'image' in title:")
    for i, product in enumerate(products):
        title = product.properties.get('pds:Identification_Area.pds:title', ['N/A'])[0]
        print(f"{i+1}. {title}")
        if i >= 9:
            break

Recipe 12: Extract Specific Metadata Fields Only
-------------------------------------------------

**Goal:** For better performance, only retrieve the metadata fields you need.

.. code-block:: python

    import pds.peppi as pep

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

    # Results will only contain the specified fields
    for i, product in enumerate(products):
        print(f"{i+1}. {product.properties.get('pds:Identification_Area.pds:title', ['N/A'])[0]}")
        print(f"   Start: {product.properties.get('pds:Time_Coordinates.pds:start_date_time', ['N/A'])[0]}")
        if i >= 4:
            break

Advanced Recipes
================

These recipes demonstrate complex queries and data processing workflows. For each advanced recipe,
we provide an overview here with key code snippets, and link to **interactive Jupyter notebooks**
that include complete implementations, visualizations, and explanations.

All interactive notebooks are available in the `NASA-PDS/search-api-notebook repository <https://github.com/NASA-PDS/search-api-notebook/tree/main/notebooks/peppi-advanced>`_.

Recipe 13: Compare Data Coverage Across Multiple Targets
---------------------------------------------------------

**Goal:** Programmatically compare data availability across different planetary bodies.

This recipe shows how to query multiple targets in a loop, aggregate results, and create
comparison DataFrames and visualizations.

.. code-block:: python

    import pds.peppi as pep
    import pandas as pd

    client = pep.PDSRegistryClient()
    context = pep.Context()

    target_names = ["Mars", "Jupiter", "Saturn", "Venus", "Mercury"]
    results = []

    for target_name in target_names:
        targets = context.TARGETS.search(target_name)
        if targets:
            products = pep.Products(client).has_target(targets[0].lid).observationals()
            df = products.as_dataframe(max_rows=10)
            results.append({'Target': targets[0].name, 'Sample Count': len(df) if df else 0})

    comparison_df = pd.DataFrame(results)

.. note::
   **Interactive Notebook:** For the complete implementation with visualizations, see
   `recipe-13-compare-target-coverage.ipynb <https://github.com/NASA-PDS/search-api-notebook/blob/main/notebooks/peppi-advanced/recipe-13-compare-target-coverage.ipynb>`_

Recipe 14: Build a Data Timeline
---------------------------------

**Goal:** Analyze temporal patterns in data collection over time.

This recipe demonstrates how to extract temporal metadata, group by time periods,
visualize timelines, and identify data gaps and mission phases.

.. code-block:: python

    import pds.peppi as pep
    import pandas as pd

    client = pep.PDSRegistryClient()
    products = pep.Products(client).has_target("Mars").observationals()
    df = products.as_dataframe(max_rows=500)

    if df is not None and 'pds:Time_Coordinates.pds:start_date_time' in df.columns:
        df['start_date'] = pd.to_datetime(df['pds:Time_Coordinates.pds:start_date_time'], errors='coerce')
        df['year'] = df['start_date'].dt.year
        timeline = df.groupby('year').size()
        print("Mars data products by year:")
        print(timeline)

.. note::
   **Interactive Notebook:** For complete timeline analysis with visualizations, see
   `recipe-14-build-data-timeline.ipynb <https://github.com/NASA-PDS/search-api-notebook/blob/main/notebooks/peppi-advanced/recipe-14-build-data-timeline.ipynb>`_

Recipe 15: Find Overlapping Observations
-----------------------------------------

**Goal:** Discover multi-instrument campaigns and coordinated observations.

This recipe shows how to use temporal windows to find products from different instruments
that observed the same target simultaneously.

.. code-block:: python

    import pds.peppi as pep
    from datetime import datetime, timedelta

    client = pep.PDSRegistryClient()
    target_date = datetime(2020, 6, 15)
    window = timedelta(days=1)

    products = pep.Products(client) \
        .has_target("Mars") \
        .after(target_date - window) \
        .before(target_date + window) \
        .observationals()

    # Group by instrument to find overlapping observations
    for product in products:
        inst = product.properties.get('ref_lid_instrument', ['Unknown'])[0]
        print(f"{inst}: {product.id}")

.. note::
   **Interactive Notebook:** For complete overlap analysis with grouping, see
   `recipe-15-overlapping-observations.ipynb <https://github.com/NASA-PDS/search-api-notebook/blob/main/notebooks/peppi-advanced/recipe-15-overlapping-observations.ipynb>`_

Recipe 16: Create a Custom Data Report
---------------------------------------

**Goal:** Generate formatted reports about PDS data availability.

This recipe demonstrates how to extract and format metadata programmatically and
create reusable report templates.

.. code-block:: python

    import pds.peppi as pep

    def create_data_report(target_name):
        client = pep.PDSRegistryClient()
        context = pep.Context()

        target = context.TARGETS.search(target_name)[0]
        products = pep.Products(client).has_target(target.lid).observationals()
        df = products.as_dataframe(max_rows=100)

        print(f"PDS Data Report for {target.name}")
        print(f"Products found: {len(df) if df else 0}")
        # Add more report sections...

    create_data_report("Mars")

.. note::
   **Interactive Notebook:** For the complete report generation function with formatting, see
   `recipe-16-custom-data-report.ipynb <https://github.com/NASA-PDS/search-api-notebook/blob/main/notebooks/peppi-advanced/recipe-16-custom-data-report.ipynb>`_

Recipe 17: Work with OSIRIS-REx Specialized Products
-----------------------------------------------------

**Goal:** Use mission-specific product classes for specialized functionality.

This recipe shows how to leverage specialized product classes like ``OrexProducts`` that
provide mission-specific features while inheriting standard Peppi filters.

.. code-block:: python

    import pds.peppi as pep

    client = pep.PDSRegistryClient()
    orex_products = pep.OrexProducts(client)

    # Use standard filters with mission-specific class
    products = orex_products.has_target("Bennu").observationals()

    for i, product in enumerate(products):
        print(product.properties.get('pds:Identification_Area.pds:title', ['N/A'])[0])
        if i >= 4:
            break

.. note::
   **Interactive Notebook:** For complete OSIRIS-REx examples, see
   `recipe-17-orex-products.ipynb <https://github.com/NASA-PDS/search-api-notebook/blob/main/notebooks/peppi-advanced/recipe-17-orex-products.ipynb>`_

Recipe 18: Handle Large Result Sets Efficiently
------------------------------------------------

**Goal:** Process thousands of products without memory issues.

This recipe demonstrates field filtering for efficiency, batch processing patterns,
and manual pagination management.

.. code-block:: python

    import pds.peppi as pep

    client = pep.PDSRegistryClient()

    # Request only needed fields for efficiency
    fields = ['lid', 'pds:Identification_Area.pds:title']
    products = pep.Products(client) \
        .has_target("Mars") \
        .observationals() \
        .fields(fields)

    # Process in batches
    batch_size = 100
    batch = []

    for product in products:
        batch.append(product.id)
        if len(batch) >= batch_size:
            # Process batch
            print(f"Processing {len(batch)} products...")
            batch = []

.. note::
   **Interactive Notebook:** For complete batch processing patterns, see
   `recipe-18-large-result-sets.ipynb <https://github.com/NASA-PDS/search-api-notebook/blob/main/notebooks/peppi-advanced/recipe-18-large-result-sets.ipynb>`_

Recipe 19: Fuzzy Search Across Multiple Terms
----------------------------------------------

**Goal:** Leverage fuzzy search to handle typos and uncertain names.

This recipe demonstrates the Context system's typo-tolerant search capabilities
for handling spelling variations and uncertain names.

.. code-block:: python

    import pds.peppi as pep

    context = pep.Context()

    # Fuzzy search handles typos
    typos = ["jupyter", "curiousity", "satturn"]  # Misspellings

    for term in typos:
        targets = context.TARGETS.search(term, limit=1)
        if targets:
            print(f"'{term}' → Found: {targets[0].name}")

.. note::
   **Interactive Notebook:** For complete fuzzy search examples across targets and spacecraft, see
   `recipe-19-fuzzy-search.ipynb <https://github.com/NASA-PDS/search-api-notebook/blob/main/notebooks/peppi-advanced/recipe-19-fuzzy-search.ipynb>`_

Recipe 20: Build a Reusable Search Function
--------------------------------------------

**Goal:** Create flexible, parameterized search functions for common patterns.

This recipe shows how to design reusable search functions with optional filters,
type hints, and sensible defaults.

.. code-block:: python

    import pds.peppi as pep
    from datetime import datetime
    from typing import Optional

    def search_planetary_data(
        target: str,
        spacecraft: Optional[str] = None,
        start_date: Optional[datetime] = None,
        processing_level: Optional[str] = None,
        max_results: int = 100
    ):
        """Flexible search function for planetary data."""
        client = pep.PDSRegistryClient()
        context = pep.Context()

        query = pep.Products(client).has_target(target)

        if spacecraft:
            host = context.INSTRUMENT_HOSTS.search(spacecraft)[0]
            query = query.has_instrument_host(host.lid)
        if start_date:
            query = query.after(start_date)
        if processing_level:
            query = query.has_processing_level(processing_level)

        return query.observationals().as_dataframe(max_rows=max_results)

    # Use with different combinations
    df = search_planetary_data("Mars", spacecraft="curiosity", max_results=50)

.. note::
   **Interactive Notebook:** For complete examples with multiple usage patterns, see
   `recipe-20-reusable-search-function.ipynb <https://github.com/NASA-PDS/search-api-notebook/blob/main/notebooks/peppi-advanced/recipe-20-reusable-search-function.ipynb>`_

Tips for Creating Your Own Recipes
===================================

1. **Start Simple**: Begin with a basic query and add complexity gradually
2. **Test Small**: Always use ``max_rows`` or ``enumerate`` with breaks when testing
3. **Check Fields**: Use ``.properties.keys()`` to see what metadata is available
4. **Handle None**: Always check if DataFrames are None before processing
5. **Use Context**: Leverage fuzzy search to find IDs instead of guessing
6. **Read Errors**: Python error messages usually tell you exactly what's wrong

Need More Help?
===============

- Can't find what you're looking for? Check the :doc:`reference` for all available methods
- Need to understand a concept better? See the :doc:`user_guide`
- Have a recipe to share? Open a `discussion <https://github.com/NASA-PDS/peppi/discussions>`_
- Found a bug? Create an `issue <https://github.com/NASA-PDS/peppi/issues>`_
