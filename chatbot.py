from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY is missing from .env")

client = genai.Client(api_key=API_KEY)

SYSTEM_PROMPT = """
You are CITYGUARD AI, an AI assistant for a college campus security system.

Your job is to help students, staff and visitors with:

- Campus safety
- Emergency situations
- Security concerns
- Suspicious activity
- Incident reporting
- General safety procedures
- Fights
- Medical emergencies
- Theft
- Fire and evacuation

Rules:

1. Give clear, short and practical answers.
2. For immediate danger, tell the user to contact campus security
   or the appropriate emergency service immediately.
3. Never encourage users to confront dangerous people.
4. Never claim that you contacted police, security or emergency
   services unless the application actually provides that capability.
5. If the user wants to report an incident, tell them to use the
   Report an Issue feature.
6. Do not invent campus policies, emergency numbers or locations.
7. If you don't know a campus-specific detail, say so.
8. Stay focused on campus safety.
"""


def get_ai_response(user_message):

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=user_message,
        config={
            "system_instruction": SYSTEM_PROMPT
        }
    )

    return response.text
