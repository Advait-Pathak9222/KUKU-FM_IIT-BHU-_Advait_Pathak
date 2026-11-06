import os
import sys
from dotenv import load_dotenv
from sarvamai import SarvamAI

load_dotenv()

api_key = os.getenv("SARVAM_API_KEY")
if not api_key:
    print("Error: SARVAM_API_KEY is not set in environment or .env file", file=sys.stderr)
    sys.exit(1)

client = SarvamAI(api_subscription_key=api_key)

try:
    response = client.chat.completions(
        model="sarvam-105b-conversations",
        messages=[
            {"role": "user", "content": "Namaste, can you briefly introduce yourself in one sentence?"}
        ]
    )
    print(response.choices[0].message.content)
except Exception as e:
    print(f"API Error: {e}", file=sys.stderr)
    sys.exit(1)
