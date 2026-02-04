import os
from google import genai
from google.genai import types # Import types for Config
from typing import Dict
from dotenv import load_dotenv
import json

load_dotenv()

# Initialize the client with the new SDK
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

async def analyze_and_reply(current_text: str, history: list) -> Dict[str, str]:
    """
    1. Detects if the message is a scam.
    2. If scam, generates a 'victim' response.
    3. If not scam, ignore it.
    """
    
    # We construct a prompt that gives the AI its 'Persona'
    # UPDATED: Added instruction for SHORT replies.
    system_prompt = f"""
    You are an AI Agent inside a HoneyPot designed to trap scammers. 
    
    INCOMING MESSAGE: "{current_text}"
    
    YOUR GOAL: 
    1. Analyze if this is a scam (Phishing, UPI fraud, Bank fraud).
    2. If it is NOT a scam, return status="safe".
    3. If it IS a scam, pretend to be a naive, non-tech-savvy victim (e.g., an elderly person).
    4. Keep the conversation going. Ask stupid questions. Waste their time.
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
        # Generate content
        # UPDATED: Added config to limit tokens
        response = await client.aio.models.generate_content(
            model='models/gemini-2.5-flash',
            contents=system_prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=60, # Limits length strictly
                temperature=0.7,
                response_mime_type="application/json" # Forces valid JSON
            )
        )
        
        # Parse the JSON response
        cleaned_text = response.text.strip()
        result = json.loads(cleaned_text)
        
        return result

    except Exception as e:
        print(f"AI Error: {e}")
        return {"is_scam": True, "reply": "I am confused. What do you mean?"}