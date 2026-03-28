"""
FastF1-format CSV adapter.

Reads the denormalized FastF1 exports (RaceResults.csv, QualTimes.csv, etc.)
and converts them into the Raw* dataclasses used by F1DataTransformer, so the
rest of the ingestion pipeline can run unchanged.

Expected files in data_dir:
  RaceResults.csv  — one row per driver per race (primary source)
  QualTimes.csv    — qualifying positions (optional)
"""

import csv
from pathlib import Path
from typing import Optional

from app.ingestion.csv_parser import (
    RawCircuit,
    RawConstructor,
    RawDriver,
    RawQualifying,
    RawRace,
    RawResult,
)

SEASON_YEAR = 2025  # FastF1 files don't carry a year column; 2025 data confirmed


def _int_or_none(val: str) -> Optional[int]:
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None


def _float_or_zero(val: str) -> float:
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0


def _str_or_none(val: str) -> Optional[str]:
    v = val.strip() if val else ""
    return v if v else None


def _status_to_id(status: str) -> str:
    """Return a synthetic status_id string so the transformer can look it up."""
    return status.strip()


def parse_fastf1_csvs(data_dir: Path) -> dict:
    """
    Parse FastF1 CSVs and return a dict of Raw* lists matching what
    F1DataTransformer expects.
    """
    results_path = data_dir / "RaceResults.csv"
    qual_path = data_dir / "QualTimes.csv"

    rows = []
    with open(results_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # --- Unique drivers ---
    seen_drivers: dict[str, RawDriver] = {}
    for row in rows:
        did = row.get("DriverId", "").strip()
        if did and did not in seen_drivers:
            seen_drivers[did] = RawDriver(
                ergast_driver_id=did,
                first_name=_str_or_none(row.get("FirstName", "")) or "",
                last_name=_str_or_none(row.get("LastName", "")) or "",
                nationality=_str_or_none(row.get("CountryCode", "")),
                date_of_birth=None,
                url=_str_or_none(row.get("HeadshotUrl", "")),
            )
    raw_drivers = list(seen_drivers.values())

    # --- Unique constructors ---
    seen_constructors: dict[str, RawConstructor] = {}
    for row in rows:
        tid = row.get("TeamId", "").strip()
        if tid and tid not in seen_constructors:
            seen_constructors[tid] = RawConstructor(
                ergast_constructor_id=tid,
                name=row.get("TeamName", tid).strip(),
                nationality=None,
            )
    raw_constructors = list(seen_constructors.values())

    # --- Unique circuits (keyed by Location slug) ---
    seen_circuits: dict[str, RawCircuit] = {}
    for row in rows:
        loc = row.get("Location", "").strip()
        loc_key = loc.lower().replace(" ", "_")
        if loc_key and loc_key not in seen_circuits:
            seen_circuits[loc_key] = RawCircuit(
                ergast_circuit_id=loc_key,
                name=row.get("Event Name", loc).strip(),
                location=loc or None,
                country=_str_or_none(row.get("Country", "")),
            )
    raw_circuits = list(seen_circuits.values())

    # --- Unique races (one per Round) ---
    seen_races: dict[str, RawRace] = {}
    for row in rows:
        rnd = row.get("Round", "").strip()
        if rnd and rnd not in seen_races:
            loc = row.get("Location", "").strip()
            loc_key = loc.lower().replace(" ", "_")
            seen_races[rnd] = RawRace(
                race_id=rnd,
                year=SEASON_YEAR,
                circuit_id=loc_key,
                name=row.get("Event Name", f"Round {rnd}").strip(),
                date=None,
            )
    raw_races = list(seen_races.values())

    # --- Results ---
    # Build a synthetic status lookup: status_id → status_text
    # (we use the status string itself as the ID)
    statuses: dict[str, str] = {}
    raw_results: list[RawResult] = []
    for row in rows:
        status_text = row.get("Status", "Finished").strip()
        status_id = _status_to_id(status_text)
        statuses[status_id] = status_text

        did = row.get("DriverId", "").strip()
        tid = row.get("TeamId", "").strip()
        rnd = row.get("Round", "").strip()
        if not (did and rnd):
            continue

        raw_results.append(
            RawResult(
                race_id=rnd,
                driver_id=did,
                constructor_id=tid,
                grid=_int_or_none(row.get("GridPosition", "")),
                position=_int_or_none(row.get("ClassifiedPosition", row.get("Position", ""))),
                points=_float_or_zero(row.get("Points", "0")),
                laps=_int_or_none(row.get("Laps", "")),
                status_id=status_id,
                fastest_lap_rank=None,  # not in RaceResults.csv
            )
        )

    # --- Qualifying (optional) ---
    raw_qualifying: list[RawQualifying] = []
    if qual_path.exists():
        with open(qual_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                did = row.get("DriverId", "").strip()
                rnd = row.get("Round", "").strip()
                if did and rnd:
                    raw_qualifying.append(
                        RawQualifying(
                            race_id=rnd,
                            driver_id=did,
                            position=_int_or_none(row.get("Position", "")),
                        )
                    )

    return {
        "raw_drivers": raw_drivers,
        "raw_constructors": raw_constructors,
        "raw_circuits": raw_circuits,
        "raw_races": raw_races,
        "raw_results": raw_results,
        "raw_qualifying": raw_qualifying,
        "raw_standings": [],
        "statuses": statuses,
    }


def is_fastf1_data_dir(data_dir: Path) -> bool:
    """Return True if the directory contains FastF1-format files instead of Ergast."""
    return (data_dir / "RaceResults.csv").exists()
