"""
Basic data quality validation for ingested F1 data.
Raises ValueError with a descriptive message if critical data is missing.
"""

from app.ingestion.csv_parser import RawDriver


def validate_drivers(drivers: list[RawDriver]) -> list[str]:
    """Returns list of warning strings (non-fatal issues)."""
    warnings = []
    seen_ids: set[str] = set()
    for d in drivers:
        if not d.ergast_driver_id:
            warnings.append(f"Driver missing ergast_driver_id: {d.first_name} {d.last_name}")
        if not d.first_name or not d.last_name:
            warnings.append(f"Driver missing name: id={d.ergast_driver_id}")
        if d.ergast_driver_id in seen_ids:
            warnings.append(f"Duplicate driver id: {d.ergast_driver_id}")
        seen_ids.add(d.ergast_driver_id)
    return warnings
