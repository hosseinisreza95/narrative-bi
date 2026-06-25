import os
import sqlite3
import pandas as pd
import chromadb
from chromadb.config import Settings
from openai import OpenAI
from dotenv import load_dotenv

# Load API Key from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ==========================================
# STEP 1: Auto-Extract Schema from Database
# ==========================================
def extract_schemas_from_db(db_path):
    print(f"Reading database schemas from: {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = cursor.fetchall()
    
    schemas = []
    table_names = []
    
    for name, sql in tables:
        if sql:
            schemas.append(sql)
            table_names.append(name)
            
    conn.close()
    return schemas, table_names

db_schemas, db_table_names = extract_schemas_from_db('sales_data.sqlite')

# ==========================================
# STEP 2: Setup Vector Database (Memory)
# ==========================================
print("\nInitializing Vector DB and memorizing schemas...")

# FIX: Turn off ChromaDB telemetry to remove annoying warnings
chroma_client = chromadb.Client(Settings(anonymized_telemetry=False))

try:
    chroma_client.delete_collection("database_schemas")
except:
    pass
collection = chroma_client.create_collection(name="database_schemas")

collection.add(
    documents=db_schemas,
    metadatas=[{"table": name} for name in db_table_names],
    ids=[f"table_{name}" for name in db_table_names]
)

# ==========================================
# STEP 3: The User Asks a Question
# ==========================================
user_question = "What is the amount of sales in North?"
print(f"\n👤 User Question: {user_question}")

results = collection.query(
    query_texts=[user_question],
    n_results=1 
)

relevant_schema = results['documents'][0][0]
matched_table_name = results['metadatas'][0][0]['table']
print(f"AI found relevant table: '{matched_table_name}'")

# ==========================================
# STEP 4: Generate SQL with OpenAI
# ==========================================
print("\nGenerating SQL Query...")

prompt = f"""You are a Senior SQL Developer.
Your task is to write a SQLite query to answer the user's question.
Return ONLY the raw SQL query. Do not use formatting blocks (like ```sql). Do not explain anything.

Table Schema:
{relevant_schema}

Question: {user_question}
"""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}]
)

generated_sql = response.choices[0].message.content.strip()
print(f"SQL Generated: {generated_sql}")


# 💡 استخراج و پرینت مصرف توکن‌ها برای تولید SQL
sql_prompt_tokens = response.usage.prompt_tokens
sql_completion_tokens = response.usage.completion_tokens
sql_total_tokens = response.usage.total_tokens

print(f"   ✓ SQL Generated: {generated_sql}")
print(f"   🪙 Token Usage (SQL): {sql_total_tokens} tokens (Prompt: {sql_prompt_tokens} | Output: {sql_completion_tokens})")

# ==========================================
# STEP 5: Execute SQL and Fetch Data
# ==========================================
print("\nExecuting SQL on Database...")

# Connect to database and run the generated query
conn = sqlite3.connect('sales_data.sqlite')
try:
    # We use Pandas to easily run the query and get a formatted table
    df = pd.read_sql_query(generated_sql, conn)
    
    print("\nFinal Extracted Data:")
    print("-" * 30)
    print(df.to_string(index=False)) # Print dataframe without row numbers
    print("-" * 30)
    
except Exception as e:
    print(f"\nError executing SQL: {e}")
finally:
    conn.close()


# ==========================================
# STEP 6: Generate Narrative Analysis (The "BI" part)
# ==========================================
print("\nGenerating Narrative Analysis...")

# پرامپت تحلیلگر: دیتا و سوال رو به مدل می‌دیم تا تفسیرش کنه
narrative_prompt = f"""You are a Senior Data Analyst.
The user asked this question: "{user_question}"
We ran this SQL query to get the data: {generated_sql}
And here is the raw data result from the database:
{df.to_string(index=False)}

Your task:
Write a short, professional, and easy-to-understand response for a business manager.
Explain what this data means in the context of their question.
Write the final response entirely in Persian (فارسی).
"""

# ارسال درخواست به OpenAI برای تولید متن روایت
narrative_response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": narrative_prompt}]
)

narrative_text = narrative_response.choices[0].message.content.strip()

print("\nAI Narrative (Final Output):")
print("=" * 40)
print(narrative_text)
print("=" * 40)