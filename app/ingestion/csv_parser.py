"""
CSV parser for Kaggle/Ergast F1 dataset.

Expected files (standard Ergast CSV column names):
  drivers.csv     — driverId, driverRef, number, code, forename, surname,
                    dob, nationality, url
  results.csv     — resultId, raceId, driverId, constructorId, number, grid,
                    position, positionText, positionOrder, points, laps,
                    time, milliseconds, fastestLap, rank, fastestLapTime,
                    fastestLapSpeed, statusId
  races.csv       — raceId, year, round, circuitId, name, date, time, url
  circuits.csv    — circuitId, circuitRef, name, location, country, lat, lng,
                    alt, url
  constructors.csv — constructorId, constructorRef, name, nationality, url
  status.csv      — statusId, status
  qualifying.csv  — qualifyId, raceId, driverId, constructorId, number,
                    position, q1, q2, q3
  driver_standings.csv — driverStandingsId, raceId, driverId, points,
                          position, positionText, wins
"""

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class RawDriver:
    ergast_driver_id: str
    first_name: str
    last_name: str
    nationality: Optional[str]
    date_of_birth: Optional[str]  # raw string, parsed later
    url: Optional[str]


@dataclass
class RawConstructor:
    ergast_constructor_id: str
    name: str
    nationality: Optional[str]


@dataclass
class RawCircuit:
    ergast_circuit_id: str
    name: str
    location: Optional[str]
    country: Optional[str]


@dataclass
class RawRace:
    race_id: str
    year: int
    circuit_id: str
    name: str
    date: Optional[str]


@dataclass
class RawResult:
    race_id: str
    driver_id: str
    constructor_id: str
    grid: Optional[int]
    position: Optional[int]
    points: float
    laps: Optional[int]
    status_id: str
    fastest_lap_rank: Optional[int]  # rank=1 means fastest lap


@dataclass
class RawQualifying:
    race_id: str
    driver_id: str
    position: Optional[int]


@dataclass
class RawDriverStanding:
    race_id: str
    driver_id: str
    points: float
    position: Optional[int]
    wins: int


@dataclass
class RawStatus:
    status_id: str
    status: str


def _int_or_none(val: str) -> Optional[int]:
    try:
        return int(val)
    except (ValueError, TypeError):
        return None


def _float_or_zero(val: str) -> float:
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0


def _str_or_none(val: str) -> Optional[str]:
    v = val.strip() if val else ""
    return v if v and v != "\\N" else None


def read_drivers(path: Path) -> list[RawDriver]:
    drivers = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            drivers.append(
                RawDriver(
                    ergast_driver_id=row.get("driverRef", row.get("driverId", "")).strip(),
                    first_name=_str_or_none(row.get("forename", "")) or "",
                    last_name=_str_or_none(row.get("surname", "")) or "",
                    nationality=_str_or_none(row.get("nationality", "")),
                    date_of_birth=_str_or_none(row.get("dob", "")),
                    url=_str_or_none(row.get("url", "")),
                )
            )
    return drivers


def read_constructors(path: Path) -> list[RawConstructor]:
    constructors = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            constructors.append(
                RawConstructor(
                    ergast_constructor_id=row.get("constructorRef", row.get("constructorId", "")).strip(),
                    name=row.get("name", "").strip(),
                    nationality=_str_or_none(row.get("nationality", "")),
                )
            )
    return constructors


def read_circuits(path: Path) -> list[RawCircuit]:
    circuits = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            circuits.append(
                RawCircuit(
                    ergast_circuit_id=row.get("circuitRef", row.get("circuitId", "")).strip(),
                    name=row.get("name", "").strip(),
                    location=_str_or_none(row.get("location", "")),
                    country=_str_or_none(row.get("country", "")),
                )
            )
    return circuits


def read_races(path: Path) -> list[RawRace]:
    races = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            year = _int_or_none(row.get("year", ""))
            if year is None:
                continue
            races.append(
                RawRace(
                    race_id=row.get("raceId", "").strip(),
                    year=year,
                    circuit_id=row.get("circuitId", "").strip(),
                    name=row.get("name", "").strip(),
                    date=_str_or_none(row.get("date", "")),
                )
            )
    return races


def read_results(path: Path) -> list[RawResult]:
    results = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            pos_text = row.get("positionText", "").strip()
            position = _int_or_none(row.get("positionOrder", row.get("position", "")))
            # positionText of "R", "D", "E", "W", "F", "N" = non-finishers
            if pos_text.isdigit():
                finish_pos = int(pos_text)
            else:
                finish_pos = None
            results.append(
                RawResult(
                    race_id=row.get("raceId", "").strip(),
                    driver_id=row.get("driverId", "").strip(),
                    constructor_id=row.get("constructorId", "").strip(),
                    grid=_int_or_none(row.get("grid", "")),
                    position=finish_pos,
                    points=_float_or_zero(row.get("points", "0")),
                    laps=_int_or_none(row.get("laps", "")),
                    status_id=row.get("statusId", "").strip(),
                    fastest_lap_rank=_int_or_none(row.get("rank", "")),
                )
            )
    return results


def read_qualifying(path: Path) -> list[RawQualifying]:
    qualifying = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            qualifying.append(
                RawQualifying(
                    race_id=row.get("raceId", "").strip(),
                    driver_id=row.get("driverId", "").strip(),
                    position=_int_or_none(row.get("position", "")),
                )
            )
    return qualifying


def read_driver_standings(path: Path) -> list[RawDriverStanding]:
    standings = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            standings.append(
                RawDriverStanding(
                    race_id=row.get("raceId", "").strip(),
                    driver_id=row.get("driverId", "").strip(),
                    points=_float_or_zero(row.get("points", "0")),
                    position=_int_or_none(row.get("position", "")),
                    wins=int(_float_or_zero(row.get("wins", "0"))),
                )
            )
    return standings


def read_statuses(path: Path) -> dict[str, str]:
    """Returns {statusId: status_text}"""
    statuses = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            statuses[row.get("statusId", "").strip()] = row.get("status", "").strip()
    return statuses
