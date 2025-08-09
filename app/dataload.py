import pandas as pd
import sqlite3

conn = sqlite3.connect("resources/db.sqlite")

df = pd.read_csv("resources/flipkart_product_data.csv")

df.to_sql("product", conn, if_exists="replace", index=True)