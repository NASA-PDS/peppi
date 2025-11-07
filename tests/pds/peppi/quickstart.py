from datetime import datetime

import pds.peppi as pep

# Get the connection to the PDS Web API (and the underlying Registry)
client = pep.PDSRegistryClient()

# Find your data, observation data of mercury before 2012-01-23:
# find alternate filter methods in the `reference </reference.html#pds.peppi.query_builder.QueryBuilder>`_
date1 = datetime.fromisoformat("2012-01-23")

# find instrument host Messenger
context = pep.Context()
messenger = context.INSTRUMENT_HOSTS.search("messenger")[0]

# filter here:
products = pep.Products(client).has_target("Mercury").has_instrument_host(messenger.lid).before(date1).observationals()


# Iterate on the results:
for i, p in enumerate(products):
    print(p.id, p.investigations)
    # there a lot of there data, break after a couple of hundreds
    if i > 200:
        break


pep.Context().TARGETS
