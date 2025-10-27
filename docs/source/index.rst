PDS Peppi
=========

The **Peppi Open-Source Python Library** provides an intuitive interface for the research community to query and extract data from the `Planetary Data System (PDS) <https://pds.nasa.gov>`_.

Peppi is powered by the robust `PDS web API <https://nasa-pds.github.io/pds-api/>`_, which offers consistent access to data products from the Planetary Archive of NASA and other participating agencies. These products are described using the comprehensive `PDS4 standard <https://pds.nasa.gov/datastandards/about/>`_.

Whether you're a planetary scientist searching for mission data, a student learning about the solar system, or a researcher building data analysis pipelines, Peppi makes it easy to find and access the data you need.

Quick Example
=============

Here's a simple example to get you started:

.. code-block:: python

    import pds.peppi as pep

    # Connect to PDS
    client = pep.PDSRegistryClient()

    # Search for Mars data from Curiosity rover
    context = pep.Context()
    curiosity = context.INSTRUMENT_HOSTS.search("curiosity")[0]

    products = pep.Products(client) \
        .has_target("Mars") \
        .has_instrument_host(curiosity.lid) \
        .observationals()

    # View first 5 results
    for i, product in enumerate(products):
        print(product.id)
        if i >= 4:
            break

Key Features
============

- **Simple Search**: Use plain language to search for planetary data by target, mission, instrument, time range, and more
- **Fuzzy Matching**: Typo-tolerant search helps you find what you need even with imperfect queries
- **Pandas Integration**: Easily convert results to DataFrames for analysis
- **Automatic Pagination**: Seamlessly handles large result sets across multiple API pages
- **Context Discovery**: Browse available targets, missions, and instruments
- **Flexible Filtering**: Combine multiple criteria to find exactly what you need

Who is Peppi For?
=================

**Scientists and Researchers**
    Programmatically access PDS data for analysis, build data pipelines, create reproducible research workflows

**Students and Educators**
    Explore planetary data for projects, assignments, and learning about the solar system

**Data Engineers**
    Build applications and tools that integrate PDS data, create data catalogs and discovery systems

**Citizen Scientists**
    Access the same data used by professional researchers for personal projects and exploration

Documentation Structure
========================

Choose your path based on your experience and needs:

**New to Peppi?**
    Start with :doc:`getting_started` for a gentle introduction and your first search

**Want practical examples?**
    Jump to the :doc:`cookbook` for ready-to-use recipes you can copy and customize

**Need to understand concepts?**
    Read the :doc:`user_guide` to learn how Peppi works and how to use it effectively

**Looking for specific methods?**
    Check the :doc:`reference` for complete API documentation

Installation
============

Install Peppi using pip:

.. code-block:: bash

    pip install pds.peppi

Requires Python 3.13 or newer.

Table of Contents
=================

..  toctree::
    :maxdepth: 2
    :caption: Documentation

    getting_started
    user_guide
    cookbook
    reference

..  toctree::
    :maxdepth: 1
    :caption: Community & Support

    quickstart
    support/contribute
    support/contact

Additional Resources
====================

- `PDS Search API Documentation <https://nasa-pds.github.io/pds-api/>`_ - Understanding the underlying API
- `Search API Notebooks <https://github.com/NASA-PDS/search-api-notebook>`_ - Jupyter notebook examples
- `PDS Portal <https://pds.nasa.gov/>`_ - Browse data through the web interface
- `PDS4 Standard <https://pds.nasa.gov/datastandards/about/>`_ - Learn about PDS data standards

Contributing
============

Recognizing the vast and unpredictable range of scientific use cases, and the rich complexity of the PDS4 standard, Peppi is an evolving project. We invite you to :doc:`support/contribute` to its development and help shape its future.

- Report bugs or request features: `GitHub Issues <https://github.com/NASA-PDS/peppi/issues>`_
- Discuss ideas and ask questions: `GitHub Discussions <https://github.com/NASA-PDS/peppi/discussions>`_
- Contribute code: See our :doc:`support/contribute` guide

.. _API: https://nasa-pds.github.io/pds-api/
.. _PDS: https://pds.nasa.gov/
.. _PDS4: https://pds.nasa.gov/datastandards/about/
