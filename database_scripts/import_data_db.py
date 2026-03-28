import pandas as pd
from sqlalchemy import create_engine

# Connect to MariaDB
engine = create_engine('mysql+pymysql://root:code@localhost/f1_analytics')

# List of CSV files and their corresponding table names
csv_files = {
    #"LapTimes.csv": "LapTimes",
    "QualTimes.csv": "QualTimes",
    "RaceResults.csv": "RaceResults",
    "RaceTimes.csv": "RaceTimes"
}

# Loop through each file and import
for csv_file, table_name in csv_files.items():
    print(f"Importing {csv_file} into table {table_name}...")
    df = pd.read_csv(f'/codequantum/CQ2026_DataTrack/data/{csv_file}')  # Read CSV
    df.to_sql(table_name, engine, if_exists='replace', index=False)      # Import to MariaDB
    print(f"{csv_file} imported successfully into {table_name}!")

print("All CSV files imported successfully!")