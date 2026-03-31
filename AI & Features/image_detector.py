"""
Image-Based Ingredient Detection
=================================
Uses Gemini Vision API to identify food ingredients from uploaded images.
Returns structured data with ingredient names, confidence scores, and categories.
"""

import json
import os
import base64
from google import genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

# Models to try for vision tasks
VISION_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.5-flash",
    "gemini-2.0-flash-lite",
]

DETECTION_PROMPT = """
You are an expert food and ingredient recognition system.

Analyze this image and identify ALL food ingredients, produce, or cooking items visible.

For each detected item, provide:
1. **name** — the common English name of the ingredient (singular, lowercase)
2. **confidence** — your confidence that this item is correctly identified (0.0 to 1.0)
3. **category** — one of: Produce, Protein, Dairy, Grains, Spices, Condiments, Oils, Nuts, Fruits, Beverages, Other

RULES:
- Only identify clearly visible food items or ingredients.
- Do NOT identify containers, utensils, or non-food objects.
- If multiple of the same item exist, list it once.
- Be precise: "red bell pepper" not just "pepper".
- Confidence should reflect visual clarity: fully visible = 0.9+, partially obscured = 0.6-0.8, uncertain = 0.3-0.5.

OUTPUT FORMAT (JSON ONLY, NO extra text):
{
  "detected_items": [
    {"name": "tomato", "confidence": 0.95, "category": "Produce"},
    {"name": "chicken breast", "confidence": 0.88, "category": "Protein"}
  ],
  "total_count": 2,
  "scene_description": "Fresh ingredients laid out on a kitchen counter"
}
"""


def detect_ingredients(image_bytes, mime_type="image/jpeg"):
    """
    Detect food ingredients from an image using Gemini Vision.

    Args:
        image_bytes: Raw bytes of the uploaded image
        mime_type: MIME type of the image (image/jpeg, image/png, etc.)

    Returns:
        dict with 'detected_items', 'total_count', 'scene_description'
    """
    last_error = None

    for model_name in VISION_MODELS:
        try:
            print(f"📸 Detecting ingredients with {model_name}...")

            # Encode image to base64 for inline data
            b64_image = base64.b64encode(image_bytes).decode("utf-8")

            response = client.models.generate_content(
                model=model_name,
                contents=[
                    {
                        "role": "user",
                        "parts": [
                            {"text": DETECTION_PROMPT},
                            {
                                "inline_data": {
                                    "mime_type": mime_type,
                                    "data": b64_image
                                }
                            }
                        ]
                    }
                ]
            )

            raw_text = response.text.strip()
            # Clean markdown code fences
            raw_text = raw_text.replace("```json", "").replace("```", "").strip()

            result = json.loads(raw_text)

            # Validate structure
            if "detected_items" not in result:
                raise ValueError("Missing 'detected_items' in response")

            # Ensure all items have required fields
            validated_items = []
            for item in result.get("detected_items", []):
                validated_items.append({
                    "name": item.get("name", "unknown").strip().lower(),
                    "confidence": min(max(float(item.get("confidence", 0.5)), 0.0), 1.0),
                    "category": item.get("category", "Other")
                })

            # Sort by confidence descending
            validated_items.sort(key=lambda x: x["confidence"], reverse=True)

            result = {
                "detected_items": validated_items,
                "total_count": len(validated_items),
                "scene_description": result.get("scene_description", "Food ingredients detected")
            }

            print(f"✅ Detected {result['total_count']} ingredients with {model_name}")
            return result

        except Exception as e:
            last_error = str(e)
            print(f"⚠️ Vision detection failed with {model_name}: {last_error}")
            continue

    # All models failed
    print(f"❌ All vision models failed. Last error: {last_error}")
    return {
        "detected_items": [],
        "total_count": 0,
        "scene_description": f"Detection failed: {last_error}",
        "error": last_error
    }
