import pandas as pd
from sqlalchemy import create_engine
import ollama

# 1️⃣ Connect to your MariaDB database
engine = create_engine('mysql+pymysql://root:code@localhost/f1_analytics')

# 2️⃣ Pull a small sample from RaceResults (top 3 drivers by points)
query = """
SELECT DriverNumber, FullName, Points
FROM RaceResults
ORDER BY Points DESC
LIMIT 3;
"""
sample_df = pd.read_sql(query, engine)

# 3️⃣ Prepare prompt for Ollama
summary = sample_df.to_dict(orient='records')
prompt = f"Here are 3 drivers with their points: {summary}. Can you give a short insight about them?"

# 4️⃣ Send to Qwen 3.5
response = ollama.chat(
    model="qwen3.5:latest",
    messages=[{"role": "user", "content": prompt}]
)

# 5️⃣ Print response
print("=== Ollama DB Test Output ===")
print(response['content'])