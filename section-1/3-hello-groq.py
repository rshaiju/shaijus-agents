
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv(override=True)
import os
client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "user",
            "content": "Hello, how are you?"
        }
    ]
)
print(response.choices[0].message.content)