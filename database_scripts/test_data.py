# load_f1_data.py
import pandas as pd
from sqlalchemy import create_engine

# -------------------------------
# Step 1: Connect to the database
# -------------------------------
# Format: mysql+pymysql://username:password@host/database
engine = create_engine('mysql+pymysql://root:code@localhost/f1_analytics')

# -------------------------------
# Step 2: Load tables into DataFrames
# -------------------------------
try:
    lap_times_df = pd.read_sql('SELECT * FROM LapTimes', engine)
    qual_times_df = pd.read_sql('SELECT * FROM QualTimes', engine)
    race_results_df = pd.read_sql('SELECT * FROM RaceResults', engine)
    race_times_df = pd.read_sql('SELECT * FROM RaceTimes', engine)
    print("All tables loaded successfully!")

except Exception as e:
    print("Error loading tables:", e)
    exit(1)

# -------------------------------
# Step 3: Example operations
# -------------------------------
# Show first 5 rows of each table
print("\nLapTimes sample:")
print(lap_times_df.head())

print("\nQualTimes sample:")
print(qual_times_df.head())

print("\nRaceResults sample:")
print(race_results_df.head())

print("\nRaceTimes sample:")
print(race_times_df.head())

# Example: Merge LapTimes with RaceResults on DriverNumber and Event Name
merged_df = pd.merge(
    lap_times_df,
    race_results_df,
    how='inner',
    left_on=['DriverNumber', 'Event Name'],
    right_on=['DriverNumber', 'Event Name']
)

print("\nMerged LapTimes + RaceResults sample:")
print(merged_df.head())

# -------------------------------
# Step 4: Close the connection
# -------------------------------
engine.dispose()
print("\nDatabase connection closed.")