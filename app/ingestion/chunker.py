from typing import Optional

from app.config import settings
from app.models.document_chunk import DocumentChunk
from app.models.driver import Driver, DriverCareerStats
from app.models.driver_season import DriverSeason

_MAX_SEASONS = 5  # most recent seasons to include as individual chunks


def build_chunks(driver: Driver, seasons: list[DriverSeason]) -> list[DocumentChunk]:
    """
    Build DocumentChunk objects for a driver.
    Embeddings are NOT set here — Celery tasks handle that.
    """
    chunks: list[DocumentChunk] = []
    stats: Optional[DriverCareerStats] = driver.career_stats

    chunks.append(_bio_chunk(driver, stats))

    if stats:
        chunks.append(_career_stats_chunk(driver, stats))

    # Most recent seasons first, capped at _MAX_SEASONS
    recent_seasons = sorted(seasons, key=lambda s: s.season_year, reverse=True)[:_MAX_SEASONS]
    for season in recent_seasons:
        chunks.append(_season_chunk(driver, season))

    return chunks


def _bio_chunk(driver: Driver, stats: Optional[DriverCareerStats]) -> DocumentChunk:
    dob = driver.date_of_birth.isoformat() if driver.date_of_birth else "unknown"
    status = "Active" if driver.active_status else "Retired"
    license = driver.license_grade or "unknown"

    parts = [
        f"{driver.full_name}.",
        f"Nationality: {driver.nationality or 'unknown'}.",
        f"Born: {dob}.",
        f"Status: {status}.",
        f"License grade: {license}.",
    ]

    if stats:
        teams = ", ".join(stats.teams_driven_for) if stats.teams_driven_for else "unknown"
        parts += [
            f"Career: {stats.total_wins} wins, {stats.total_podiums} podiums, "
            f"{stats.championships_won} championships, {stats.total_pole_positions} poles.",
            f"Teams: {teams}.",
            f"Win rate: {stats.career_win_rate:.1f}%.",
            f"Podium rate: {stats.career_podium_rate:.1f}%.",
        ]

    if driver.biography:
        # Truncate long biographies to keep chunks concise
        bio = driver.biography[:500]
        parts.append(f"Bio: {bio}")

    return DocumentChunk(
        driver_id=driver.id,
        source_type="driver_bio",
        content=" ".join(parts),
        metadata_={"driver_name": driver.full_name},
        embedding_model=settings.embedding_model,
        embedding=None,
    )


def _career_stats_chunk(driver: Driver, stats: DriverCareerStats) -> DocumentChunk:
    seasons_str = (
        f"{min(stats.seasons_active)}–{max(stats.seasons_active)}"
        if stats.seasons_active
        else "unknown"
    )
    avg_finish = f"{stats.avg_finish_position:.1f}" if stats.avg_finish_position else "N/A"
    avg_qual = f"{stats.avg_qualifying_position:.1f}" if stats.avg_qualifying_position else "N/A"

    content = (
        f"Career statistics for {driver.full_name}: "
        f"{stats.total_race_starts} race starts, "
        f"{stats.total_wins} wins, "
        f"{stats.total_podiums} podiums, "
        f"{stats.total_pole_positions} poles, "
        f"{stats.total_fastest_laps} fastest laps, "
        f"{stats.championships_won} championships won. "
        f"DNF rate: {stats.dnf_rate:.1f}%. "
        f"Average finish position: {avg_finish}. "
        f"Average qualifying position: {avg_qual}. "
        f"Active seasons: {seasons_str}."
    )

    return DocumentChunk(
        driver_id=driver.id,
        source_type="career_stats",
        content=content,
        metadata_={"driver_name": driver.full_name},
        embedding_model=settings.embedding_model,
        embedding=None,
    )


def _season_chunk(driver: Driver, season: DriverSeason) -> DocumentChunk:
    parts = [
        f"{driver.full_name} in {season.season_year}:",
        f"{season.races_entered} races,",
        f"{season.wins} wins,",
        f"{season.podiums} podiums,",
        f"{season.poles} poles,",
        f"{season.points:.0f} points.",
    ]

    if season.championship_position:
        parts.append(f"Championship position: P{season.championship_position}.")

    if season.dnfs:
        parts.append(f"DNFs: {season.dnfs}.")

    if season.teammate_qualifying_delta is not None:
        sign = "+" if season.teammate_qualifying_delta >= 0 else ""
        parts.append(
            f"vs teammate qualifying: {sign}{season.teammate_qualifying_delta:.3f}s."
        )

    if season.teammate_race_delta is not None:
        sign = "+" if season.teammate_race_delta >= 0 else ""
        parts.append(f"vs teammate race: {sign}{season.teammate_race_delta:.3f}s.")

    return DocumentChunk(
        driver_id=driver.id,
        source_type="season_summary",
        content=" ".join(parts),
        metadata_={"driver_name": driver.full_name, "season_year": season.season_year},
        embedding_model=settings.embedding_model,
        embedding=None,
    )
