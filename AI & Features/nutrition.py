# VERY simple example — replace with rich database or API for accuracy.
INGREDIENT_DB = {
    "egg": {"cal": 70, "protein": 6, "carbs": 0.6, "fat": 5},
    "chicken breast (100g)": {"cal": 165, "protein": 31, "carbs": 0, "fat": 3.6},
    "rice (100g cooked)": {"cal": 130, "protein": 2.4, "carbs": 28, "fat": 0.3},
    # add more entries or use external API
}

def estimate_nutrition(ingredient_list):
    """
    ingredient_list: list or newline string of ingredient descriptions
    returns: dict totals
    """
    total = {"calories":0, "protein":0, "carbs":0, "fat":0}
    for ing in ingredient_list:
        # simple matching: find a key substring
        for k, v in INGREDIENT_DB.items():
            if k.split()[0].lower() in ing.lower():
                total["calories"] += v["cal"]
                total["protein"] += v["protein"]
                total["carbs"] += v["carbs"]
                total["fat"] += v["fat"]
                break
    return total
