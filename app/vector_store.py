import sqlite3
import chromadb
from chromadb.config import Settings

def setup_vector_db(db_path):
    """Reads SQLite database and stores schemas in ChromaDB."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = cursor.fetchall()
    conn.close()

    schemas = []
    table_names = []
    for name, sql in tables:
        if sql:
            schemas.append(sql)
            table_names.append(name)

    # 💡 FIX: Use PersistentClient to avoid Streamlit cache/memory conflicts
    chroma_client = chromadb.PersistentClient(
        path="./chroma_db", 
        settings=Settings(anonymized_telemetry=False)
    )
    
    # 💡 FIX: Use get_or_create to safely load the existing database
    collection = chroma_client.get_or_create_collection(name="database_schemas")
    
    if schemas:
        # Only add documents if the collection is empty (prevents duplicates on reload)
        if collection.count() == 0:
            collection.add(
                documents=schemas,
                metadatas=[{"table": name} for name in table_names],
                ids=[f"table_{name}" for name in table_names]
            )
    return collection

def get_relevant_schema(collection, user_question):
    """Retrieves the most relevant table schema based on user question."""
    results = collection.query(query_texts=[user_question], n_results=1)
    if results['documents'] and results['documents'][0]:
        return results['documents'][0][0]
    return "No relevant schema found."