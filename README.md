# AiSQL: AI-Powered SQL Query Generator
## AiSQL is a Streamlit-based application that leverages an AI model to convert natural language queries into SQL queries. It allows users to upload a CSV file, generate SQL queries based on the data, and execute those queries to retrieve results. The application also provides SQL query suggestions based on the uploaded data.

## Features
**Upload CSV File: Users can upload a CSV file to analyze.**
**Natural Language to SQL: Convert natural language queries into SQL queries using an AI model.**
**Execute SQL Queries: Run the generated SQL queries on the uploaded data and display the results.**
**SQL Query Suggestions: Generate and display SQL query suggestions based on the uploaded data.**


## Requirements
```bash 
pip install -r requirements.txt
```
**Create a ```.env``` File:**

In the root directory of your project, create a file named ```.env```.
Add your Hugging Face API token to the ```.env``` file.

## Usage
```bash
streamlit run app.py
```
- **Upload a CSV File:**

Click on the "Upload a CSV file" button and select your CSV file.
The uploaded data will be displayed in a table format.
- **Run a Natural Language Query:**

Enter your query in plain English in the text area provided.
Click on the "Run Query/Code" button.
The application will generate an SQL query, execute it, and display the results.
- **Show Query Suggestions:**

Click on the "Show Query Suggestions" button.
The application will generate and display 5 SQL query suggestions based on the uploaded data.
- **Execute a Suggested Query:**

Select a query from the dropdown.
Click on the "Execute Selected Query" button.
The application will execute the selected query and display the results.
