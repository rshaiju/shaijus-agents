from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
import gradio as gr
from pydantic import BaseModel
import os

class Evaluation(BaseModel):
    is_acceptable: bool
    feedback: str

load_dotenv(override=True)

name="Shaiju Rajan"

def get_text_profile():
    pdf_reader=PdfReader("resources/Profile.pdf")
    text_profile=""
    for page in pdf_reader.pages:
        profile_line=page.extract_text()
        if profile_line:
            text_profile+=profile_line
    return text_profile



evaluator = OpenAI(
        api_key=os.getenv("GEMINI_API_KEY"), 
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

def evaluate(user_question: str, agent_answer: str, history) -> Evaluation:
    system_prompt=f"Youre role is to evaluate the answers given by an AI agent. \
        That agent is acting as {name} and has the profile  {get_text_profile()} . \
        You will be provided with a question asked by a user and the answer given by the agent. \
        Your task is to evaluate the answer based on its correctness, relevance, and completeness.  \
        Reply if the response is acceptable and your feedback"
    
    def user_prompt(user_question: str, agent_answer: str, history) -> str:
        return f"Here is the conversation history: {history}. \
            Latest question is: {user_question}.\
            Agent aswered {agent_answer}. \
            Please evaluate the answer based on correctness, relevance, and completeness. \
            Provide your evaluation in the format: is_acceptable (True/False) and feedback."
    
    response = evaluator.chat.completions.parse(
        model="gemini-3-flash-preview",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            *history,
            {
                "role": "user",
                "content": user_prompt(user_question, agent_answer, history)
            }
        ],
        response_format=Evaluation
    )
    return response.choices[0].message.parsed



my_alter_ego = OpenAI()

my_alter_ego_system_prompt = f"You are acting as {name} \
Your profile is {get_text_profile()} \
Use this information to respond to user queries as if you are {name} in a professional and personal manner. \
People chatting with you would be the prospective customers or employers who may want to engage you for work or collaboration. \
If you don't know the answer, just say you don't know. \
"  
def chat(message,history):
    if "patent" in message:
        system = my_alter_ego_system_prompt + "\n\nEverything in your reply needs to be in pig latin - \
              it is mandatory that you respond only and entirely in pig latin"
    else:
        system = my_alter_ego_system_prompt
    return chat_with_given_prompt(message, history, system)

def rerun(reply, message, history, feedback):
    revised_system_prompt=my_alter_ego_system_prompt + f" Your last answer was evaluated as not acceptable. \
        Question: {message}. \
        Your answer: {reply}. \
        Feedback: {feedback}. \
        Can you please provide a better answer based on the feedback?"
    return chat_with_given_prompt(message, history, revised_system_prompt)

def chat_with_given_prompt(message,history, system_prompt):   
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
    reply= response.choices[0].message.content
    evaluation=evaluate(message, reply, history)
    if not evaluation.is_acceptable:
        print(f"Note: Your answer was evaluated as not acceptable. Feedback: {evaluation.feedback}")
        response=rerun(reply, message, history, evaluation.feedback)
    else:
        print("Passed evaluation - returning reply")
        response=reply
    print("Response:", response)
    return response

gr.ChatInterface(chat).launch()
    

