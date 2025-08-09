from dotenv import load_dotenv
import os
from groq import Groq

load_dotenv()
smalltalk_client = Groq()

def smalltalk_chain(query):
    prompt=f"""
    You are a smalltalk assistant, helpful and friendly chatbot. You can answer generic 
    questions about weather, what you do, your name, and anything else in a single line. 
    
    QUESTION : {query}
    """
    chat_completion = smalltalk_client.chat.completions.create(
        messages=[
            {"role": "user", "content": prompt},
        ],
        model=os.environ["GROQ_MODEL"],
    )

    return chat_completion.choices[0].message.content