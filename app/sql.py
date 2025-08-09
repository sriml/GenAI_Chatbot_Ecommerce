import sqlite3
import os
import pandas as pd
from groq import Groq
from dotenv import load_dotenv
import re
from pathlib import Path

load_dotenv()

groq_model = os.getenv("GROQ_MODEL")
client_sql = Groq()

sql_prompt='''
you are an expert in understanding the database schema and generating SQL queries
 for a natural language question pertaining to the data you have. The schema is provided
 in the schema tags.
 <schema>
 table: product
 fields:
 product_link - string (hyperlink to the product)
 title - string (name of the product)
 brand - string (brand of the product)
 price - integer (price of the product in Indian Rupees)
 discount - float (discount on the product. 10% discount is represented as 0.1, 
 20% discount is represented as 0.2 etc.)
 avg_rating - float (average rating of the product. range 0-5 , 5 is the highest.)
 total_ratings - integer (total number of ratings for the product)
  </schema>
Make sure whenever you search for the brand name, the name can be in any case.
The field values in the database are non case sensitive.
So, make sure to use '%LIKE%' and all lower chars to find the condition. Never use "ILIKE".
create a single SQL query for the question provided. The query should have all the fields
in select clause. (i.e. select *)
Just the sql query, nothing more.
Always provide the SQL query in between <SQL> </SQL> tags.
'''

def generate_sql_query(question):
    chat_completion = client_sql.chat.completions.create(
        messages=[
            {"role": "system", "content": sql_prompt},
            {"role": "user", "content": question},
        ],
        model=os.environ["GROQ_MODEL"],
        temperature=0.2,
        max_tokens=1024
    )

    return chat_completion.choices[0].message.content

dbpath = Path(__file__).parent / "resources/db.sqlite"
def run_query(ans):
    query = re.search(r"<SQL>(.*?)</SQL>", ans, re.DOTALL).group(1)
    if query.strip().upper().startswith("SELECT"):
        with sqlite3.connect(dbpath) as conn:
            df = pd.read_sql_query(query, conn)
            return df

bkupcomprehension_prompt='''
You are provided with question and data.
QUESTION : All Spykar blue jeans in price range 1000 to 1500
DATA : [
{price: 1000, brand: "Spykar", title:"adfs"},
{price: 1300, brand: "Spykar", title:"adfs"},
{price: 1200, brand: "Spykar", title:"adfs"}
]
Generate the output in this format:
Spykar blue jeans : Rs. 1300 (35% off) , Rating: 4.4 <link>
Spykar blue jeans : Rs. 1200 (40% off) , Rating: 4.2 <link>

Do not write anything else.
'''
comprehension_prompt = """You are an expert in understanding the context of the question and replying based on the data pertaining to the question provided. You will be provided with QUESTION: and DATA:. The data will be in the form of an array or a dataframe or dict. Reply based on only the data provided as Data for answering the question asked as Question. Do not write anything like 'Based on the data' or any other technical words. Just a plain simple natural language response.
The Data would always be in context to the question asked. For example is the question is “What is the average rating?” and data is “4.3”, then answer should be “The average rating for the product is 4.3”. So make sure the response is curated with the question and data. Make sure to note the column names to have some context, if needed, for your response.
There can also be cases where you are given an entire dataframe in the Data: field. Always remember that the data field contains the answer of the question asked. All you need to do is to always reply in the following format when asked about a product: 
Product title, price in indian rupees, discount, and rating, and then product link. Take care that all the products are listed in list format, one line after the other. Not as a paragraph.
For example:
1. Campus Women Running Shoes: Rs. 1104 (35 percent off), Rating: 4.4 <link>
2. Campus Women Running Shoes: Rs. 1104 (35 percent off), Rating: 4.4 <link>
3. Campus Women Running Shoes: Rs. 1104 (35 percent off), Rating: 4.4 <link>

"""

def data_comprehension(question, context):
    chat_completion = client_sql.chat.completions.create(
        messages=[
            {"role": "system", "content": comprehension_prompt},
            {"role": "user", "content": f"QUESTION: {question} DATA: {context}"},
        ],
        model=os.environ["GROQ_MODEL"],
        temperature=0.2,
    )

    return chat_completion.choices[0].message.content

def sql_chain(query):
    response = generate_sql_query(query)
    result = run_query(response)
    context = result.to_dict(orient="records")
    answer = data_comprehension(query, context)
    return answer

if __name__ == "__main__":
    query = "All Spykar blue jeans in price range 1000 to 1500"
    answer = sql_chain(query)
    print(answer)
