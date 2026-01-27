# encoding: utf-8
"""Model Context Protocol (MCP) server for natural language PDS queries using the Peppi QueryBuilder."""
import inspect
import logging
import re
from datetime import datetime
from typing import Any
from typing import get_args

import pds.peppi as pep
from fastmcp import FastMCP
from pds.peppi.query_builder import PROCESSING_LEVELS
from pds.peppi.query_builder import QueryBuilder

logger = logging.getLogger(__name__)

# Common targets for searches that include search terms like "find Mars data"
_targets = [
    "mars", "jupiter", "moon", "bennu", "enceladus", "venus", "mercury", "earth", "saturn",
    "neptune", "uranus", "pluto", "ceres", "vesta", "eros", "ida"
]

# Mission names. This may not be needed since they identical for all missions right now, but
# it's here for future use if there's ever any need.
_missions = {
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

# Category configuration: organizes specific QueryBuilder methods into logical groups with
# descriptions for the LLM to better understand method usage. Methods listed here appear
# under their category headings in the generated documentation. Methods not included here
# are STILL CAPTURED automatically and appear in an "Other Methods" section, but can be
# added to this dictionary to provide better categorization and context for the LLM.
_categories: dict[str, dict[str, object]] = {
    "Target Filtering": {
        "methods": ["has_target"],
        "description": "Filter by planetary body, moon, or asteroid",
    },
    "Mission/Spacecraft Filtering": {
        "methods": ["has_instrument_host"],
        "description": "Filter by spacecraft/mission (requires LID from Context search)",
    },
    "Instrument Filtering": {
        "methods": ["has_instrument"],
        "description": "Filter by instrument (requires LID)",
    },
    "Investigation Filtering": {
        "methods": ["has_investigation"],
        "description": "Filter by investigation/mission",
    },
    "Date Filtering": {
        "methods": ["after", "before"],
        "description": "Filter by date/time ranges",
    },
    "Product Type Filtering": {
        "methods": ["observationals", "collections", "bundles", "contexts"],
        "description": "Filter by product class type",
    },
    "Processing Level Filtering": {
        "methods": ["has_processing_level"],
        "description": "Filter by processing level",
    },
    "Collection Filtering": {
        "methods": ["of_collection"],
        "description": "Filter by parent collection",
    },
    "Spatial Filtering": {
        "methods": ["within_range", "within_bbox"],
        "description": "Filter by spatial constraints (product-specific)",
    },
    "Product Lookup": {
        "methods": ["get"],
        "description": "Get specific product by identifier",
    },
    "Field Selection": {
        "methods": ["fields"],
        "description": "Limit returned fields for efficiency",
    },
    "Custom Filtering": {
        "methods": ["filter"],
        "description": "Add custom PDS API query clause",
    },
    "Result Methods": {
        "methods": ["as_dataframe", "reset"],
        "description": "Convert results or reset query state",
    },
}


def _generatequerybuilderdocumentation() -> str:
    """Dynamically generate documentation for QueryBuilder methods using introspection.

    The goal is to create a full docstring for the LLM to use to understand the QueryBuilder methods,
    and to automatically generate that the QueryBuilder class changes.

    The "_categories" dictionary can be used to fine-tune the documentation per-method if necessary.

    • Uses `inspect.getmembers(…, predicate=inspect.isfunction)` for reliable method discovery.
    • Documents configured categories first, then adds an "Other Methods" section for any
      newly added public methods not explicitly categorized; this can be fine-tuned as needed.
    • Produces compact, LLM-friendly signatures and examples.
    """
    def _formatannotation(ann: object) -> str:
        """Best-effort, human/LLM-friendly annotation formatting."""
        if ann is inspect._empty:
            return ""

        # typing constructs often stringify as "typing.X[…]"; remove prefix
        s = str(ann).replace("typing.", "")

        # Clean common Python 3.10+ union formatting like "X | None"
        s = s.replace("NoneType", "None")

        # Make Optional[…] more readable if it appears in string form
        # (Don't aggressively strip brackets; just a light normalization)
        s = s.replace("Optional[", "").rstrip("]") if s.startswith("Optional[") else s

        # C'est tout pour maintenant
        return s

    def _formatdefault(val: object) -> str:
        """Readable default values (quote strings)."""
        if val is inspect._empty:
            return ""
        if isinstance(val, str):
            return f' = "{val}"'
        return f" = {repr(val)}"

    def _methodsignaturestr(name: str, fn: object) -> str:
        """Return `name(param: Type = default, …)`."""
        try:
            sig = inspect.signature(fn)
        except (TypeError, ValueError):
            return f"{name}(...)"  # Note: do not use ellipsis here as LLMs are trained to recognize three periods

        parts: list[str] = []
        for p in sig.parameters.values():
            if p.name == "self":
                continue

            piece, ann = p.name, _formatannotation(p.annotation)
            if ann:
                piece += f": {ann}"
            piece += _formatdefault(p.default)

            # Keep *args/**kwargs readable
            if p.kind == inspect.Parameter.VAR_POSITIONAL:
                piece = "*" + piece
            elif p.kind == inspect.Parameter.VAR_KEYWORD:
                piece = "**" + piece
            parts.append(piece)
        return f"{name}({', '.join(parts)})"

    def _docsummary(fn: object) -> str:
        """Provide the first non-empty line of docstring, lightly cleaned for LLM use."""
        doc = inspect.getdoc(fn) or ""
        for line in doc.splitlines():
            s = line.strip()
            if s:
                # KISS principle (keep it short) and remove the trailing period
                return s[:-1] if s.endswith(".") else s
        return ""

    def _examplefor(name: str, fn: object) -> str:
        """Generate a simple chaining example.

        This adds `.method(…)` and related boilerplate to the example.
        """
        # Use signature to guess something sensible
        try:
            sig = inspect.signature(fn)
            params = [p for p in sig.parameters.values() if p.name != "self"]
        except (TypeError, ValueError):
            return f".{name}()"

        # No args
        if not params:
            return f".{name}()"

        # First parameter heuristics
        p0 = params[0]
        p0_name = p0.name.lower()
        p0_ann = str(p0.annotation).lower() if p0.annotation is not inspect._empty else ""

        # These provide useful examples to the LLM to help understand the parameters and possibilities
        if "target" in name.lower() or "target" in p0_name:
            return f'.{name}("Mars")'
        if "instrument_host" in name.lower():
            return f'.{name}("urn:nasa:pds:context:...")'  # See earlier note about ellipsis; also applies here
        if "instrument" in name.lower() and "host" not in name.lower():
            return f'.{name}("urn:nasa:pds:context:...")'  # And here, and below…
        if "investigation" in name.lower():
            return f'.{name}("urn:nasa:pds:context:...")'
        if "processing_level" in name.lower() or "processing" in p0_name:
            return f'.{name}("calibrated")'
        if "after" == name.lower() or "before" == name.lower() or "datetime" in p0_ann:
            return f".{name}(datetime(2020, 1, 1))"
        if "fields" in name.lower() or "fields" in p0_name:
            return f'.{name}(["lid", "pds:Identification_Area.pds:title"])'
        if "filter" == name.lower() or "clause" in p0_name:
            return f'.{name}(\'product_class eq "Product_Observational"\')'
        if "collection" in name.lower() or "collection" in p0_name:
            return f'.{name}("urn:nasa:pds:...")'
        if "bbox" in name.lower():
            return f".{name}((-5.0, -5.0, 5.0, 5.0))"
        if "range" in name.lower():
            return f".{name}(0.0, 10.0)"

        # Fallback based on likely primitive type
        if "int" in p0_ann or "max" in p0_name or "limit" in p0_name:
            return f".{name}(100)"
        if "float" in p0_ann:
            return f".{name}(1.0)"
        if "str" in p0_ann:
            return f'.{name}("...")'

        # Fallback to just the name if we can't guess anything better
        return f".{name}()"

    # Discover public methods reliably
    all_methods: dict[str, object] = {}
    for name, fn in inspect.getmembers(QueryBuilder, predicate=inspect.isfunction):
        if name.startswith("_"):
            continue
        all_methods[name] = fn

    lines: list[str] = []
    lines.append("QueryBuilder Methods Available:")
    lines.append("=" * 30)
    lines.append("")

    # Track which methods we have documented explicitly
    documented: set[str] = set()

    for category_name, info in _categories.items():
        method_names = [m for m in info.get("methods", []) if m in all_methods]
        if not method_names:
            continue

        base_desc = str(info.get("description", "")).strip()
        lines.append(f"{category_name}:")

        for method_name in method_names:
            fn = all_methods[method_name]
            documented.add(method_name)

            sig_str = _methodsignaturestr(method_name, fn)
            summary = _docsummary(fn)
            example = _examplefor(method_name, fn)

            desc = base_desc
            if method_name == "has_processing_level":
                # Include valid values if available
                try:
                    processing_levels = list(get_args(PROCESSING_LEVELS))
                except Exception:
                    processing_levels = ["telemetry", "raw", "partially-processed", "calibrated", "derived"]
                desc = f"Filter by processing level. Valid values: {', '.join(map(str, processing_levels))}"
            elif method_name == "has_instrument_host":
                desc = f'{desc}. Use context.INSTRUMENT_HOSTS.search("curiosity") to find LIDs'

            lines.append(f"  - {sig_str} - {desc}")
            if summary and summary != desc:
                lines.append(f"    {summary}")
            lines.append(f"    Example: {example}")

        lines.append("")

    # Add uncategorized methods so new API surface shows up automatically
    other_methods = sorted(set(all_methods) - documented)
    if other_methods:
        lines.append("Other Methods:")
        lines.append("  (Public methods not explicitly categorized above)")
        for method_name in other_methods:
            fn = all_methods[method_name]
            sig_str = _methodsignaturestr(method_name, fn)
            summary = _docsummary(fn)
            example = _examplefor(method_name, fn)

            lines.append(f"  - {sig_str}")
            if summary:
                lines.append(f"    {summary}")
            lines.append(f"    Example: {example}")
        lines.append("")

    return "\n".join(lines)


# Generate the base documentation once at module load time
_QUERYBUILDERDOCS = _generatequerybuilderdocumentation()


def querypdsdata(query: str, max_results: int = 50) -> dict[str, Any]:
    # Note: at module load time, we generate the docstring for this function by replacing
    # the {querybuilder_docs} placeholder with the dynamically generated documentation.
    #
    # The MCP framework uses the docstring for this function to guide the LLM.
    """Query PDS data using natural language.

    This tool allows you to query the Planetary Data System (PDS) using natural language.
    Translate the user's natural language query into appropriate QueryBuilder method calls.

    {querybuilder_docs}

    Iterate directly: for product in products: …
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
            logger.warning("Failed to initialize Context (continuing without mission search): %s", e)
            context = None

        products = pep.Products(client)

        # Parse the natural language query and build QueryBuilder chain
        query_lower = query.lower()
        query_builder_calls = []

        # Check for target mentions
        for target in _targets:
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
            for mission_key, mission_name in _missions.items():
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
        #
        # Potential future enhancement is to allow full date ranges and not just years.
        try:
            full_years = re.findall(r'\b(19|21)\d{2}\b', query)
            if full_years:
                # Extract first 4-digit year found
                year_match = re.search(r"\b(?:19|21)\d{2}\b", query)
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


# Assign the dynamically generated documentation to __doc__
if querypdsdata.__doc__:
    querypdsdata.__doc__ = querypdsdata.__doc__.format(querybuilder_docs=_QUERYBUILDERDOCS)


def main():
    """Main entry point to launch the MCP server.

    This server exposes a natural language query tool for PDS data.
    The tool delegates query translation to the MCP client (Claude) by providing
    comprehensive documentation in the tool description.
    """
    mcp = FastMCP("Planetary Data System (PDS) Query Builder Model Context Protocol (MCP) Server")

    # Register the natural language query tool
    mcp.tool(querypdsdata)

    # Run the server with stdio transport
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
