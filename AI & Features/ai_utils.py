import os
import google.generativeai as genai

from config import Config

openai.api_key = Config.OPENAI_API_KEY

def generate_recipe(ingredients:list, preferences:dict=None, style:str="detailed"):
    """
    ingredients: list of ingredient strings
    preferences: dict e.g. {"diet":"vegan","calorie_target":600}
    returns: dict {title, ingredients, directions, notes}
    """
    prompt = f"""
You are a helpful gourmet chef and dietitian.
Create a {style} recipe using these ingredients: {', '.join(ingredients)}.
Include: title, ingredient list with quantities (estimate), step-by-step directions, and a short nutrition summary with rough calories and macros.
If user preferences are provided, follow them: {preferences}
Return the result as JSON with keys: title, ingredients, directions, nutrition.
"""
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # replace with preferred model
        messages=[{"role":"system","content":"You are a professional chef"},
                  {"role":"user","content":prompt}],
        temperature=0.8,
        max_tokens=800
    )
    text = resp['choices'][0]['message']['content']
    # Try parsing JSON; if model returned plain text, do a best-effort parsing.
    import json
    try:
        data = json.loads(text)
    except Exception:
        # naive split parsing (best-effort)
        data = {"title": "", "ingredients": "", "directions": "", "nutrition": {}}
        data["raw"] = text
    return data
