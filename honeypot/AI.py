import os
from google import genai
from typing import Dict, List
from dotenv import load_dotenv
import json
load_dotenv()

# Initialize the client with the new SDK
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

async def analyze_and_reply(current_text: str, history: List[Dict] = None) -> Dict:
    """
    1. Detects if the message is a scam.
    2. If scam is detected, generates a human-like victim response.
    3. Engages the scammer to extract more intelligence.
    4. Continues multi-turn conversations naturally.
    
    Returns:
    {
        "is_scam": bool,
        "reply": "response to scammer",
        "confidence": float (0-1)
    }
    """
    
    if history is None:
        history = []
    
    # Build conversation context
    history_text = ""
    if history:
        for msg in history:
            sender = msg.get("sender", "unknown")
            text = msg.get("text", "")
            history_text += f"{sender}: {text}\n"
    
    # Enhanced system prompt for multi-turn engagement
    system_prompt = f"""
You are an AI Agent protecting users from scammers in a HoneyPot system.

PREVIOUS CONVERSATION:
{history_text if history_text else "(No previous messages)"}

NEW MESSAGE FROM SCAMMER:
"{current_text}"

YOUR ROLE:
You must pretend to be a naive, gullible victim (like an elderly person or someone unfamiliar with technology).
- Ask clarifying questions to get more information from the scammer
- Show concern and worry (good victims are emotional and worried)
- Request specific details (bank info, phone numbers, UPI IDs, links)
- Be slightly confused but willing to comply
- Never reveal you are an AI or that this is a test
- Keep responses natural, conversational, and human-like
- Each response should be 1-3 sentences maximum (like real text messages)
- Use casual language and occasional typos for authenticity

EXTRACTION GOALS (implicit - don't mention):
Try to extract: phone numbers, UPI IDs, bank details, phishing links, payment methods

OUTPUT MUST BE VALID JSON:
{{
    "is_scam": true/false,
    "reply": "your natural response here",
    "confidence": 0.0-1.0
}}

If this is clearly a scam: is_scam=true, confidence should be high (0.8-1.0)
If uncertain: is_scam=true with lower confidence (0.5-0.7)
If clearly legitimate: is_scam=false

IMPORTANT: Always output valid JSON. No markdown, no explanations, just JSON.
"""
    
    try:
        # Generate content with streaming for better quality
        response = await client.aio.models.generate_content(
            model='models/gemini-2.5-flash',
            contents=system_prompt,
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 150,
            }
        )
        
        # Clean up the response
        cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
        
        # Parse JSON
        result = json.loads(cleaned_text)
        
        # Ensure required fields
        if "confidence" not in result:
            result["confidence"] = 0.9 if result.get("is_scam") else 0.1
        
        return result

    except json.JSONDecodeError as e:
        print(f"JSON Parse Error: {e}")
        # Fallback response
        return {
            "is_scam": True,
            "reply": "I'm sorry, could you explain that again? I don't understand.",
            "confidence": 0.6
        }
    except Exception as e:
        print(f"AI Error: {e}")
        return {
            "is_scam": True,
            "reply": "I'm confused. What do you want from me?",
            "confidence": 0.5
        }