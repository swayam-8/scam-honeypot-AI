import os
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Initialize Gemini API
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

async def analyze_and_reply(
    current_text: str, 
    history: Optional[List[Dict]] = None
) -> Dict:
    """
    Analyzes incoming message for scam indicators and generates appropriate response.
    
    Args:
        current_text: The message to analyze
        history: Previous conversation history
    
    Returns:
        Dictionary with:
        - is_scam: bool indicating if scam detected
        - reply: Human-like response to send
        - confidence: Confidence level (0-1)
    """
    
    if history is None:
        history = []
    
    # Build conversation context
    history_text = ""
    if history:
        for msg in history:
            sender = msg.get("sender", "Unknown")
            text = msg.get("text", "")
            history_text += f"{sender}: {text}\n"
    
    # System prompt for scam detection
    system_prompt = f"""You are an AI Agent in a HoneyPot system designed to detect and engage scammers.

CONVERSATION HISTORY:
{history_text if history_text else "(No previous messages)"}

NEW MESSAGE:
"{current_text}"

YOUR TASK:
1. Determine if this is a scam message
2. If it is, respond as a gullible victim to extract more information
3. Keep responses natural and short (1-2 sentences)

RESPONSE FORMAT (MUST BE VALID JSON):
{{
    "is_scam": true/false,
    "reply": "Your response here",
    "confidence": 0.0-1.0
}}

RULES:
- Never reveal you are an AI or this is a test
- Use casual language and occasional typos
- Ask clarifying questions to get more details
- Act worried/confused like a real victim
- Keep response under 50 words
- Output ONLY valid JSON, no other text"""
    
    try:
        # Use Gemini 1.5 Flash (stable, compatible model)
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={"temperature": 0.7, "max_output_tokens": 200}
        )
        
        response = model.generate_content(system_prompt)
        
        # Clean and parse response
        response_text = response.text.strip()
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        
        result = json.loads(response_text)
        
        # Validate result structure
        if "confidence" not in result:
            result["confidence"] = 0.9 if result.get("is_scam") else 0.1
        
        return result
        
    except json.JSONDecodeError:
        return {
            "is_scam": True,
            "reply": "Sorry, can you explain that again? I don't understand.",
            "confidence": 0.6
        }
    except Exception as e:
        print(f"AI Error: {e}")
        return {
            "is_scam": True,
            "reply": "What do you want? I'm confused.",
            "confidence": 0.5
        }
