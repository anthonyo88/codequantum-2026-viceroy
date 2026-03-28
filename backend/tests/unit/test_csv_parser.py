import csv
import tempfile
from pathlib import Path

from app.ingestion.csv_parser import read_drivers


def test_read_drivers_standard_columns(tmp_path):
    csv_file = tmp_path / "drivers.csv"
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["driverId", "driverRef", "number", "code", "forename", "surname", "dob", "nationality", "url"],
        )
        writer.writeheader()
        writer.writerow({
            "driverId": "1",
            "driverRef": "hamilton",
            "number": "44",
            "code": "HAM",
            "forename": "Lewis",
            "surname": "Hamilton",
            "dob": "1985-01-07",
            "nationality": "British",
            "url": "http://en.wikipedia.org/wiki/Lewis_Hamilton",
        })

    drivers = read_drivers(csv_file)
    assert len(drivers) == 1
    assert drivers[0].first_name == "Lewis"
    assert drivers[0].last_name == "Hamilton"
    assert drivers[0].nationality == "British"
    assert drivers[0].date_of_birth == "1985-01-07"
    assert drivers[0].ergast_driver_id == "hamilton"


def test_read_drivers_handles_null_values(tmp_path):
    csv_file = tmp_path / "drivers.csv"
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["driverRef", "forename", "surname", "dob", "nationality", "url"],
        )
        writer.writeheader()
        writer.writerow({
            "driverRef": "test_driver",
            "forename": "Test",
            "surname": "Driver",
            "dob": "\\N",
            "nationality": "\\N",
            "url": "\\N",
        })

    drivers = read_drivers(csv_file)
    assert drivers[0].date_of_birth is None
    assert drivers[0].nationality is None
