import sqlite3
import random

conn = sqlite3.connect('sales_data.sqlite')
cursor = conn.cursor()

# Create table
cursor.execute('''
CREATE TABLE IF NOT EXISTS daily_sales (
    date TEXT,
    region TEXT,
    sales_amount INTEGER,
    marketing_spend INTEGER
)
''')

# Insert sample data
regions = ['North', 'South', 'East', 'West']
for i in range(1, 31):
    for region in regions:
        cursor.execute(f"INSERT INTO daily_sales VALUES ('2023-10-{i:02d}', '{region}', {random.randint(1000, 5000)}, {random.randint(100, 1000)})")

conn.commit()
conn.close()
print("Database 'sales_data.sqlite' created successfully!")