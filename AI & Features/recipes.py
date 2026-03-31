from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from models import Recipe, Favorite
from extensions import db
from ai_utils import generate_recipe
from nutrition import estimate_nutrition
import json

recipes_bp = Blueprint('recipes', __name__, url_prefix='/api/recipes')

@recipes_bp.route('/generate', methods=['POST'])
def generate():
    data = request.get_json() or {}
    ingredients = data.get('ingredients', [])
    prefs = data.get('preferences', {})
    if isinstance(ingredients, str):
        ingredients = [i.strip() for i in ingredients.splitlines() if i.strip()]
    ai_result = generate_recipe(ingredients, preferences=prefs)
    # if nutrition not in ai_result, estimate
    if not ai_result.get('nutrition'):
        ai_result['nutrition'] = estimate_nutrition(ingredients)
    # convert ingredients list to newline string if needed
    return jsonify({"success": True, "recipe": ai_result})

@recipes_bp.route('/save', methods=['POST'])
@login_required
def save_recipe():
    payload = request.get_json()
    title = payload.get('title','AI Recipe')
    ingredients = payload.get('ingredients','')
    directions = payload.get('directions','')
    nutrition = payload.get('nutrition',{})
    recipe = Recipe(title=title, ingredients=json.dumps(ingredients) if not isinstance(ingredients,str) else ingredients,
                    directions=directions, nutrition=nutrition, created_by=current_user.id)
    db.session.add(recipe)
    db.session.commit()
    return jsonify({"success": True, "recipe_id": recipe.id})

@recipes_bp.route('/favorite/<int:recipe_id>', methods=['POST'])
@login_required
def favorite(recipe_id):
    fav = Favorite(user_id=current_user.id, recipe_id=recipe_id)
    db.session.add(fav)
    db.session.commit()
    return jsonify({"success": True})
