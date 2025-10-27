===============
Getting Started
===============

Welcome to Peppi! This guide will help you get started searching and accessing planetary data from NASA's Planetary Data System (PDS), even if you're new to Python.

What is Peppi?
==============

Peppi is a Python library that makes it easy to search and download planetary science data from NASA's Planetary Data System. Think of it as a search engine for planetary data - but instead of clicking through web pages, you write simple Python code to find exactly what you need.

No matter if you're looking for:

- Images from Mars rovers
- Spectral data from asteroids
- Atmospheric measurements from Venus
- Surface maps of the Moon
- ...or any other planetary data

Peppi helps you find and access it programmatically.

Prerequisites
=============

Before you begin, you'll need:

1. **Python 3.13 or newer** installed on your computer

   - Check if you have Python: Open a terminal/command prompt and type ``python --version`` or ``python3 --version``
   - If you need to install Python, visit https://www.python.org/downloads/

2. **Basic comfort with the command line** (terminal on Mac/Linux, Command Prompt or PowerShell on Windows)

3. **A text editor or Python environment** like:

   - VS Code (beginner-friendly)
   - Jupyter Notebook/Lab (great for data exploration)
   - PyCharm (full-featured IDE)
   - Or even a simple text editor

Installation
============

Open your terminal and install Peppi using pip:

.. code-block:: bash

    pip install pds.peppi

.. note::
   If you're using a virtual environment (recommended!), make sure to activate it first.

Your First Search
=================

Let's start with a simple example: finding data about Mars.

Step 1: Import Peppi
--------------------

Create a new Python file (e.g., ``my_first_search.py``) or open a Jupyter notebook, and add:

.. code-block:: python

    import pds.peppi as pep

This imports the Peppi library and gives it a short nickname (``pep``) so we don't have to type as much.

Step 2: Connect to the PDS
---------------------------

Next, create a connection to the PDS API:

.. code-block:: python

    client = pep.PDSRegistryClient()

This connects to NASA's public PDS server. You don't need any credentials or API keys - it's free and open to everyone!

Step 3: Find Products About Mars
---------------------------------

Now let's search for observational data (like images, spectra, or measurements) about Mars:

.. code-block:: python

    # Search for observational products targeting Mars
    products = pep.Products(client).has_target("Mars").observationals()

Let's break this down:

- ``pep.Products(client)`` - This creates a search query
- ``.has_target("Mars")`` - Filter for data about Mars
- ``.observationals()`` - Only return observational data (actual measurements, not documentation)

Step 4: Look at the Results
----------------------------

Now let's see what we found. We'll look at just the first 5 products:

.. code-block:: python

    # Print information about the first 5 products
    for i, product in enumerate(products):
        print(f"Product {i+1}:")
        print(f"  ID: {product.id}")
        print(f"  Title: {product.properties.get('pds:Identification_Area.pds:title', ['N/A'])[0]}")
        print()

        if i >= 4:  # Stop after 5 products
            break

When you run this, you'll see information about real Mars data in the PDS!

Complete First Example
=======================

Here's the complete code all together:

.. code-block:: python

    import pds.peppi as pep

    # Connect to PDS
    client = pep.PDSRegistryClient()

    # Search for Mars observational data
    products = pep.Products(client).has_target("Mars").observationals()

    # Print information about the first 5 products
    for i, product in enumerate(products):
        print(f"Product {i+1}:")
        print(f"  ID: {product.id}")
        print(f"  Title: {product.properties.get('pds:Identification_Area.pds:title', ['N/A'])[0]}")
        print()

        if i >= 4:  # Stop after 5 products
            break

Understanding What You Got
===========================

Each ``product`` in your results contains metadata (information about the data):

- **product.id** - A unique identifier for this product
- **product.properties** - A dictionary containing all the metadata fields
- **product.type** - What kind of product it is (observational, collection, bundle, etc.)

The metadata tells you things like:

- What mission collected the data
- When it was collected
- What instrument was used
- How to cite the data
- Where to download the actual data files

Next Steps
==========

Now that you've run your first search, you're ready to:

1. **Explore different targets** - Try searching for "Jupiter", "Moon", or "Bennu"
2. **Add more filters** - Learn about time ranges, instruments, and processing levels
3. **Work with results** - Export to pandas DataFrames, download data files, etc.

Check out these sections next:

- :doc:`user_guide` - Understand key concepts and how Peppi works
- :doc:`cookbook` - Copy and customize recipes for common tasks
- :doc:`reference` - Complete API documentation

Getting Help
============

If you get stuck:

1. **Read the error message** - Python errors often tell you exactly what's wrong
2. **Check the cookbook** - :doc:`cookbook` has solutions to common tasks
3. **Ask for help**:

   - Create a `GitHub issue <https://github.com/NASA-PDS/peppi/issues>`_
   - Start a `discussion <https://github.com/NASA-PDS/peppi/discussions>`_
   - Contact the `PDS Help Desk <mailto:pds-operator@jpl.nasa.gov>`_

Common Installation Issues
===========================

**"pip: command not found"**
    Try ``pip3`` instead of ``pip``, or install pip: ``python3 -m ensurepip``

**"No module named 'pds.peppi'"**
    Make sure you installed it: ``pip install pds.peppi``

    If using a virtual environment, make sure it's activated.

**"ImportError: No module named 'pandas'" or similar**
    Peppi has dependencies that should install automatically. Try: ``pip install --upgrade pds.peppi``

**Using Python 3.12 or earlier?**
    Peppi requires Python 3.13+. Consider using `pyenv <https://github.com/pyenv/pyenv>`_ or `conda <https://docs.conda.io/>`_ to manage multiple Python versions.
