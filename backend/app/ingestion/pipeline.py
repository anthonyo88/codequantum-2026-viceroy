"""
F1 data ingestion pipeline.

Usage:
  from app.ingestion.pipeline import run_ingestion
  await run_ingestion(data_dir=Path("data/raw"), db_session=session)
"""

import structlog
from pathlib import Path
from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.ingestion.csv_parser import (
    read_circuits,
    read_constructors,
    read_driver_standings,
    read_drivers,
    read_qualifying,
    read_races,
    read_results,
    read_statuses,
)
from app.ingestion.fastf1_pipeline import is_fastf1_data_dir, parse_fastf1_csvs
from app.ingestion.transformers import F1DataTransformer
from app.ingestion.validators import validate_drivers
from app.models.driver import Driver, DriverCareerStats
from app.models.driver_season import DriverSeason
from app.models.race_result import Circuit, RaceResult
from app.models.team import Team

log = structlog.get_logger()

# Maps our expected file name → possible alternative names from different Kaggle exports
FILE_ALIASES = {
    "drivers.csv": ["drivers.csv", "driver.csv"],
    "results.csv": ["results.csv", "result.csv"],
    "races.csv": ["races.csv", "race.csv"],
    "circuits.csv": ["circuits.csv", "circuit.csv"],
    "constructors.csv": ["constructors.csv", "constructor.csv", "teams.csv"],
    "qualifying.csv": ["qualifying.csv", "qualifyingresults.csv"],
    "driver_standings.csv": ["driver_standings.csv", "driverStandings.csv"],
    "status.csv": ["status.csv", "statuses.csv"],
}


def _find_file(data_dir: Path, key: str) -> Optional[Path]:
    for alias in FILE_ALIASES[key]:
        candidate = data_dir / alias
        if candidate.exists():
            return candidate
    return None


async def _truncate_tables(session: AsyncSession) -> None:
    """Clear all F1 data tables in dependency order."""
    tables = [
        "driver_career_stats",
        "driver_seasons",
        "race_results",
        "document_chunks",
        "drivers",
        "circuits",
        "teams",
    ]
    for table in tables:
        await session.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
    await session.commit()
    log.info("ingestion.tables_truncated")


async def run_ingestion(
    data_dir: Path,
    session: AsyncSession,
    truncate_first: bool = True,
) -> dict:
    """
    Run full CSV ingestion pipeline.
    Returns a summary dict with row counts.
    """
    data_dir = Path(data_dir)
    log.info("ingestion.start", data_dir=str(data_dir))

    # --- Load CSV files ---
    log.info("ingestion.reading_csvs")
    if is_fastf1_data_dir(data_dir):
        log.info("ingestion.format_detected", format="fastf1")
        parsed = parse_fastf1_csvs(data_dir)
        raw_drivers = parsed["raw_drivers"]
        raw_constructors = parsed["raw_constructors"]
        raw_circuits = parsed["raw_circuits"]
        raw_races = parsed["raw_races"]
        raw_results = parsed["raw_results"]
        raw_qualifying = parsed["raw_qualifying"]
        raw_standings = parsed["raw_standings"]
        statuses = parsed["statuses"]
    else:
        drivers_path = _find_file(data_dir, "drivers.csv")
        results_path = _find_file(data_dir, "results.csv")
        races_path = _find_file(data_dir, "races.csv")
        circuits_path = _find_file(data_dir, "circuits.csv")
        constructors_path = _find_file(data_dir, "constructors.csv")

        if not all([drivers_path, results_path, races_path, circuits_path, constructors_path]):
            missing = [k for k, p in {
                "drivers": drivers_path,
                "results": results_path,
                "races": races_path,
                "circuits": circuits_path,
                "constructors": constructors_path,
            }.items() if p is None]
            raise FileNotFoundError(f"Required CSV files not found in {data_dir}: {missing}")

        qualifying_path = _find_file(data_dir, "qualifying.csv")
        standings_path = _find_file(data_dir, "driver_standings.csv")
        status_path = _find_file(data_dir, "status.csv")

        raw_drivers = read_drivers(drivers_path)
        raw_constructors = read_constructors(constructors_path)
        raw_circuits = read_circuits(circuits_path)
        raw_races = read_races(races_path)
        raw_results = read_results(results_path)
        raw_qualifying = read_qualifying(qualifying_path) if qualifying_path else []
        raw_standings = read_driver_standings(standings_path) if standings_path else []
        statuses = read_statuses(status_path) if status_path else {}

    log.info(
        "ingestion.csvs_loaded",
        drivers=len(raw_drivers),
        constructors=len(raw_constructors),
        circuits=len(raw_circuits),
        races=len(raw_races),
        results=len(raw_results),
    )

    # --- Validate ---
    warnings = validate_drivers(raw_drivers)
    for w in warnings:
        log.warning("ingestion.validation_warning", message=w)

    # --- Transform ---
    log.info("ingestion.transforming")
    transformer = F1DataTransformer(
        raw_drivers=raw_drivers,
        raw_constructors=raw_constructors,
        raw_circuits=raw_circuits,
        raw_races=raw_races,
        raw_results=raw_results,
        raw_qualifying=raw_qualifying,
        raw_standings=raw_standings,
        statuses=statuses,
    )

    teams = transformer.build_teams()
    circuits = transformer.build_circuits()
    drivers = transformer.build_drivers()
    race_results = transformer.build_race_results()
    driver_seasons = transformer.build_driver_seasons(race_results)
    career_stats = transformer.build_career_stats(drivers, driver_seasons, race_results)

    log.info(
        "ingestion.transformation_complete",
        teams=len(teams),
        circuits=len(circuits),
        drivers=len(drivers),
        race_results=len(race_results),
        driver_seasons=len(driver_seasons),
        career_stats=len(career_stats),
    )

    # --- Persist ---
    if truncate_first:
        await _truncate_tables(session)

    log.info("ingestion.persisting")

    # Insert in FK-safe order
    session.add_all(teams)
    await session.flush()

    session.add_all(circuits)
    await session.flush()

    session.add_all(drivers)
    await session.flush()

    # career_stats reference drivers, so flush drivers first
    session.add_all(career_stats)
    await session.flush()

    # Batch inserts for large tables
    BATCH = 5000
    for i in range(0, len(race_results), BATCH):
        session.add_all(race_results[i : i + BATCH])
        await session.flush()

    for i in range(0, len(driver_seasons), BATCH):
        session.add_all(driver_seasons[i : i + BATCH])
        await session.flush()

    await session.commit()

    # Queue embedding generation for every ingested driver
    from app.workers.embedding_tasks import generate_driver_embedding
    for driver in drivers:
        generate_driver_embedding.delay(str(driver.id))
    log.info("ingestion.embedding_tasks_queued", count=len(drivers))

    summary = {
        "teams": len(teams),
        "circuits": len(circuits),
        "drivers": len(drivers),
        "race_results": len(race_results),
        "driver_seasons": len(driver_seasons),
        "career_stats": len(career_stats),
        "warnings": len(warnings),
    }
    log.info("ingestion.complete", **summary)
    return summary
