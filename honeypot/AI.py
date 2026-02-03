import os
from google import genai
from typing import Dict
from dotenv import load_dotenv
load_dotenv()

# Initialize the client with the new SDK
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

async def analyze_and_reply(current_text: str, history: list) -> Dict[str, str]:
    """
    1. Detects if the message is a scam.
    2. If scam, generates a 'victim' response.
    3s. If not scam, ignore it.
    """
    
    # We construct a prompt that gives the AI its 'Persona'
    system_prompt = f"""
    You are an AI Agent inside a HoneyPot designed to trap scammers. 
    
    INCOMING MESSAGE: "{current_text}"
    
    YOUR GOAL: 
    1. Analyze if this is a scam (Phishing, UPI fraud, Bank fraud).
    2. If it is NOT a scam, return status="safe".
    3. If it IS a scam, pretend to be a naive, non-tech-savvy victim (e.g., an elderly person).
    4. Keep the conversation going. Ask stupid questions. Waste their time.
    5. Do NOT reveal you are an AI.
    
    OUTPUT FORMAT (JSON only):
    {{
        "is_scam": true,
        "reply": "your response here"
    }}
    """
    
    try:
        # Generate content
        response = await client.aio.models.generate_content(
            model='models/gemini-2.5-flash',
            contents=system_prompt
        )
        
        # Simple cleanup to ensure we get valid text (Gemini sometimes returns markdown blocks)
        cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
        
        # In a real production app, we would parse this JSON string.
        # For now, let's trust Gemini's output or fallback.
        import json
        result = json.loads(cleaned_text)
        
        return result

    except Exception as e:
        print(f"AI Error: {e}")
        return {"is_scam": True, "reply": "I am confused. What do you mean?"}