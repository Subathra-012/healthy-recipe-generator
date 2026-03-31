
# ----------------------------
# TRANSLATION ENDPOINT
# ----------------------------
@app.route("/translate", methods=["POST"])
def translate_content():
    try:
        data = request.json
        content = data.get("content")
        target_lang = data.get("language")
        
        if not content or not target_lang:
            return jsonify({"error": "Missing content or language"}), 400

        # Create a specialized prompt for translation
        translation_prompt = f"""
        You are a professional translator for a food application.
        Translate the following JSON content to Language Code: '{target_lang}'.
        
        RULES:
        1. Keep the JSON structure EXACTLY the same. Keys must NOT change.
        2. Only translate the VALUES (strings).
        3. Do NOT translate technical keys like 'calories', 'protein_g', 'calories_kcal'.
        4. Do NOT translate the 'image_search_query' or 'image_prompt'.
        5. Return valid JSON only.
        
        CONTENT TO TRANSLATE:
        {json.dumps(content)}
        """
        
        # Use a lightweight model for speed
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=translation_prompt
        )
        
        translated_text = response.text.replace("```json", "").replace("```", "").strip()
        translated_json = json.loads(translated_text)
        
        return jsonify({"data": translated_json})

    except Exception as e:
        print(f"Translation Error: {e}")
        return jsonify({"error": str(e)}), 500
