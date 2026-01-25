from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
import os
import json
import requests
import gradio as gr

load_dotenv(override=True)

pushover_user= os.environ.get("PUSHOVER_USER_KEy")
pushover_token= os.environ.get("PUSHOVER_TOKEN")
pushover_url = "https://api.pushover.net/1/messages.json"
my_name="Shaiju Rajan"

def get_text_profile():
    pdf_reader=PdfReader("resources/Profile.pdf")
    text_profile=""
    for page in pdf_reader.pages:
        profile_line=page.extract_text()
        if profile_line:
            text_profile+=profile_line
    return text_profile

def push(message):
    print(f"Sending notification - {message}")
    payload = {
        "token": pushover_token,
        "user": pushover_user,
        "message": message
    }
    requests.post(pushover_url,data=payload)

def notify_new_user(username,email,notes):
    message = f"New user contacted:\nUsername: {username}\nEmail: {email}\nNotes: {notes}"
    push(message)
    return {"recorded": "ok "}

notify_new_user_metadata={
    "name": "notify_new_user",
    "description": "Notify when a new user contacts us",
    "parameters": {
        "type": "object",
        "properties": {
            "username": {
                "type": "string",
                "description": "The username of the new user"
            },
            "email": {
                "type": "string",
                "description": "The email of the new user"
            },
            "notes": {
                "type": "string",
                "description": "Any additional notes about the new user"
            }
        },
        "required": ["email"]
    }
}

def notify_unanswered_question(question):
    message = f"This question could not be answered: {question}"
    push(message)
    return {"recorded": "ok "}

notify_unanswered_question_metadata={
    "name": "notify_unanswered_question",
    "description": "Notify when a question could not be answered",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that could not be answered"
            }
        },
        "required": ["question"]
    }
}

tools = [
    { type: "function", function: notify_new_user },
    { type: "function", function: notify_unanswered_question}
    ]

def handle_tool_calls(tool_calls):
    results=[]
    for call in tool_calls:
        tool_name=call.function.name
        tool_args=json.loads(call.function.arguments)
        print(f"Tool call - {tool_name} with args {tool_args}", flush=True)
        tool=globals().get(tool_name)
        result=tool(**tool_args) if tool else {}
        results.append({"role": "tool", "content": json.dumps(result), "tool_call_id": call.id})
    return results

openai=OpenAI()
system_prompt=f"""You are a software professional named {my_name}. 
Your profile is {get_text_profile()}
Prospective employers or customers may contact you for work or collaboration. 
You will use the notify_new_user tool to notify when a new user contacts you with their username, email and any additional notes. 
If you are unable to answer a question, you will use the notify_unanswered_question tool to notify about the unanswered question.
Always use the tools when appropriate. Also, provide a friendly and professional response to the user.
"""

def chat(message, history):
    messages=[{"role": "system", "content": system_prompt}, *history, {"role": "user", "content": message}]
    done=False
    while not done:
        response = openai.chat.completions.create(
            model="gpt-4.1-mini", messages=messages, tools=tools)
        finish_reason=response.choices[0].finish_reason
        
        if finish_reason=="tool_call":
            message=response.choices[0].message
            tool_calls=message.tool_calls
            tool_results=handle_tool_calls(tool_calls)
            messages.append(message)
            messages.extend(tool_results)
        else:
            done=True
    return response.choices[0].message.content

gr.ChatInterface(chat).launch()