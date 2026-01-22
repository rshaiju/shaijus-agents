from dotenv import load_dotenv
from google import genai

load_dotenv(override=True)

client = genai.Client()
response = client.models.generate_content(
    model="gemini-3-flash-preview", contents="Hello, how are you Gemini?"
)
print(response.text)