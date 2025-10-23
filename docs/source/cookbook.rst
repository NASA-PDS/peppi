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

These recipes demonstrate complex queries and data processing workflows.

Recipe 13: Compare Data Coverage Across Multiple Targets
---------------------------------------------------------

**Goal:** Analyze how much data is available for different planetary bodies.

.. code-block:: python

    import pds.peppi as pep
    import pandas as pd

    client = pep.PDSRegistryClient()
    context = pep.Context()

    # Define targets to compare
    target_names = ["Mars", "Jupiter", "Saturn", "Venus", "Mercury"]

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

        df = products.as_dataframe(max_rows=10)

        count = len(df) if df is not None else 0

        results.append({
            'Target': target.name,
            'Type': target.type,
            'Sample Count': count
        })

    # Create comparison DataFrame
    comparison_df = pd.DataFrame(results)
    print(comparison_df)

Recipe 14: Build a Data Timeline
---------------------------------

**Goal:** Analyze when data was collected for a target over time.

.. code-block:: python

    import pds.peppi as pep
    import pandas as pd
    from datetime import datetime

    client = pep.PDSRegistryClient()

    # Get Mars data
    products = pep.Products(client) \
        .has_target("Mars") \
        .observationals()

    # Convert to DataFrame
    df = products.as_dataframe(max_rows=500)

    if df is not None and 'pds:Time_Coordinates.pds:start_date_time' in df.columns:
        # Convert to datetime
        df['start_date'] = pd.to_datetime(
            df['pds:Time_Coordinates.pds:start_date_time'],
            errors='coerce'
        )

        # Group by year
        df['year'] = df['start_date'].dt.year
        timeline = df.groupby('year').size()

        print("Mars data products by year:")
        print(timeline)

        # Find earliest and latest
        print(f"\nEarliest: {df['start_date'].min()}")
        print(f"Latest: {df['start_date'].max()}")
    else:
        print("No data available or no time coordinates")

Recipe 15: Find Overlapping Observations
-----------------------------------------

**Goal:** Find products from different instruments that observed the same target at the same time.

.. code-block:: python

    import pds.peppi as pep
    from datetime import datetime, timedelta

    client = pep.PDSRegistryClient()

    # Define a specific time window
    target_date = datetime(2020, 6, 15)
    window = timedelta(days=1)  # +/- 1 day

    # Search for Mars observations in this window
    products = pep.Products(client) \
        .has_target("Mars") \
        .after(target_date - window) \
        .before(target_date + window) \
        .observationals()

    # Group by instrument
    instruments = {}

    for product in products:
        inst = product.properties.get('ref_lid_instrument', ['Unknown'])[0]
        start = product.properties.get('pds:Time_Coordinates.pds:start_date_time', ['N/A'])[0]

        if inst not in instruments:
            instruments[inst] = []

        instruments[inst].append({
            'id': product.id,
            'start': start
        })

    # Display results
    print(f"Observations of Mars around {target_date.date()}:")
    for inst, obs_list in instruments.items():
        print(f"\n{inst}: {len(obs_list)} observations")
        for obs in obs_list[:3]:  # Show first 3
            print(f"  {obs['start']}")

Recipe 16: Create a Custom Data Report
---------------------------------------

**Goal:** Generate a formatted report about a dataset for documentation.

.. code-block:: python

    import pds.peppi as pep
    from datetime import datetime

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

        df = products.as_dataframe(max_rows=100)

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

            # Instruments
            if 'ref_lid_instrument' in df.columns:
                instruments = df['ref_lid_instrument'].value_counts()
                report_lines.append("\n  By Instrument:")
                for inst, count in instruments.head(5).items():
                    report_lines.append(f"    {inst}: {count}")

        # Write report
        report_text = '\n'.join(report_lines)
        with open(output_file, 'w') as f:
            f.write(report_text)

        print(report_text)
        print(f"\nReport saved to {output_file}")

    # Use it
    create_data_report("Mars", "mars_report.txt")

Recipe 17: Work with OSIRIS-REx Specialized Products
-----------------------------------------------------

**Goal:** Use mission-specific product classes for specialized functionality.

.. code-block:: python

    import pds.peppi as pep

    client = pep.PDSRegistryClient()

    # Use the OSIRIS-REx (OREX) specialized products class
    orex_products = pep.OrexProducts(client)

    # OrexProducts inherits all the standard filters
    products = orex_products.has_target("Bennu").observationals()

    print("OSIRIS-REx products about Bennu:")
    for i, product in enumerate(products):
        title = product.properties.get('pds:Identification_Area.pds:title', ['N/A'])[0]
        print(f"{i+1}. {title}")
        if i >= 9:
            break

.. note::
   Mission-specific product classes like ``OrexProducts`` can provide additional
   methods and filters specific to that mission's data structure. Check the
   :doc:`reference` for available specialized classes.

Recipe 18: Handle Large Result Sets Efficiently
------------------------------------------------

**Goal:** Process thousands of products without running out of memory.

.. code-block:: python

    import pds.peppi as pep

    client = pep.PDSRegistryClient()

    # Get only the fields we need
    fields = ['lid', 'pds:Identification_Area.pds:title']

    products = pep.Products(client) \
        .has_target("Mars") \
        .observationals() \
        .fields(fields)

    # Process in batches
    batch_size = 100
    processed = 0

    batch = []
    for product in products:
        batch.append(product.id)

        if len(batch) >= batch_size:
            # Process this batch
            print(f"Processing products {processed} to {processed + len(batch)}...")
            # Do something with the batch
            # save_to_database(batch)
            # process_data(batch)

            batch = []
            processed += batch_size

        if processed >= 1000:  # Stop after 1000 for this example
            break

    # Process remaining products
    if batch:
        print(f"Processing final {len(batch)} products...")

    print(f"Total processed: {processed + len(batch)}")

Recipe 19: Fuzzy Search Across Multiple Terms
----------------------------------------------

**Goal:** Use the Context's fuzzy search to handle uncertain or variant names.

.. code-block:: python

    import pds.peppi as pep

    context = pep.Context()

    # The search is typo-tolerant
    search_terms = [
        "jupyter",      # Typo of Jupiter
        "curiousity",   # Typo of Curiosity
        "venus",        # Correct
        "satturn",      # Typo of Saturn
    ]

    print("Fuzzy search results:\n")

    for term in search_terms:
        print(f"Searching for: '{term}'")

        # Search targets
        targets = context.TARGETS.search(term, limit=1)
        if targets:
            print(f"  → Found target: {targets[0].name}")

        # Search spacecraft
        spacecraft = context.INSTRUMENT_HOSTS.search(term, limit=1)
        if spacecraft:
            print(f"  → Found spacecraft: {spacecraft[0].name}")

        print()

Recipe 20: Build a Reusable Search Function
--------------------------------------------

**Goal:** Create a reusable function for common search patterns.

.. code-block:: python

    import pds.peppi as pep
    from datetime import datetime
    from typing import Optional

    def search_planetary_data(
        target: str,
        spacecraft: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        processing_level: Optional[str] = None,
        max_results: Optional[int] = 100
    ):
        """
        Flexible search function for planetary data.

        Args:
            target: Name of planetary body (e.g., "Mars", "Jupiter")
            spacecraft: Optional spacecraft/rover name
            start_date: Optional start date for temporal filter
            end_date: Optional end date for temporal filter
            processing_level: Optional processing level filter
            max_results: Maximum number of results to return

        Returns:
            pandas DataFrame with results
        """
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

    # Example usage
    df = search_planetary_data(
        target="Mars",
        spacecraft="curiosity",
        start_date=datetime(2020, 1, 1),
        processing_level="calibrated",
        max_results=50  # This gets passed as max_rows to as_dataframe()
    )

    if df is not None:
        print(f"Found {len(df)} products")
        print(df.head())

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
