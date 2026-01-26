from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
import json

todos=[]
completions=[]

load_dotenv(override=True)

def show(text):
    try:
        Console.print(text)
    except Exception as e:
        print(f"Error displaying text: {e}")

def get_todo_report()->str:
    result=""
    for index,todo in enumerate(todos):
        if (completions[index]):
            result+= f"ToDo #{index + 1}: [green][stike]{todo}[/strike][/green] \n"
        else:
             result+= f"ToDo #{index + 1}:{todo} \n"
    return result

def create_todos(descriptions:list[str])->str:
    todos.extend(descriptions)
    completions.extend([False]*len(descriptions))
    return get_todo_report()

def mark_todo_complete(index:int, completion_notes: str)->str:
    if index<1 or index>len(todos):
        return f"No ToDo at this index: {index}"
    completions[index-1]=True
    Console().print(completion_notes)
    return get_todo_report()

create_todos_metadata={
    "name": "create_todos",
    "description": "Create a list of ToDos from the given descriptions and return the full list",
    "parameters": {
        "type": "object",
        "properties": {
            "descriptions": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "List of ToDo descriptions to create"
            }
        },
        "required": ["descriptions"]
    }
}

mark_todo_complete_metadata={
    "name": "mark_todo_complete",
    "description": "Mark the ToDo at the given index as complete with completion notes and return the full list",
    "parameters": {
        "type": "object",
        "properties": {
            "index": {
                "type": "integer",
                "description": "The index of the ToDo to mark as complete (1-based index)"
            },
            "completion_notes": {
                "type": "string",
                "description": "Notes about the completion"
            }
        },
        "required": ["index", "completion_notes"]
    }   
}

tools = [
    { "type": "function", "function": create_todos_metadata },
    { "type": "function", "function": mark_todo_complete_metadata }
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

system_prompt="""You are a ToDo management assistant.
You will be given with a problem statement. You wll create a list of ToDos to solve the problem statement using the create_todos tool.
Once the ToDos are created, you will mark them as complete one by one using the mark_todo_complete tool with completion notes.
Make use of the tools. You can make assumptions if required. Don't ask for additional information. Just find the right ToDos yourself"""

message=""""
A train leaves Boston at 2:00 pm traveling 60 mph.
Another train leaves New York at 3:00 pm traveling 80 mph toward Boston.
When do they meet?
"""
messages=[
    {"role": "system", "content": system_prompt},   
    {"role": "user", "content": message}    
]

def manage_todos(messages):
    openai=OpenAI()
    done=False
    while not done:
        response=openai.chat.completions.create(
            model="gpt-4.1-mini", messages=messages, tools=tools)
        finish_reason=response.choices[0].finish_reason
        
        if finish_reason=="tool_calls":
            message=response.choices[0].message
            tool_calls=message.tool_calls
            tool_results=handle_tool_calls(tool_calls)
            messages.append(message)
            messages.extend(tool_results)
        else:
            done=True
    show(response.choices[0].message.content)

result=manage_todos(messages)
