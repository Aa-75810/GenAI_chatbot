# Extractor

from dotenv import load_dotenv

load_dotenv()  #load all variables

# Libraries
import mysql.connector
# import few_shot_prompt
import streamlit as st
import os
# from PIL import Image
import google.generativeai as gemini

# Connect to MySQL
def connect_to_database():
    return mysql.connector.connect(
        host='172.104.50.53',
        user='sa',
        password='P@ssword1',
        database='chat'
        )

# db = SQLDatabase.from_uri(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}",sample_rows_in_table_info=1,
#                           include_tables=['atm_master' ,'coffee_users', 'warehouse_master','city','orders','cricket_data'],
#                           custom_table_info={'warehouse':"Warehouse_Master"})    

# configure api_key

gemini.configure(api_key = os.getenv("gem_api"))

# function to load Gemini pro vision and provide queries 
def get_gemini_response(question, prompt):
    model = gemini.GenerativeModel(model_name="gemini-1.5-flash")
    print(question)
    response = model.generate_content([prompt[0], question])
    cleaned_response = response.text.replace("```sql", "").replace("```", "").strip()
    return cleaned_response


# Function to execute query from the database
def execute_query(sql_query):
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        
        cursor.execute(sql_query)
        print(sql_query)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
        return None
    

# table_info = ['atm_master' ,'coffee_users', 'warehouse_master','city','orders','cricket_data']
table_info = ['atm_master','audit', 'audit_type', 'holiday', 'object', 'page', "question", 
              'question_type', 'question_type_option', 'schedule_site', 'site', "template",
              'ticket', 'ticket_response', 'user_audit_schedule', 'users' ]

# Define Your Prompt
prompt = [
    """ You are an expert in converting English questions to SQL query!
    Given an input question, create a syntactically correct MySQL query to run.
    Unless otherwise specificed.\n\nHere is the relevant table info: {table_info}\n\nBelow are a number of examples of questions and their corresponding SQL queries.
    examples = [
    {
        "input": "give me details of sanjay gawatiya.",
        "query": "SELECT * FROM users WHERE first_name = 'sanjay' and last_name = 'Gawatiya';"
    },
    {
        "input": "give me details of user id 16.",
        "query": "select * from users where user_id = 16;"
    },
    {
        "input": "Show and give me the details or status of  ticket response of question id 71.",
        "query": "select * from ticket_response where question_id = 71;"
    },
    {
        "input": "Retrieve and give me the holiday id of 26 december",
        "query": "SELECT holiday_id FROM holiday WHERE holiday_date = '2023-12-26';;"
    },
    {
        "input" : "List all actions performed on the ticket table in the last 7 days",
        "query" : "SELECT * FROM ticket WHERE  'created_date' >= now();"
    },
    {
        "input": "List all products with a stock quantity less than 7000.",
        "query": "SELECT productName, quantityInStock FROM products WHERE quantityInStock < 7000;"
    },
    {
     'input':"Show all ticket changes along with user details`",
     "query": "SELECT * FROM ticket  t INNER JOIN users u ON t.user_id = u.user_id;"
    },
    {
    'input' : "which bank have maximum number of atm ? ",
    "query" : "Select bank from atm_master group by bank order by count(*) desc limit 1;"
    },
    {
        "input" : "Retrieve all user activities and data changes, along with the table details",
        "query" : "SELECT t.user_id, u.first_name, u.last_name, t.created_date, t.last_updated_date, t.status, a.audit_name FROM ticket t JOIN users u ON t.user_id = u.user_id LEFT JOIN audit a ON t.audit_id = a.audit_id where t.status= 'PENDING' ORDER BY t.created_date DESC;"
    },
    {
        "input" : "Retrieve all user activities and data changes, along with the table details.",
        "query" : "SELECT at.audit_type_id, at.last_updated_date , t.template_name, t.created_by FROM audit_type at RIGHT JOIN template t ON at.audit_type_id = t.audit_type_id where t.is_active = 0 ORDER BY t.created_date DESC;"
    }
    ]
    """
]

# def input_image_setup(upload_file):
#     if upload_file is not None:
#         # read the file
#         bytes_data = upload_file.getvalue()
#         image_parts =[
#             {
#                 "mime_type": upload_file.type ,
#                 "data" : bytes_data 
#             }
#         ]
#         return image_parts
#     else:
#         raise FileNotFoundError("No file uploaded")
    

# Streamlit App
st.set_page_config(page_title="I can Retrieve Any SQL query")
st.header("NLP2SQL")

question = st.text_input("Input: ", key="input")

submit = st.button("Ask the question")

# if submit is clicked
if submit:
    response = get_gemini_response(question, prompt)
    st.subheader("Generated SQL Query")
    st.code(response)
    
    query_result = execute_query(response)

    if query_result:
        st.subheader("Query Results")
        # Assuming the results are in the form of tuples
        for row in query_result:
            st.write(row)
    else:
        st.write("No results found.")
