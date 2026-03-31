import os
import json
import re
from google import genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY not found in environment variables.")
    exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)

MODELS = [
    "gemini-2.0-flash-lite-preview-02-05",
    "gemini-2.0-flash",
    "gemini-2.5-flash",
]

def create_translation_prompt(json_content, language):
    return f"""
You are a production-grade AI system responsible for multilingual content generation for a food and nutrition application.

INPUT:
You will receive:
- Structured recipe or meal plan data
- A language preference value:
  - "en" for English
  - "ta" for Tamil
  - "th" for Thanglish (Tamil written using English letters)

INPUT CONTENT (JSON):
{json.dumps(json_content, indent=2)}

TARGET LANGUAGE: {language}

TASK:
Return the SAME content translated into the selected language while preserving structure, meaning, and nutritional accuracy.

LANGUAGE RULES (STRICT):
1. English (en):
   Use clear, simple, professional English.
2. Tamil (ta):
   Use proper, natural Tamil. Avoid slang. Use commonly understood Tamil food terms.
3. Thanglish (th):
   Use Tamil sentence structure written in English letters. Simple, conversational.

STRUCTURE RULES (MANDATORY):
- Do NOT change keys, section names, or order
- Translate ONLY the values (text content)
- Numbers, units, and quantities must remain unchanged
- Nutrition data must not be altered

OUTPUT FORMAT (STRICT):
OUTPUT_START
LANGUAGE: {language}

TRANSLATED_CONTENT:
{{ ... same json structure ... }}

OUTPUT_END

IMPORTANT:
- Return ONLY the clean JSON for the content between OUTPUT_START and OUTPUT_END (but formatted as valid JSON).
"""

def test_translation():
    content = {
        "recipe_name": "Chicken Curry",
        "description": "A delicious and spicy chicken curry.",
        "ingredients": ["Chicken", "Onion", "Tomato", "Spices"]
    }
    language = "ta"
    
    prompt = create_translation_prompt(content, language)
    
    print(f"Testing translation to {language}...")
    
    for model_name in MODELS:
        try:
            print(f"🔄 Trying with {model_name}...")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            
            text = response.text.strip()
            print(f"Raw response length: {len(text)}")
            
            # Parse output
            json_match = re.search(r"TRANSLATED_CONTENT:\s*(\{.*\})", text, re.DOTALL)
            if not json_match:
                    json_match = re.search(r"\{.*\}", text, re.DOTALL)
                    
            if json_match:
                content_to_parse = json_match.group(1) if len(json_match.groups()) > 0 else json_match.group(0)
                print(f"Attempting to parse: {content_to_parse[:100]}...")
                try:
                    translated_json = json.loads(content_to_parse)
                    print(f"✅ Translation success with {model_name}")
                    print(json.dumps(translated_json, indent=2, ensure_ascii=False))
                    return
                except json.JSONDecodeError as je:
                    print(f"❌ JSON Decode Error: {je}")
                    print(f"Failed Content: {content_to_parse}")
            else:
                print(f"❌ Failed to parse JSON from {model_name}")
                print(f"Response start: {text[:100]}...")

        except Exception as e:
            print(f"⚠️ Error with {model_name}: {e}")

if __name__ == "__main__":
    test_translation()
