========
Cookbook
========

This cookbook provides ready-to-use recipes for common tasks with Peppi. Copy and customize these examples for your own needs.
Beware, that most recipes may return large result sets. When testing, always limit the number of results using ``max_rows`` or breaking after a few iterations.
But when you combined the multiple filters for your use case, making your own recipes, you may remove those limits to get the full results.

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
    products = pep.Products(client).has_target("Mars").collections()

    # Convert to pandas DataFrame
    df = products.as_dataframe(max_rows=100)  # Limit to 100 rows for testing

    # Save to CSV
    df.to_csv('mars_data.csv')

    print(f"Saved {len(df)} products to mars_data.csv")
    print(f"Columns: {list(df.columns)}")


Intermediate Recipes
====================

These recipes combine multiple filters and show you how to work with results more effectively.

Recipe 6: Find Mission-Specific Data in a Date Range
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


Recipe 7: Find Data and Get DOI for Citation
---------------------------------------------

**Goal:** Find data products and get their DOI for proper citation in papers.

.. code-block:: python

    import pds.peppi as pep

    client = pep.PDSRegistryClient()

    # Search for Bennu data from OSIRIS-REx
    products = pep.Products(client) \
        .has_target("Bennu") \
        .bundles()

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



Recipe 8: Extract Specific Metadata Fields Only
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


Recipe 9: Work with OSIRIS-REx Specialized Products
-----------------------------------------------------

**Goal:** Use mission-specific product classes for specialized functionality.

This recipe shows how to leverage specialized product classes like ``OrexProducts`` that
provide mission-specific features while inheriting standard Peppi filters.

.. code-block:: python

    import pds.peppi as pep

    client = pep.PDSRegistryClient()
    orex_products = pep.OrexProducts(client)

    # Use standard filters with mission-specific class
    products = orex_products.has_target("Bennu") \
        .within_range(100.0)   \
        .within_bbox(9.0, 15.0, 21.0, 27.0)  \
        .observationals()  \

    for i, product in enumerate(products):
        print(product.properties.get('pds:Identification_Area.pds:title', ['N/A'])[0])
        if i >= 4:
            break


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
