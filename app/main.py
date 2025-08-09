import sys
import pysqlite3
sys.modules["sqlite3"] = pysqlite3

import streamlit as st
from router import router
from faq import ingest_faq_data, faq_chain
from sql import sql_chain
from smalltalk import smalltalk_chain
from pathlib import Path

faqs_path = Path(__file__).parent / "resources/faq.csv"
ingest_faq_data(faqs_path)

def ask(query):
    route = router(query).name
    print(route)
    if route == 'faq':
        ans = faq_chain(query)
    elif route == 'sql':
        ans = sql_chain(query)
    elif route == 'smalltalk':
        ans = smalltalk_chain(query)
    else:
        return f"route {route} not implemented yet."
    print(ans)
    return ans

st.title("Ecommerce Chatbot")
if "messages" not in st.session_state:
    st.session_state["messages"] = []
query = st.chat_input("Write your query:")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if query:
    with st.chat_message("user"):
        st.markdown(query)
    st.session_state.messages.append({"role": "user", "content": query})
    response = ask(query)
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content":response})
