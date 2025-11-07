============
 Quickstart
============

.. note::
   This page provides a quick reference example. For a more detailed introduction,
   see :doc:`getting_started`. For more examples, see the :doc:`cookbook`.

Peppi is meant to be simple to start with. It brings you to the core of your research in a few lines of code.

The following code has been tested with **Python 3.13**.



Try it
~~~~~~~


Install:

.. code-block:: bash

    pip install pds.peppi


The following lines of code can be found in this `file <https://github.com/NASA-PDS/peppi/tree/main/tests/pds/peppi/quickstart.py>`_

Import:

.. code-block:: python

    from datetime import datetime
    import pds.peppi as pep


Get the connection to the PDS Web API (and the underlying Registry):

.. code-block:: python

    client = pep.PDSRegistryClient()

Find your data, observation data of mercury before 2012-01-23:
Alternate filter methods can be found in the :doc:`reference`

.. code-block:: python

    date1 = datetime.fromisoformat("2012-01-23")
    # mercury identifier in PDS, find it, in the type "target"
    # in the `PDS keyword search <https://pds.nasa.gov/datasearch/keyword-search/search.jsp>`_
    mercury_id = "urn:nasa:pds:context:target:planet.mercury"
    # filter here:
    products = pep.Products(client).has_target(mercury_id).before(date1).observationals()


You can even simplify the last line, selecting the target from its name, as follows:

.. code-block:: python

    products = pep.Products(client).has_target("mercury").before(date1).observationals()


Then iterate on the results:

.. code-block:: python

    for i, p in enumerate(products):
        print(p.id, p.investigations)
        # there a lot of data there, break after a couple of hundreds
        if i > 200:
            break


Numerous pre-defined filters are available, you can `explore them <https://nasa-pds.github.io/peppi/reference.html#pds.peppi.query_builder.QueryBuilder>`_.


Next Steps
~~~~~~~~~~~

Now that you've seen a quick example, explore the documentation:

- **New to Python or Peppi?** Start with :doc:`getting_started` for a gentle introduction
- **Want more examples?** Check out the :doc:`cookbook` with 20+ ready-to-use recipes
- **Need to understand concepts?** Read the :doc:`user_guide` for comprehensive explanations
- **Looking for API details?** See the full :doc:`reference`

Additional Resources
~~~~~~~~~~~~~~~~~~~~

- `Search API Jupyter Notebooks <https://github.com/NASA-PDS/search-api-notebook>`_ - Real-world examples
- `PDS Search API Docs <https://nasa-pds.github.io/pds-api/>`_ - Underlying API documentation
- Missing a feature? Request it via `GitHub Issues <https://github.com/nasa-pds/peppi/issues>`_
- Have questions? Start a `discussion <https://github.com/NASA-PDS/peppi/discussions>`_
