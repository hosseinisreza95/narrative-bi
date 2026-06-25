import os
import json
import sqlite3
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

# Load Env Variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------------------------------------------------
# Call 1: Get SQL Query
# ---------------------------------------------------------
def get_sql_query(user_question, schema):
    prompt = f"""You are an Expert Data Architect.
    Database Schema: {schema}
    User Question: "{user_question}"
    
    Your task is to write a valid SQLite query to answer the question.
    You MUST respond with a valid JSON object matching this exact format:
    {{
        "sql": "SELECT ..."
    }}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={ "type": "json_object" },
        messages=[{"role": "user", "content": prompt}]
    )
    
    return json.loads(response.choices[0].message.content).get("sql", "")

# ---------------------------------------------------------
# Deterministic Python Engine
# ---------------------------------------------------------
def execute_query_safely(db_path, sql_query):
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query(sql_query, conn)
        return df, None
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()

def calculate_statistics(df):
    if df is None or df.empty:
        return {"status": "No data found"}
    
    stats = {"total_rows": len(df)}
    numeric_cols = df.select_dtypes(include='number').columns
    
    for col in numeric_cols:
        stats[f'sum_{col}'] = float(df[col].sum())
        stats[f'mean_{col}'] = float(df[col].mean())
        stats[f'max_{col}'] = float(df[col].max())
        
    return stats

# ---------------------------------------------------------
# Call 2: Generate Plotly Code (The Vanna Way)
# ---------------------------------------------------------
def generate_plotly_code(user_question, df):
    # We pass the column names and data types to the LLM so it knows what to plot
    df_info = df.dtypes.to_string()
    
    prompt = f"""You are an Expert Python Data Scientist.
    The user asked: "{user_question}"
    
    You have a pandas DataFrame named `df` with the following columns and data types:
    {df_info}
    
    Write Python code using `plotly.express` (imported as `px`) to create an insightful chart answering the user's question based on `df`.
    
    RULES:
    1. The final chart object MUST be assigned to a variable named `fig`.
    2. Do NOT import pandas or plotly (they are already imported).
    3. Return ONLY the raw Python code. Do NOT wrap it in markdown block quotes (like ```python).
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Strip markdown if the LLM accidentally includes it
    code = response.choices[0].message.content.strip()
    if code.startswith("```python"):
        code = code[9:]
    if code.startswith("```"):
        code = code[3:]
    if code.endswith("```"):
        code = code[:-3]
        
    return code.strip()

# ---------------------------------------------------------
# Call 3: Narrative Generation
# ---------------------------------------------------------
def generate_narrative_report(user_question, df, stats):
    prompt = f"""You are a top-tier Business Analyst advising a highly busy CEO.
    
    User Question: "{user_question}"
    
    Calculated Statistics:
    {json.dumps(stats, indent=2)}
    
    Sample Data (First 3 rows):
    {df.head(3).to_markdown() if df is not None else "No data"}
    
    YOUR TASK:
    Write a sharp, highly concise, and insightful executive summary (maximum 3 to 4 sentences).
    
    STRICT RULES:
    1. NO greetings, NO sign-offs, NO placeholders (like [Your Name], [Date], or [CEO]).
    2. NO formal structures or headers (Do NOT use words like "Introduction", "Conclusion", or "Summary").
    3. Start immediately with the direct answer to the user's question.
    4. Highlight the most important business driver, trend, or outlier based ONLY on the provided statistics.
    5. Be punchy, data-driven, and write in professional English.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content.strip()