"""
Transforms raw parsed CSV data into SQLAlchemy model instances.
"""

import uuid
from collections import defaultdict
from datetime import date
from typing import Optional

from app.ingestion.csv_parser import (
    RawCircuit,
    RawConstructor,
    RawDriver,
    RawDriverStanding,
    RawQualifying,
    RawRace,
    RawResult,
)
from app.models.driver import Driver, DriverCareerStats
from app.models.driver_season import DriverSeason
from app.models.race_result import Circuit, RaceResult
from app.models.team import Team


def _parse_date(raw: Optional[str]) -> Optional[date]:
    if not raw:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            from datetime import datetime
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def _normalize_status(status_text: str) -> str:
    s = status_text.lower()
    if s == "finished":
        return "Finished"
    if any(x in s for x in ["accident", "collision", "spun off", "withdrew"]):
        return "DNF"
    if "disqualified" in s:
        return "DSQ"
    if "did not start" in s or "dns" in s:
        return "DNS"
    if "retired" in s or any(x in s for x in ["engine", "gearbox", "hydraulics", "brakes", "suspension", "electrical", "fire", "fuel", "oil", "overheating", "puncture", "wheel", "clutch", "driveshaft", "exhaust", "transmission"]):
        return "DNF"
    return "DNF"


class F1DataTransformer:
    def __init__(
        self,
        raw_drivers: list[RawDriver],
        raw_constructors: list[RawConstructor],
        raw_circuits: list[RawCircuit],
        raw_races: list[RawRace],
        raw_results: list[RawResult],
        raw_qualifying: list[RawQualifying],
        raw_standings: list[RawDriverStanding],
        statuses: dict[str, str],
    ):
        self.raw_drivers = raw_drivers
        self.raw_constructors = raw_constructors
        self.raw_circuits = raw_circuits
        self.raw_races = raw_races
        self.raw_results = raw_results
        self.raw_qualifying = raw_qualifying
        self.raw_standings = raw_standings
        self.statuses = statuses

        # Maps: ergast_id → internal UUID
        self._driver_uuid: dict[str, uuid.UUID] = {}
        self._constructor_uuid: dict[str, uuid.UUID] = {}
        self._circuit_uuid: dict[str, uuid.UUID] = {}

    def build_teams(self) -> list[Team]:
        teams = []
        for rc in self.raw_constructors:
            uid = uuid.uuid4()
            self._constructor_uuid[rc.ergast_constructor_id] = uid
            teams.append(
                Team(
                    id=uid,
                    ergast_constructor_id=rc.ergast_constructor_id,
                    name=rc.name,
                    nationality=rc.nationality,
                )
            )
        return teams

    def build_circuits(self) -> list[Circuit]:
        circuits = []
        for rc in self.raw_circuits:
            uid = uuid.uuid4()
            self._circuit_uuid[rc.ergast_circuit_id] = uid
            circuits.append(
                Circuit(
                    id=uid,
                    ergast_circuit_id=rc.ergast_circuit_id,
                    name=rc.name,
                    location=rc.location,
                    country=rc.country,
                )
            )
        return circuits

    def build_drivers(self) -> list[Driver]:
        drivers = []
        for rd in self.raw_drivers:
            uid = uuid.uuid4()
            self._driver_uuid[rd.ergast_driver_id] = uid
            drivers.append(
                Driver(
                    id=uid,
                    ergast_driver_id=rd.ergast_driver_id,
                    first_name=rd.first_name,
                    last_name=rd.last_name,
                    nationality=rd.nationality,
                    date_of_birth=_parse_date(rd.date_of_birth),
                )
            )
        return drivers

    def build_race_results(self) -> list[RaceResult]:
        """Build flat RaceResult rows from results + race metadata."""
        # Build race_id → RawRace lookup
        race_lookup: dict[str, RawRace] = {r.race_id: r for r in self.raw_races}
        # race_id → circuit ergast_id
        circuit_lookup: dict[str, str] = {
            r.race_id: r.circuit_id for r in self.raw_races
        }
        # constructor lookup per (race_id, driver_id) from results
        constructor_lookup: dict[tuple, str] = {
            (r.race_id, r.driver_id): r.constructor_id for r in self.raw_results
        }

        results = []
        for rr in self.raw_results:
            driver_uuid = self._driver_uuid.get(rr.driver_id)
            if driver_uuid is None:
                continue
            race = race_lookup.get(rr.race_id)
            if race is None:
                continue

            circuit_eid = circuit_lookup.get(rr.race_id)
            circuit_uuid = self._circuit_uuid.get(circuit_eid) if circuit_eid else None

            constructor_eid = constructor_lookup.get((rr.race_id, rr.driver_id))
            team_uuid = self._constructor_uuid.get(constructor_eid) if constructor_eid else None
            # Get team name from constructor mapping
            team_name = None
            for rc in self.raw_constructors:
                if rc.ergast_constructor_id == constructor_eid:
                    team_name = rc.name
                    break

            raw_status = self.statuses.get(rr.status_id, "Finished")
            status = _normalize_status(raw_status)

            results.append(
                RaceResult(
                    id=uuid.uuid4(),
                    driver_id=driver_uuid,
                    circuit_id=circuit_uuid,
                    season_year=race.year,
                    race_name=race.name,
                    race_date=_parse_date(race.date),
                    grid_position=rr.grid,
                    finish_position=rr.position,
                    points=rr.points,
                    status=status,
                    fastest_lap=(rr.fastest_lap_rank == 1),
                    lap_count=rr.laps,
                    team_name=team_name,
                )
            )
        return results

    def build_driver_seasons(self, race_results: list[RaceResult]) -> list[DriverSeason]:
        """Aggregate race results into per-driver-per-season rows."""
        # Group results by (driver_id, season_year)
        grouped: dict[tuple, list[RaceResult]] = defaultdict(list)
        for rr in race_results:
            grouped[(rr.driver_id, rr.season_year)].append(rr)

        # Get final championship standings for position
        # standings keyed by (driver ergast_id, year)
        # We need the last race of each season to get final standings
        race_year_lookup = {r.race_id: r.year for r in self.raw_races}
        # Sort standings by finding max race_id per driver per year (proxy for last race)
        standings_by_driver_year: dict[tuple, RawDriverStanding] = {}
        for s in self.raw_standings:
            year = race_year_lookup.get(s.race_id)
            if year is None:
                continue
            driver_ergast = None
            for eid, uid in self._driver_uuid.items():
                if str(uid) == s.driver_id or eid == s.driver_id:
                    driver_ergast = eid
                    break
            key = (s.driver_id, year)
            # Keep the entry with the highest race_id (= last race of season)
            existing = standings_by_driver_year.get(key)
            if existing is None or s.race_id > existing.race_id:
                standings_by_driver_year[key] = s

        seasons = []
        for (driver_uuid, season_year), results in grouped.items():
            wins = sum(1 for r in results if r.finish_position == 1)
            podiums = sum(1 for r in results if r.finish_position in (1, 2, 3))
            poles = sum(1 for r in results if r.grid_position == 1)
            fastest_laps = sum(1 for r in results if r.fastest_lap)
            dnfs = sum(1 for r in results if r.status in ("DNF", "DSQ", "DNS"))
            total_points = sum(r.points for r in results)

            # Find team_id from majority constructor this season
            team_name_counts: dict[str, int] = defaultdict(int)
            for r in results:
                if r.team_name:
                    team_name_counts[r.team_name] += 1
            primary_team_name = max(team_name_counts, key=team_name_counts.get) if team_name_counts else None
            team_id = None
            if primary_team_name:
                for rc in self.raw_constructors:
                    if rc.name == primary_team_name:
                        team_id = self._constructor_uuid.get(rc.ergast_constructor_id)
                        break

            # Championship position
            champ_pos = None
            for driver_eid, uid in self._driver_uuid.items():
                if uid == driver_uuid:
                    standing = standings_by_driver_year.get((driver_eid, season_year))
                    # Also try by numeric ergast driverId
                    if standing is None:
                        for s in self.raw_standings:
                            if race_year_lookup.get(s.race_id) == season_year:
                                pass  # handled above
                    if standing:
                        champ_pos = standing.position
                    break

            seasons.append(
                DriverSeason(
                    id=uuid.uuid4(),
                    driver_id=driver_uuid,
                    team_id=team_id,
                    season_year=season_year,
                    championship_position=champ_pos,
                    points=total_points,
                    wins=wins,
                    podiums=podiums,
                    poles=poles,
                    fastest_laps=fastest_laps,
                    races_entered=len(results),
                    dnfs=dnfs,
                )
            )
        return seasons

    def build_career_stats(
        self,
        drivers: list[Driver],
        seasons: list[DriverSeason],
        race_results: list[RaceResult],
    ) -> list[DriverCareerStats]:
        """Aggregate all seasons into career-level stats per driver."""
        driver_seasons: dict[uuid.UUID, list[DriverSeason]] = defaultdict(list)
        for s in seasons:
            driver_seasons[s.driver_id].append(s)

        driver_results: dict[uuid.UUID, list[RaceResult]] = defaultdict(list)
        for r in race_results:
            driver_results[r.driver_id].append(r)

        # Build team name lookup
        team_name_by_id: dict[uuid.UUID, str] = {}
        for rc in self.raw_constructors:
            uid = self._constructor_uuid.get(rc.ergast_constructor_id)
            if uid:
                team_name_by_id[uid] = rc.name

        stats_list = []
        for driver in drivers:
            s_list = driver_seasons[driver.id]
            r_list = driver_results[driver.id]

            starts = len(r_list)
            wins = sum(s.wins for s in s_list)
            podiums = sum(s.podiums for s in s_list)
            poles = sum(s.poles for s in s_list)
            fastest_laps = sum(s.fastest_laps for s in s_list)
            points = sum(s.points for s in s_list)
            dnfs = sum(s.dnfs for s in s_list)
            championships = sum(1 for s in s_list if s.championship_position == 1)

            win_rate = round(wins / starts, 4) if starts > 0 else 0.0
            podium_rate = round(podiums / starts, 4) if starts > 0 else 0.0
            dnf_rate = round(dnfs / starts, 4) if starts > 0 else 0.0

            finish_positions = [r.finish_position for r in r_list if r.finish_position is not None]
            avg_finish = round(sum(finish_positions) / len(finish_positions), 2) if finish_positions else None

            grid_positions = [r.grid_position for r in r_list if r.grid_position is not None and r.grid_position > 0]
            avg_grid = round(sum(grid_positions) / len(grid_positions), 2) if grid_positions else None

            active_years = sorted({s.season_year for s in s_list})
            teams = list({team_name_by_id[s.team_id] for s in s_list if s.team_id and s.team_id in team_name_by_id})

            race_dates = [r.race_date for r in r_list if r.race_date]
            last_race = max(race_dates) if race_dates else None

            stats_list.append(
                DriverCareerStats(
                    id=uuid.uuid4(),
                    driver_id=driver.id,
                    total_race_starts=starts,
                    total_wins=wins,
                    total_podiums=podiums,
                    total_pole_positions=poles,
                    total_fastest_laps=fastest_laps,
                    total_championship_points=points,
                    championships_won=championships,
                    career_win_rate=win_rate,
                    career_podium_rate=podium_rate,
                    dnf_rate=dnf_rate,
                    avg_qualifying_position=avg_grid,
                    avg_finish_position=avg_finish,
                    seasons_active=active_years,
                    teams_driven_for=teams,
                    active_status=bool(active_years and max(active_years) >= 2022),
                    last_race_date=last_race,
                )
            )
        return stats_list
