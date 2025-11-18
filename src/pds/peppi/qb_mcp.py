# encoding: utf-8
"""Model Context Protocol (MCP) server for natural language PDS queries using the Peppi QueryBuilder."""
import logging
import re
from datetime import datetime
from typing import Any

import pds.peppi as pep
from fastmcp import FastMCP

logger = logging.getLogger(__name__)


def query_pds_data(query: str, max_results: int = 50) -> dict[str, Any]:
    """Query PDS data using natural language.

    This tool allows you to query the Planetary Data System (PDS) using natural language.
    Translate the user's natural language query into appropriate QueryBuilder method calls.

    QueryBuilder Methods Available:
    ===============================

    Target Filtering:
    - has_target(target: str) - Filter by planetary body (e.g., "Mars", "Jupiter", "Moon", "Bennu", "Enceladus", "Venus", "Mercury")
      Example: .has_target("Mars")

    Mission/Spacecraft Filtering:
    - has_instrument_host(identifier: str) - Filter by spacecraft/mission (requires LID from Context search)
      Example: .has_instrument_host("urn:nasa:pds:context:instrument_host:spacecraft.msl")
      Use context.INSTRUMENT_HOSTS.search("curiosity") to find LIDs

    Instrument Filtering:
    - has_instrument(identifier: str) - Filter by instrument (requires LID)
      Example: .has_instrument("urn:nasa:pds:context:instrument:...")

    Investigation Filtering:
    - has_investigation(identifier: str) - Filter by investigation/mission
      Example: .has_investigation("urn:nasa:pds:context:investigation:mission.orex")

    Date Filtering:
    - after(dt: datetime) - Products with start date after given datetime
      Example: .after(datetime(2020, 1, 1))
    - before(dt: datetime) - Products with start date before given datetime
      Example: .before(datetime(2020, 12, 31))

    Product Type Filtering:
    - observationals() - Only observational products (actual data)
      Example: .observationals()
    - collections(collection_type: Optional[str] = None) - Only collection products
      Example: .collections() or .collections("Data")
    - bundles() - Only bundle products
      Example: .bundles()

    Processing Level Filtering:
    - has_processing_level(processing_level: str) - Filter by processing level
      Valid values: "telemetry", "raw", "partially-processed", "calibrated", "derived"
      Example: .has_processing_level("calibrated")

    Collection Filtering:
    - of_collection(identifier: str) - Products belonging to a specific collection
      Example: .of_collection("urn:nasa:pds:orex.bennu.regolith:...")

    Product Lookup:
    - get(identifier: str) - Get specific product by LIDVID
      Example: .get("urn:nasa:pds:orex.bennu.regolith::1.0")

    Field Selection:
    - fields(fields: list[str]) - Limit returned fields for efficiency
      Example: .fields(['lid', 'pds:Identification_Area.pds:title', 'pds:Time_Coordinates.pds:start_date_time'])

    Custom Filtering:
    - filter(clause: str) - Add custom PDS API query clause
      Example: .filter('product_class eq "Product_Observational"')

    Result Methods:
    - as_dataframe(max_rows: Optional[int] = None) - Convert results to pandas DataFrame
    - Iterate directly: for product in products: ...

    Common Query Patterns:
    ======================

    1. Find all data about a target:
       pep.Products(client).has_target("Mars").observationals()

    2. Find data from a specific mission:
       context = pep.Context()
       curiosity = context.INSTRUMENT_HOSTS.search("curiosity")[0]
       pep.Products(client).has_instrument_host(curiosity.lid).observationals()

    3. Find data in a date range:
       pep.Products(client).has_target("Mercury").after(datetime(2020, 1, 1)).before(datetime(2020, 12, 31)).observationals()

    4. Find calibrated data:
       pep.Products(client).has_target("Mars").has_processing_level("calibrated").observationals()

    5. Find collections:
       pep.Products(client).has_target("Mars").collections()

    6. Find bundles:
       pep.Products(client).has_target("Bennu").bundles()

    7. Complex query (mission + target + date):
       context = pep.Context()
       messenger = context.INSTRUMENT_HOSTS.search("messenger")[0]
       pep.Products(client).has_target("Mercury").has_instrument_host(messenger.lid).before(datetime(2012, 1, 23)).observationals()

    Translation Guidelines:
    ======================

    When translating natural language to QueryBuilder calls:

    1. Identify the target (planet/moon/asteroid) - use has_target()
    2. Identify mission/spacecraft - use Context to search, then has_instrument_host()
    3. Identify date ranges - use after() and before() with datetime objects
    4. Identify product type - use observationals(), collections(), or bundles()
    5. Identify processing level - use has_processing_level()
    6. Chain methods together - methods return self, so you can chain them

    Example translations:
    - "Find Mars data" → .has_target("Mars").observationals()
    - "Find calibrated Mars data" → .has_target("Mars").has_processing_level("calibrated").observationals()
    - "Find Curiosity rover data" → Search for "curiosity" in INSTRUMENT_HOSTS, then .has_instrument_host(lid).observationals()
    - "Find Mercury data from 2020" → .has_target("Mercury").after(datetime(2020, 1, 1))
        .before(datetime(2020, 12, 31)).observationals()
    - "Find Mars collections" → .has_target("Mars").collections()

    Parameters
    ----------
    query : str
        Natural language query describing what PDS data to find. Examples include "Find all Mars observational data",
        "Find calibrated data from Jupiter", "Find data from the Curiosity rover", "Find Mercury data from 2020",
        "Find Mars collections", and "Find Bennu bundles".
    max_results : int, optional
        Maximum number of results to return. Default is 50.

    Returns
    -------
    dict
        Dictionary containing:
        - "query": The natural language query that was processed
        - "query_builder_calls": Description of QueryBuilder methods used
        - "count": Number of results found
        - "results": List of products, each containing:
          - "id": Product LIDVID
          - "title": Product title
          - "start_date": Start date if available
          - "target": Target if available
          - "processing_level": Processing level if available
          - "product_class": Product class type
          - "properties": Full product properties dictionary
    """
    try:
        # Initialize client and context
        try:
            client = pep.PDSRegistryClient()
        except Exception as e:
            logger.error("Failed to initialize PDS client: %s", e)
            return {
                "query": query,
                "error": f"Failed to connect to PDS API: {str(e)}",
                "count": 0,
                "results": [],
            }

        try:
            context = pep.Context()
        except Exception as e:
            logger.warning("Failed to initialize Context (continuing without mission search: %s", e)
            context = None

        products = pep.Products(client)

        # Parse the natural language query and build QueryBuilder chain
        query_lower = query.lower()
        query_builder_calls = []

        # Check for target mentions
        targets = [
            "mars", "jupiter", "moon", "bennu", "enceladus", "venus", "mercury", "earth", "saturn",
            "neptune", "uranus", "pluto", "ceres", "vesta", "eros", "ida"
        ]
        for target in targets:
            if target in query_lower:
                try:
                    products = products.has_target(target.capitalize())
                    query_builder_calls.append(f"has_target('{target.capitalize()}')")
                    break
                except Exception as e:
                    logger.warning("Error adding target filter for %s: %s", target, e)
                    # Continue without this filter

        # Check for mission/spacecraft mentions
        if context is not None:
            # May not need this mapping since the key and name are identical for most missions
            missions = {
                "curiosity": "curiosity",
                "perseverance": "perseverance",
                "juno": "juno",
                "cassini": "cassini",
                "messenger": "messenger",
                "new horizons": "new horizons",
                "osiris-rex": "osiris-rex",
                "orex": "osiris-rex",
                "maven": "maven",
                "insight": "insight",
            }
            for mission_key, mission_name in missions.items():
                if mission_key in query_lower:
                    try:
                        instrument_hosts = context.INSTRUMENT_HOSTS.search(mission_name)
                        if instrument_hosts:
                            lid = instrument_hosts[0].lid
                            products = products.has_instrument_host(lid)
                            query_builder_calls.append(f"has_instrument_host('{lid}')")
                        else:
                            logger.warning("No instrument host found for %s", mission_name)
                    except Exception as e:
                        logger.warning("Could not find instrument host for %s: %s", mission_name, e)
                    break

        # Check for date mentions (simple patterns)
        # Look for year patterns like "2020", "from 2020", "in 2020"
        try:
            full_years = re.findall(r'\b(19|20)\d{2}\b', query)
            if full_years:
                # Extract first 4-digit year found
                year_match = re.search(r'\b(19|20)\d{2}\b', query)
                if year_match:
                    year_str = year_match.group(0)
                    year = int(year_str)

                    # Validate year range
                    if 1900 <= year <= 2100:
                        # Use the year for date filtering
                        products = products.after(datetime(year, 1, 1))
                        products = products.before(datetime(year, 12, 31))
                        query_builder_calls.append(f"after(datetime({year}, 1, 1))")
                        query_builder_calls.append(f"before(datetime({year}, 12, 31))")
        except Exception as e:
            logger.warning("Error parsing date from query: %s", e)

        # Check for processing level
        try:
            if "calibrated" in query_lower:
                products = products.has_processing_level("calibrated")
                query_builder_calls.append("has_processing_level('calibrated')")
            elif "raw" in query_lower:
                products = products.has_processing_level("raw")
                query_builder_calls.append("has_processing_level('raw')")
            elif "derived" in query_lower:
                products = products.has_processing_level("derived")
                query_builder_calls.append("has_processing_level('derived')")
        except Exception as e:
            logger.warning("Error adding processing level filter: %s", e)

        # Check for product type
        try:
            if "collection" in query_lower or "collections" in query_lower:
                products = products.collections()
                query_builder_calls.append("collections()")
            elif "bundle" in query_lower or "bundles" in query_lower:
                products = products.bundles()
                query_builder_calls.append("bundles()")
            else:
                # Default to observationals if not specified
                products = products.observationals()
                query_builder_calls.append("observationals()")
        except Exception as e:
            logger.warning("Error adding product type filter: %s", e)
            # Fallback to observationals
            try:
                products = products.observationals()
                query_builder_calls.append("observationals()")
            except Exception:
                pass

        # Execute query and collect results
        results = []
        count = 0
        query_error = None
        try:
            for product in products:
                if count >= max_results:
                    break

                try:
                    # Extract key properties safely
                    title_prop = product.properties.get("pds:Identification_Area.pds:title", [])
                    title = title_prop[0] if title_prop else "«N/A»"

                    start_date_prop = product.properties.get("pds:Time_Coordinates.pds:start_date_time", [])
                    start_date = start_date_prop[0] if start_date_prop else None

                    target_prop = product.properties.get("ref_lid_target", [])
                    target = target_prop[0] if target_prop else None

                    processing_level_prop = product.properties.get("pds:Primary_Result_Summary.pds:processing_level", [])
                    processing_level = processing_level_prop[0] if processing_level_prop else None

                    product_class_prop = product.properties.get("product_class", [])
                    product_class = product_class_prop[0] if product_class_prop else "«N/A»"

                    product_data = {
                        "id": product.id,
                        "title": title,
                        "start_date": start_date,
                        "target": target,
                        "processing_level": processing_level,
                        "product_class": product_class,
                    }

                    results.append(product_data)
                    count += 1
                except Exception as e:
                    logger.warning(
                        "Error processing product %s: %s",
                        product.id if hasattr(product, 'id') else '«unknown»', e
                    )
                    # Continue with next product
                    continue
        except Exception as e:
            query_error = str(e)
            logger.error("Error executing query iteration: %s", e, exc_info=True)
        finally:
            # Always reset query builder state, even if iteration fails
            try:
                products.reset()
            except Exception:
                pass

        response = {
            "query": query,
            "query_builder_calls": " → ".join(query_builder_calls) if query_builder_calls else "No filters applied",
            "count": count,
            "results": results,
        }

        if query_error:
            response["warning"] = f"Query executed but encountered errors: {query_error}"

        return response

    except Exception as e:
        logger.error("Error executing query: %s", e, exc_info=True)
        return {
            "query": query,
            "error": str(e),
            "count": 0,
            "results": [],
        }


def main():
    """Main entry point to launch the MCP server.

    This server exposes a natural language query tool for PDS data.
    The tool delegates query translation to the MCP client (Claude) by providing
    comprehensive documentation in the tool description.
    """
    mcp = FastMCP("Planetary Data System (PDS) Query Builder Model Context Protocol (MCP) Server")

    # Register the natural language query tool
    mcp.tool(query_pds_data)

    # Run the server with stdio transport
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
