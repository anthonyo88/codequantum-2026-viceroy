# top_points.py
import pandas as pd
from sqlalchemy import create_engine

# -------------------------------
# Step 1: Connect to the database
# -------------------------------
engine = create_engine('mysql+pymysql://root:code@localhost/f1_analytics')

# -------------------------------
# Step 2: Load RaceResults table
# -------------------------------
race_results_df = pd.read_sql('SELECT * FROM RaceResults', engine)

# -------------------------------
# Step 3: Find top 10 drivers by points
# -------------------------------

# Make sure Points column is numeric
race_results_df['Points'] = pd.to_numeric(race_results_df['Points'], errors='coerce').fillna(0)

# Group by driver and sum points (include TeamName + DriverId)
total_points = race_results_df.groupby(
    ['DriverId', 'DriverNumber', 'FullName', 'TeamName']
)['Points'].sum().reset_index()

# Sort descending by points
total_points_sorted = total_points.sort_values(by='Points', ascending=False)

# Get the top 10 drivers
top_10_drivers = total_points_sorted.head(10).reset_index(drop=True)

# Add ranking column starting at 1
top_10_drivers.index = top_10_drivers.index + 1

# -------------------------------
# Step 4: Print results
# -------------------------------

print("Top 10 drivers by total points:\n")
print(top_10_drivers)

# Optional: print #1 driver
top_driver = total_points_sorted.iloc[0]
print(f"\nTop driver: {top_driver['FullName']} ({top_driver['TeamName']}) - {top_driver['Points']} points")

# -------------------------------
# Step 5: Close the connection
# -------------------------------
engine.dispose()
