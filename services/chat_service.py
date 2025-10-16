from google import genai
from google.genai import types

from config.load_env import GOOGLE_API_KEY, GEMINI_MODEL
client = genai.Client(api_key=GOOGLE_API_KEY)


# 1. Define web search tool
grounding_tool = types.Tool(
    google_search=types.GoogleSearch()
)


def create_chat(medicine_information):
    chat = client.chats.create(
    model=GEMINI_MODEL,
    config=types.GenerateContentConfig(
            tools=[grounding_tool],
            system_instruction=f"Here are the patient prescription information: {medicine_information}"
        )
    )
    return chat



