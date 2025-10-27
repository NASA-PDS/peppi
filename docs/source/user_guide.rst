==========
User Guide
==========

This guide explains the key concepts and components of Peppi to help you understand how to effectively search and access PDS data.

Key Concepts
============

PDS Products
------------

The Planetary Data System organizes data into **products**. There are different types of products:

**Observational Products**
    The actual science data - images, spectra, measurements, etc. This is usually what you want.

**Collections**
    Groups of related products (e.g., all images from a particular Mars rover camera for a specific mission phase).

**Bundles**
    Groups of collections (e.g., all data from a complete mission).

**Context Products**
    Metadata describing targets (planets, moons), instruments, missions, and spacecraft. These help you search for the data you want.

Understanding PDS Identifiers
------------------------------

Every product in the PDS has a unique identifier called a **LID** (Logical Identifier). It looks like:

.. code-block:: text

    urn:nasa:pds:mission.instrument:collection:product

For example:

.. code-block:: text

    urn:nasa:pds:context:target:planet.mars

Some products also have versions, making them **LIDVIDs** (LID + Version ID):

.. code-block:: text

    urn:nasa:pds:mission.instrument:collection:product::1.0

You usually don't need to know the exact LID - Peppi lets you search by name (like "Mars") and it finds the LID for you.

Core Components
===============

PDSRegistryClient
-----------------

The **PDSRegistryClient** connects your Python code to the PDS API:

.. code-block:: python

    import pds.peppi as pep

    client = pep.PDSRegistryClient()

By default, it connects to NASA's production PDS server (``https://pds.nasa.gov/api/search/1``).

If you need to connect to a different server (e.g., for testing):

.. code-block:: python

    client = pep.PDSRegistryClient(base_url="https://pds.nasa.gov/api/search/1")

Products
--------

The **Products** class is your main tool for searching. It uses a "fluent" interface where you chain methods together:

.. code-block:: python

    products = pep.Products(client) \
        .has_target("Mars") \
        .has_instrument_host("urn:nasa:pds:context:instrument_host:spacecraft.msl") \
        .observationals()

Each method returns the Products object, so you can keep adding filters.

Context
-------

The **Context** gives you access to searchable catalogs of targets and spacecraft:

.. code-block:: python

    context = pep.Context()

    # Search for a target (with fuzzy matching!)
    jupiter = context.TARGETS.search("jupiter")[0]
    print(jupiter.name)  # "Jupiter"
    print(jupiter.lid)   # "urn:nasa:pds:context:target:planet.jupiter"

    # Search for a spacecraft
    curiosity = context.INSTRUMENT_HOSTS.search("curiosity")[0]
    print(curiosity.name)  # "Mars Science Laboratory"

The search is typo-tolerant, so ``context.TARGETS.search("jupyter")`` will still find Jupiter!

Building Queries
================

The Query Builder Pattern
--------------------------

Peppi uses a "query builder" pattern. You start with ``Products(client)`` and add filters:

.. code-block:: python

    query = pep.Products(client)            # Start with all products
    query = query.has_target("Mars")        # Filter by target
    query = query.observationals()          # Filter by product type

    # Now execute by iterating
    for product in query:
        print(product.id)

Or chain it all together:

.. code-block:: python

    products = pep.Products(client).has_target("Mars").observationals()

Lazy Evaluation
---------------

**Important:** Queries don't execute until you iterate over the results or convert to a DataFrame.

This means you can build up complex queries step by step:

.. code-block:: python

    # No API call happens yet
    query = pep.Products(client).has_target("Mars")

    # Still no API call
    query = query.observationals()

    # NOW the API is called, as we start iterating
    for product in query:
        print(product.id)

Automatic Pagination
--------------------

When searching, the PDS API returns results in pages (typically 100 at a time). Peppi automatically handles this for you:

.. code-block:: python

    products = pep.Products(client).has_target("Mars").observationals()

    # This will automatically fetch multiple pages as needed
    for product in products:
        print(product.id)

You don't need to worry about pagination - just iterate and Peppi handles the rest!

Available Filters
=================

Here are the main filtering methods you can use:

By Target
---------

Filter by celestial body (planet, moon, asteroid, comet):

.. code-block:: python

    # By name (Peppi finds the LID for you)
    .has_target("Mars")

    # Or by LID if you know it
    .has_target("urn:nasa:pds:context:target:planet.mars")

By Time
-------

Filter by when data was collected:

.. code-block:: python

    from datetime import datetime

    date1 = datetime(2020, 1, 1)
    date2 = datetime(2020, 12, 31)

    # Data collected before a date
    .before(date1)

    # Data collected after a date
    .after(date1)

    # Combine for a range
    .after(date1).before(date2)

By Mission/Spacecraft
---------------------

Filter by instrument host (spacecraft or rover):

.. code-block:: python

    # By LID
    .has_instrument_host("urn:nasa:pds:context:instrument_host:spacecraft.msl")

    # Or find it with Context
    context = pep.Context()
    curiosity = context.INSTRUMENT_HOSTS.search("curiosity")[0]
    products.has_instrument_host(curiosity.lid)

By Instrument
-------------

Filter by the specific instrument that collected the data:

.. code-block:: python

    .has_instrument("urn:nasa:pds:context:instrument:instrument_lid")

By Investigation
----------------

Filter by mission or investigation:

.. code-block:: python

    .has_investigation("urn:nasa:pds:context:investigation:mission.msl")

By Collection
-------------

Get products from a specific collection:

.. code-block:: python

    .of_collection("urn:nasa:pds:mission.instrument:collection::1.0")

By Processing Level
-------------------

Filter by how processed the data is:

.. code-block:: python

    # Available levels: "telemetry", "raw", "partially-processed", "calibrated", "derived"
    .has_processing_level("calibrated")

**Processing levels explained:**

- **telemetry**: Raw transmission from spacecraft
- **raw**: Unprocessed instrument data
- **partially-processed**: Some processing applied
- **calibrated**: Converted to physical units with corrections applied
- **derived**: Higher-level products created from processed data

By Product Type
---------------

Filter by the class of product:

.. code-block:: python

    .observationals()           # Actual science data
    .collections()              # Collection products
    .bundles()                  # Bundle products
    .contexts()                 # Context products (targets, instruments, etc.)

    # For collections, you can specify the type
    .collections(collection_type="data")

Custom Filters
--------------

For advanced use cases, you can write custom query clauses using the PDS API syntax:

.. code-block:: python

    # Filter by any PDS4 property
    .filter('pds:Identification_Area.pds:title like "*Mars*"')

See the `PDS API documentation <https://nasa-pds.github.io/pds-api/>`_ for the query syntax.

Working with Results
====================

Iterating Over Products
-----------------------

The simplest way to work with results:

.. code-block:: python

    products = pep.Products(client).has_target("Mars").observationals()

    for product in products:
        print(product.id)
        print(product.properties)  # Dictionary of all metadata
        break  # Remove this to see all results

Limiting Results
----------------

To avoid iterating over thousands of products while testing:

.. code-block:: python

    for i, product in enumerate(products):
        print(product.id)

        if i >= 9:  # Stop after 10 products
            break

Converting to DataFrame
-----------------------

For data analysis, convert results to a pandas DataFrame:

.. code-block:: python

    import pds.peppi as pep

    products = pep.Products(client).has_target("Mars").observationals()

    # Convert to DataFrame (automatically handles all pages)
    df = products.as_dataframe()

    print(df.head())
    print(df.columns)

    # Limit rows for testing
    df = products.as_dataframe(max_rows=100)

Accessing Metadata
------------------

Each product has a ``properties`` dictionary containing all PDS4 metadata:

.. code-block:: python

    for product in products:
        # Access specific properties
        title = product.properties.get('pds:Identification_Area.pds:title', ['N/A'])[0]
        start_time = product.properties.get('pds:Time_Coordinates.pds:start_date_time', ['N/A'])[0]

        print(f"Title: {title}")
        print(f"Start Time: {start_time}")
        break

.. note::
   Most properties are returned as lists (even single values) for consistency. Use ``[0]`` to get the first value.

Reducing Returned Fields
-------------------------

For better performance, especially with large result sets, you can limit which fields are returned:

.. code-block:: python

    products = pep.Products(client) \
        .has_target("Mars") \
        .observationals() \
        .fields(['lid', 'title', 'pds:Time_Coordinates.pds:start_date_time'])

    # Now products will only include the specified fields

Resetting a Query
-----------------

If you're iterating and want to start over or build a new query:

.. code-block:: python

    products = pep.Products(client).has_target("Mars").observationals()

    # Iterate through some results
    for i, product in enumerate(products):
        if i >= 10:
            break

    # Reset to use the same query again
    products.reset()

    # Or build a new query
    products = pep.Products(client).has_target("Jupiter").observationals()

Combining Filters
=================

You can combine multiple filters to narrow your search:

.. code-block:: python

    from datetime import datetime
    import pds.peppi as pep

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

    df = products.as_dataframe(max_rows=10)
    print(df)

Understanding Data Organization
================================

PDS data is organized hierarchically:

.. code-block:: text

    Bundle (e.g., entire mission)
    └── Collection (e.g., one instrument's data)
        └── Observational Products (e.g., individual images)

When you search for observational products, you're searching at the most detailed level.

To understand what collection or bundle a product belongs to, look at its properties:

.. code-block:: python

    product.properties.get('ops:Provenance.ops:parent_collection_identifier')
    product.properties.get('ops:Provenance.ops:parent_bundle_identifier')

Tips and Best Practices
========================

Start Broad, Then Narrow
-------------------------

When exploring new data:

1. Start with a broad search to see what's available
2. Look at the results to understand the data structure
3. Add more specific filters based on what you learned

.. code-block:: python

    # Start broad
    products = pep.Products(client).has_target("Mars").observationals()

    # Look at first few results
    for i, p in enumerate(products):
        print(p.properties.keys())  # See what metadata is available
        if i >= 2:
            break

    # Now refine based on what you learned
    products.reset()
    products = pep.Products(client) \
        .has_target("Mars") \
        .has_processing_level("calibrated") \
        .after(datetime(2020, 1, 1)) \
        .observationals()

Use Context for Discovery
--------------------------

Don't know the exact name of a target or spacecraft? Use Context:

.. code-block:: python

    context = pep.Context()

    # See all available targets (returns top 10 matches)
    mars_related = context.TARGETS.search("mars")
    for target in mars_related:
        print(f"{target.name}: {target.lid}")

    # Find spacecraft (handles typos!)
    spacecraft = context.INSTRUMENT_HOSTS.search("curiousity")  # Typo on purpose!
    print(spacecraft[0].name)  # Still finds "Mars Science Laboratory"

Test with Small Result Sets
----------------------------

Always test with limited results before processing large datasets:

.. code-block:: python

    # Use max_rows when creating DataFrames
    df = products.as_dataframe(max_rows=10)

    # Or break out of loops early
    for i, product in enumerate(products):
        # Your processing here
        if i >= 9:
            break

Common PDS Metadata Fields
===========================

Here are some commonly used metadata fields:

.. code-block:: python

    # Identification
    'lid'                                          # Product identifier
    'title'                                        # Human-readable title
    'pds:Identification_Area.pds:title'           # Full title
    'pds:Identification_Area.pds:logical_identifier'  # LID

    # Time
    'pds:Time_Coordinates.pds:start_date_time'    # When observation started
    'pds:Time_Coordinates.pds:stop_date_time'     # When observation ended

    # References
    'ref_lid_target'                              # Target (planet, moon, etc.)
    'ref_lid_instrument'                          # Instrument used
    'ref_lid_instrument_host'                     # Spacecraft/rover
    'ref_lid_investigation'                       # Mission/investigation

    # Processing
    'pds:Primary_Result_Summary.pds:processing_level'  # Processing level

    # Provenance
    'ops:Provenance.ops:parent_collection_identifier'  # Parent collection
    'ops:Provenance.ops:parent_bundle_identifier'      # Parent bundle

    # Citation
    'pds:Citation_Information.pds:doi'            # DOI for citing

Next Steps
==========

Now that you understand the key concepts, check out:

- :doc:`cookbook` - Ready-to-use recipes for common tasks
- :doc:`reference` - Complete API documentation
- `PDS Search API Documentation <https://nasa-pds.github.io/pds-api/>`_ - Understanding the underlying API
