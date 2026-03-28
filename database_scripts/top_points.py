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
# Step 3: Find driver with most points
# -------------------------------
# Make sure Points column is numeric
race_results_df['Points'] = pd.to_numeric(race_results_df['Points'], errors='coerce').fillna(0)

# Group by driver and sum points
total_points = race_results_df.groupby(['DriverNumber', 'FullName'])['Points'].sum().reset_index()

# Sort descending by points
total_points_sorted = total_points.sort_values(by='Points', ascending=False)

# Get the top driver
top_driver = total_points_sorted.iloc[0]

print(f"Driver with most points: {top_driver['FullName']} ({top_driver['Points']} points)")

# -------------------------------
# Optional: Show top 5 drivers
# -------------------------------
print("\nTop 5 drivers by points:")
print(total_points_sorted.head())

# -------------------------------
# Step 4: Close the connection
# -------------------------------
engine.dispose()