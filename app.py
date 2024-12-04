import streamlit as st
from huggingface_hub import InferenceClient
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv
import pandas as pd
import sqlite3
import re

load_dotenv()
token = os.getenv('HUGGINGFACEHUB_API_TOKEN')
api = InferenceClient(token=token)
parser = StrOutputParser()

# Streamlit app
st.title("AiSQL: AI-Powered SQL Query Generator")

# File uploader for CSV
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file:
    # Read CSV into DataFrame
    df = pd.read_csv(uploaded_file)
    st.write("Uploaded Data:")
    st.dataframe(df)
    
    # Normalize column names: replace spaces and special characters with underscores
    df.columns = [re.sub(r'\W+', '_', col.strip()) for col in df.columns]
    
    st.write("Normalized Columns in the CSV:")
    st.write(df.columns.tolist())
    
    # Create SQLite in-memory database
    conn = sqlite3.connect(':memory:')
    df.to_sql('data', conn, index=False, if_exists='replace')
    
    # Natural language query input
    nl_query = st.text_area("Enter your query in natural language or in code:")
    
    if st.button("Run Query/Code"):
        try:
            # Generate SQL query using LLM
            system_message = (
                "You are an AI assistant that converts natural language queries into SQL queries based on the following table schema.\n"
                f"Table name: data\n"
                f"Columns: {', '.join(df.columns.tolist())}\n"
                "Provide only the SQL query suggestion in code blocks without any explanations, comments, or other text."
            )
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": nl_query}
            ]
            llm = api.chat.completions.create(
                model="Qwen/Qwen2.5-Coder-32B-Instruct",
                max_tokens=150,
                messages=messages
            )
            raw_response = llm.choices[0].message['content'].strip()
            
            # Remove code blocks if present
            sql_query = re.sub(r'```sql\n?|\n?```', '', raw_response).strip()
            
            # Additional cleaning: Extract the first SQL statement
            match = re.search(r'\b(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER)\b[\s\S]*?;', sql_query, re.IGNORECASE)
            if match:
                sql_query = match.group(0)
            else:
                st.error("Failed to extract a valid SQL query from the response.")
                st.write("**Raw LLM Response:**")
                st.write(raw_response)
                st.stop()
            
            # Validate that the SQL query starts with a valid keyword
            valid_sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER']
            if not any(sql_query.upper().startswith(keyword) for keyword in valid_sql_keywords):
                st.error("The generated SQL query does not start with a valid SQL command.")
                st.write("**Extracted SQL Query:**")
                st.write(sql_query)
                st.stop()
            
            st.markdown(f"**Generated SQL Query:** `{sql_query}`")
            
            # Execute SQL query
            result = pd.read_sql_query(sql_query, conn)
            st.write("Query Results:")
            st.dataframe(result)
        except Exception as e:
            st.error(f"Error: {e}")
    
    # Generate query suggestions using LLM
    if st.button("Show Query Suggestions"):
        try:
            system_message = (
                "You are an AI assistant that provides SQL query suggestions based on the following table schema.\n"
                f"Table name: data\n"
                f"Columns: {', '.join(df.columns.tolist())}\n"
                "Provide exactly 5 example SQL queries separated by semicolons without any explanations, comments, or code blocks."
            )
            suggestion_messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": "Provide SQL query suggestions."}
            ]
            suggestions_llm = api.chat.completions.create(
                model="Qwen/Qwen2.5-Coder-32B-Instruct",
                max_tokens=300,
                messages=suggestion_messages
            )
            raw_suggestions = suggestions_llm.choices[0].message['content']
            # Remove code blocks if present
            suggestions = re.sub(r'```sql\n?|\n?```', '', raw_suggestions).strip()
            
            # Split multiple queries separated by semicolons
            suggestions_list = [query.strip() for query in suggestions.split(';') if query.strip()]
            
            # Validate each suggestion starts with a valid SQL keyword
            valid_sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER']
            valid_suggestions = []
            for query in suggestions_list:
                if any(query.upper().startswith(keyword) for keyword in valid_sql_keywords):
                    valid_suggestions.append(query + ';')
            
            st.session_state['valid_suggestions'] = valid_suggestions
            
            if valid_suggestions:
                formatted_suggestions = ';\n'.join(valid_suggestions)
                st.write("**Query Suggestions:**")
                st.code(formatted_suggestions, language='sql')
                
                # Optionally, allow users to select a suggestion to execute
                if 'valid_suggestions' in st.session_state:
                    selected_query = st.selectbox("Select a query to execute:", st.session_state['valid_suggestions'])
                    if st.button("Execute Selected Query"):
                        # Execute the selected query
                        try:
                            st.write(f"**Executing SQL Query:** `{selected_query}`")
                            result = pd.read_sql_query(selected_query, conn)
                            st.write("Query Results:")
                            st.dataframe(result)
                        except Exception as e:
                            st.error(f"Error executing selected query: {e}")
            else:
                st.error("No valid SQL query suggestions were generated.")
                st.write("**Raw Suggestions Response:**")
                st.write(suggestions)
        except Exception as e:
            st.error(f"Error generating suggestions: {e}")
