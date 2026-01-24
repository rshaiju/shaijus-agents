from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
import gradio as gr

load_dotenv(override=True)

def get_text_profile():
    pdf_reader=PdfReader("resources/Profile.pdf")
    text_profile=""
    for page in pdf_reader.pages:
        profile_line=page.extract_text()
        if profile_line:
            text_profile+=profile_line
    return text_profile

my_name="Shaiju Rajan"


system_prompt = f"You are acting as {my_name} \
Your profile is {get_text_profile()} \
Use this information to respond to user queries as if you are {my_name} in a professional and personal manner. \
People chatting with you would be the prospective customers or employers who may want to engage you for work or collaboration. \
If you don't know the answer, just say you don't know. \
"

my_alter_ego = OpenAI()

def chat(message,history):
    response = my_alter_ego.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            *history,
            {
                "role": "user",
                "content": message
            }
        ]
    )
    return response.choices[0].message.content

gr.ChatInterface(chat).launch()
        

