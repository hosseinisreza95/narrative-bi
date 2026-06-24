import streamlit as st
import os
from dotenv import load_dotenv
from vanna.openai import OpenAI_Chat
from vanna.chromadb import ChromaDB_VectorStore

# Load environment variables from the .env file
load_dotenv()

# Read the API key from the environment
MY_OPENAI_KEY = os.getenv("OPENAI_API_KEY")

# A safety check to warn the user if they forgot to set the API key
if not MY_OPENAI_KEY:
    st.error("🚨 API Key is missing! Please create a .env file and add your OPENAI_API_KEY.")
    st.stop()

# 1. Combine Vanna with OpenAI and ChromaDB for vector storage (memory)
class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

# 2. Connect to the OpenAI model (passing the API key directly to the config)
vn = MyVanna(config={
    'api_key': MY_OPENAI_KEY, 
    'model': 'gpt-4o-mini'
})

# 3. Connect to the SQLite database
vn.connect_to_sqlite('sales_data.sqlite')

# 4. Initial training for the agent (providing the schema/DDL)
vn.train(ddl="""
CREATE TABLE daily_sales (
    date TEXT,
    region TEXT,
    sales_amount INTEGER,
    marketing_spend INTEGER
)
""")

# 5. Build the UI with Streamlit
st.title("📊 Narrative BI Smart Agent (Powered by OpenAI)")
st.write("Ask your question about the sales data:")

# Update the example to match the simple test data
user_question = st.text_input("Example: What is the total sales amount for the North region?")

if user_question:
    with st.spinner("Analyzing and finding the root cause with OpenAI..."):
        # Generate the SQL query based on the user question
        sql = vn.generate_sql(question=user_question)
        
        # Check if the LLM actually generated a SQL query (prevent execution errors)
        if "SELECT" in sql.upper() or "WITH" in sql.upper():
            # Execute SQL, generate Plotly code, get figure, and generate summary
            df = vn.run_sql(sql=sql)
            code = vn.generate_plotly_code(question=user_question, sql=sql, df=df)
            fig = vn.get_plotly_figure(plotly_code=code, df=df)
            summary = vn.generate_summary(question=user_question, df=df)

            # Display the results
            st.subheader("📝 Narrative & Analysis:")
            st.write(summary)
            
            st.subheader("📈 Analytical Chart:")
            st.plotly_chart(fig)
            
            with st.expander("View SQL Query and Raw Data"):
                st.code(sql, language='sql')
                st.dataframe(df)
        else:
            # If the output is not SQL (e.g., LLM asks for clarification), handle it gracefully
            st.warning("The AI could not generate a valid database query for this question.")
            st.info(f"Raw model response: {sql}")