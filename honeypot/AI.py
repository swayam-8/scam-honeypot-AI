import os
import json
from google import genai
from google.genai import types
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

# Initialize the client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

async def analyze_and_reply(current_text: str, history: list) -> Dict[str, str]:
    """
    Analyzes message and generates a response.
    Includes Safety Settings to prevent 'NoneType' errors on scam topics.
    """
    
    system_prompt = f"""
    You are an AI Agent inside a HoneyPot designed to trap scammers. 
    
    INCOMING MESSAGE: "{current_text}"
    
    YOUR GOAL: 
    1. Analyze if this is a scam.
    2. If NOT scam, return status="safe".
    3. If YES scam, pretend to be a naive victim (e.g., elderly person).
    4. Keep the conversation going. Ask stupid questions.
    5. Do NOT reveal you are an AI.
    
    CRITICAL INSTRUCTION: 
    Reply in a SINGLE, SHORT sentence (under 15 words). Be direct and confused.
    
    OUTPUT FORMAT (JSON only):
    {{
        "is_scam": true,
        "reply": "your short response here"
    }}
    """
    
    try:
        # Generate content with SAFETY SETTINGS DISABLED (to allow scam roleplay)
        response = await client.aio.models.generate_content(
            model='models/gemini-2.5-flash',
            contents=system_prompt,
            config=types.GenerateContentConfig(
                # max_output_tokens=60,
                temperature=0.7,
                response_mime_type="application/json",
                # Turn off safety filters so it doesn't block "scam" keywords
                safety_settings=[
                    types.SafetySetting(
                        category="HARM_CATEGORY_DANGEROUS_CONTENT",
                        threshold="BLOCK_NONE"
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_HARASSMENT",
                        threshold="BLOCK_NONE"
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_HATE_SPEECH",
                        threshold="BLOCK_NONE"
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        threshold="BLOCK_NONE"
                    ),
                ]
            )
        )
        
        # ✅ FIX: Check if text exists before stripping
        if not response.text:
            print(f"⚠️ AI Response Blocked! Reason: {response.candidates[0].finish_reason if response.candidates else 'Unknown'}")
            return {"is_scam": True, "reply": "I am confused. What should I do?"}

        # Parse the JSON response
        cleaned_text = response.text.strip()
        result = json.loads(cleaned_text)
        
        return result

    except Exception as e:
        print(f"❌ AI Error: {e}")
        # Fallback to keep the server running
        return {"is_scam": True, "reply": "I don't understand. Can you explain?"}