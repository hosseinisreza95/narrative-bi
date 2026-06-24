import sqlite3
import pandas as pd
import random
from datetime import datetime, timedelta

# ساخت اتصال به دیتابیس محلی
conn = sqlite3.connect('sales_data.sqlite')

# تولید دیتای تستی
dates = [datetime.today() - timedelta(days=x) for x in range(30)]
data = {
    'date': [d.strftime('%Y-%m-%d') for d in dates],
    'region': [random.choice(['North', 'South', 'East', 'West']) for _ in range(30)],
    'sales_amount': [random.randint(1000, 5000) for _ in range(30)],
    'marketing_spend': [random.randint(200, 1000) for _ in range(30)]
}

df = pd.DataFrame(data)
df.to_sql('daily_sales', conn, if_exists='replace', index=False)
print("دیتابیس تستی با موفقیت ساخته شد!")
conn.close()