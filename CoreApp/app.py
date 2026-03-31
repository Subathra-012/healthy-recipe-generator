from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from google import genai
import json
import os
import re
import time
import datetime
import random
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

# Grocery Optimization System
from grocery_optimizer import GroceryOptimizer, optimize_grocery_list
from cost_estimator import CostEstimator, estimate_grocery_cost
from budget_tracker import BudgetTracker
from pantry_manager import PantryManager

# Image Detection
from image_detector import detect_ingredients

# ----------------------------
# LOAD ENV
# ----------------------------
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "super_secret_nutrigen_key")

# ----------------------------
# USER STORE (Simple JSON)
# ----------------------------
USERS_FILE = "users.json"

# OTP Store (in-memory for demo; use Redis in production)
OTP_STORE = {}  # key: email/mobile -> {otp, expires, verified}

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_user(email, password, name, mobile=""):
    users = load_users()
    if email in users:
        return False # User exists
    # Check duplicate mobile
    for u in users.values():
        if mobile and u.get("mobile") == mobile:
            return False
    users[email] = {
        "password": generate_password_hash(password),
        "name": name,
        "mobile": mobile,
        "email_verified": True,
        "mobile_verified": True,
        "login_history": []
    }
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)
    return True

def verify_user(email, password):
    users = load_users()
    if email in users and check_password_hash(users[email]["password"], password):
        # Create Session ID
        session_id = str(datetime.datetime.now().timestamp())
        
        # New Session Structure
        new_session = {
            "session_id": session_id,
            "login": datetime.datetime.now().isoformat(),
            "logout": None,
            "duration": 0,
            "features_used": []
        }
        
        if "login_history" not in users[email]:
            users[email]["login_history"] = []
            
        users[email]["login_history"].append(new_session)
        
        # Keep last 50
        users[email]["login_history"] = users[email]["login_history"][-50:]
        
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=4)
            
        user_data = users[email]
        user_data["current_session_id"] = session_id # Pass temporarily to session
        return user_data
    return None

def track_feature_usage(email, activity_description):
    """Updates the current active session with the specific activity"""
    users = load_users()
    if email in users and "login_history" in users[email] and users[email]["login_history"]:
        # Assume last session is active
        last_session = users[email]["login_history"][-1]
        
        if "features_used" not in last_session:
            last_session["features_used"] = []
            
        # Append specific activity (e.g. "Generated Recipe: Chicken")
        # Add timestamp to activity?
        timestamp = datetime.datetime.now().strftime("%H:%M")
        last_session["features_used"].append(f"[{timestamp}] {activity_description}")
        
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=4)

@app.route('/api/history', methods=['GET'])
def get_history():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    users = load_users()
    # Use stored email, fallback to searching by user dict
    email = session.get("email")
    print(f"📊 History request - session email: {email}, session keys: {list(session.keys())}")
    user = users.get(email) if email else None
    print(f"📊 User found: {user is not None}, history entries: {len(user.get('login_history', [])) if user else 'N/A'}")
    
    if not user and isinstance(session.get("user"), dict):
        # Fallback: search by name/password match
        print(f"📊 Fallback search by name: {session['user'].get('name')}")
        for e, udata in users.items():
            if udata.get("name") == session["user"].get("name"):
                user = udata
                session["email"] = e  # Cache for future
                email = e
                print(f"📊 Fallback matched: {e}, history: {len(udata.get('login_history', []))}")
                break
    
    if not user:
        print(f"📊 No user found for history!")
        return jsonify({"history": []})
        
    # Format history for frontend
    # Reverse to show newest first
    raw_history = user.get("login_history", [])[::-1] 
    formatted_history = []
    
    for sess in raw_history:
        if isinstance(sess, dict):
            # Calculate duration if not set (for current session)
            login_time = datetime.datetime.fromisoformat(sess["login"])
            duration = sess.get("duration", 0)
            
            # If duration is 0 and no logout, it's an active/unclosed session
            # Calculate live duration for active sessions
            if duration == 0 and not sess.get("logout"):
                duration = (datetime.datetime.now() - login_time).total_seconds()
            
            # Format Date/Time
            date_str = login_time.strftime("%Y-%m-%d")
            login_time_str = login_time.strftime("%I:%M %p")
            
            # Format Logout Time
            logout_raw = sess.get("logout")
            if logout_raw:
                logout_time = datetime.datetime.fromisoformat(logout_raw)
                logout_time_str = logout_time.strftime("%I:%M %p")
            else:
                logout_time_str = "Active"
            
            activities = sess.get("features_used", [])
            activity_str = ", ".join(activities) if activities else "Logged In"
            
            # Format Duration
            if duration >= 3600:
                dur_str = f"{int(duration // 3600)}h {int((duration % 3600) // 60)}m"
            elif duration > 60:
                dur_str = f"{int(duration // 60)}m {int(duration % 60)}s"
            else:
                dur_str = f"{int(duration)}s"
                
            formatted_history.append({
                "date": date_str,
                "login_time": login_time_str,
                "logout_time": logout_time_str,
                "duration": dur_str,
                "features": activity_str
            })
        elif isinstance(sess, str):
            # Legacy string entries (old format: just a timestamp string)
            try:
                login_time = datetime.datetime.fromisoformat(sess)
                formatted_history.append({
                    "date": login_time.strftime("%Y-%m-%d"),
                    "login_time": login_time.strftime("%I:%M %p"),
                    "logout_time": "N/A",
                    "duration": "N/A",
                    "features": "Logged In (Legacy)"
                })
            except:
                pass
            
    return jsonify({"history": formatted_history})

def calculate_stats(users, current_email):
    """Calculates dashboard stats"""
    user = users.get(current_email)
    if not user: return {"total_time": "0 mins", "accuracy": "95%"}
    
    total_seconds = 0
    history = user.get("login_history", [])
    
    for sess in history:
        # If logout exists, use it. If not, ignore or use a default session length?
        # Let's count only closed sessions or calculate active diff if logout missing?
        # For simplicity: use duration field if > 0
        if isinstance(sess, dict):
            dur = sess.get("duration", 0)
        else:
            dur = 0 # Skip legacy string entries
        total_seconds += dur
        
    # Format
    hours = int(total_seconds // 3600)
    mins = int((total_seconds % 3600) // 60)
    
    time_str = f"{hours}h {mins}m" if hours > 0 else f"{mins}m"
    
    return {
        "total_time": time_str,
        "accuracy": "98%" # Mock for now
    }

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise Exception("GEMINI_API_KEY missing in .env")

# ----------------------------
# GEMINI CLIENT
# ----------------------------
client = genai.Client(api_key=GEMINI_API_KEY)

# ----------------------------
# ----------------------------
# ----------------------------
# PROMPT ENGINEERING
# ----------------------------
def create_unified_prompt(mode, data):
    # Common fields
    diet_type = data.get("food_type") or data.get("diet_type") or "Standard"
    goal = data.get("goal", "Healthy Living")
    allergies = data.get("allergies", "None")
    ingredient = data.get("ingredient", "Any")
    
    # User Profile
    age = data.get("age", "30")
    gender = data.get("gender", "Any")
    height = data.get("height", "170")
    weight = data.get("weight", "70")
    
    # Mode Specific Instructions
    strict_instructions = ""
    # Check mode argument OR data flag
    if mode == "STRICT_INGREDIENTS" or data.get("strict_mode"):
        strict_instructions = """
        CRITICAL STRICT MODE RULES:
        1) You are FORBIDDEN from adding any new main ingredients. 
        2) You must NOT generate a recipe that requires buying extra primary ingredients (like meats, veg, grains) not listed.
        3) You MAY assume the user has basic pantry staples (Salt, Pepper, Oil, Water, basic Spices).
        4) If the provided ingredients are insufficient for a complete meal, generate a simple dish using ONLY what is available.
        5) The recipe name must reflect the provided ingredients.
        """

    # Cuisine & Dietary Filters
    cuisines = data.get("cuisines", [])
    dietary = data.get("dietary", [])
    filter_instructions = ""
    if cuisines:
        filter_instructions += f"\nCUISINE FOCUS: Generate recipes in the style of {', '.join(cuisines)} cuisine(s). Use authentic ingredients, techniques, and flavors from these traditions."
    if dietary:
        filter_instructions += f"\nDIETARY REQUIREMENTS: The recipe MUST strictly comply with these dietary requirements: {', '.join(dietary)}. Do NOT include any ingredient that violates these restrictions."

    return f"""
You are an AI-Powered Personal Chef and Certified Nutritionist.

INPUT USER PROFILE:
- Diet: {diet_type}
- Goal: {goal}
- Allergies: {allergies}
- Main Ingredient: {ingredient}
- Age/Gender: {age} / {gender}
- Height/Weight: {height}cm / {weight}kg
- Activity Level: {data.get('activity_level', 'Moderate')}
{filter_instructions}

IMPORTANT RULES:
1) Always follow the user’s diet preference and health goal strictly.
{strict_instructions}
2) Use only ingredients that match the user’s diet preference.
2) Use only ingredients that match the user’s diet preference.
3) If the user provides ingredients, prioritize them first.
4) Do NOT include any ingredient that violates the diet.
5) The output MUST be valid JSON only. Do not add extra text.

OUTPUT FORMAT (JSON ONLY):
{{
  "user": {{
    "diet_preference": "{diet_type}",
    "health_goal": "{goal}",
    "available_ingredients": ["{ingredient}"]
  }},
  "recipe": {{

    "name": "Recipe Name in its original/native language (if applicable)",
    "english_name": "Recipe Name ALWAYS in English (mandatory)",
    "servings": 2,
    "prep_time_minutes": 15,
    "cook_time_minutes": 20,
    "difficulty": "Easy",
    "ingredients": [
      {{ "item": "Ingredient Name", "quantity": "1 cup", "notes": "diced" }}
    ],
    "instructions": [
      "Step 1...",
      "Step 2..."
    ],
    "cooking_tips": [
        "Tip 1...", "Tip 2..."
    ],
    "nutrition": {{
      "calories_kcal": 500,
      "protein_g": 30,
      "carbs_g": 40,
      "fat_g": 15,
      "fiber_g": 5,
      "sugar_g": 2,
      "sodium_mg": 200
    }}
    }}
  }},
   "meal_plan_7_days": {{
      "Day_1": {{ "Breakfast": "...", "Lunch": "...", "Dinner": "...", "daily_nutrition": {{ "Calories": "2000", "Protein_g": "150", "Carbs_g": "200", "Fat_g": "70" }} }},
      "Day_2": {{ "Breakfast": "...", "Lunch": "...", "Dinner": "...", "daily_nutrition": {{ "Calories": "2000", "Protein_g": "150", "Carbs_g": "200", "Fat_g": "70" }} }},
      "Day_3": {{ "Breakfast": "...", "Lunch": "...", "Dinner": "...", "daily_nutrition": {{ "Calories": "2000", "Protein_g": "150", "Carbs_g": "200", "Fat_g": "70" }} }},
      "Day_4": {{ "Breakfast": "...", "Lunch": "...", "Dinner": "...", "daily_nutrition": {{ "Calories": "2000", "Protein_g": "150", "Carbs_g": "200", "Fat_g": "70" }} }},
      "Day_5": {{ "Breakfast": "...", "Lunch": "...", "Dinner": "...", "daily_nutrition": {{ "Calories": "2000", "Protein_g": "150", "Carbs_g": "200", "Fat_g": "70" }} }},
      "Day_6": {{ "Breakfast": "...", "Lunch": "...", "Dinner": "...", "daily_nutrition": {{ "Calories": "2000", "Protein_g": "150", "Carbs_g": "200", "Fat_g": "70" }} }},
      "Day_7": {{ "Breakfast": "...", "Lunch": "...", "Dinner": "...", "daily_nutrition": {{ "Calories": "2000", "Protein_g": "150", "Carbs_g": "200", "Fat_g": "70" }} }}
  }},
  "grocery_list": {{
      "Produce": ["Item 1", "Item 2"],
      "Protein": ["Item 3"]
  }}
}}
"""

def parse_generated_output(text):
    data = {}
    try:
        # Clean markdown code blocks if present
        text = text.replace("```json", "").replace("```", "").strip()
        
        # Parse JSON
        parsed = json.loads(text)
        
        # MAP TO LEGACY FORMAT (for Frontend Compatibility)
        
        # 1. Recipe Basics
        recipe = parsed.get("recipe", {})
        # Use english_name as the primary display name to avoid non-English titles
        eng_name = recipe.get("english_name", "")
        original_name = recipe.get("name", "Unknown Recipe")
        data["recipe_name"] = eng_name if eng_name else original_name
        data["original_name"] = original_name
        data["intro"] = f"A delicious {recipe.get('difficulty', 'Easy')} meal ready in {recipe.get('total_time_minutes', 30)} minutes."
        data["prep_time"] = f"{recipe.get('prep_time_minutes', 0)} mins"
        data["servings"] = recipe.get("servings", 2)
        # 2. Image Prompt - PROGRAMMATIC CONSTRUCTION (Reliable)
        rec_name = recipe.get("name", "Delicious Food")
        eng_name = recipe.get("english_name", rec_name) # Fallback to name if english_name missing
        data["english_name"] = eng_name # Explicitly send to frontend
        
        # Generate Keywords for Fallback (Cleaner than full prompt)
        # Remove non-alphanumeric chars for safety
        safe_name = re.sub(r'[^\w\s]', '', eng_name)
        keywords = [w for w in safe_name.split() if len(w) > 3][:3]
        data["image_keywords"] = ", ".join(keywords)
        
        # Construct the prompt
        # User defined professional prompt
        constructed_prompt = f"A high-resolution, professional food photography shot of {eng_name}. The dish is steaming hot, arranged beautifully on a ceramic plate. Soft, natural morning sunlight from a side window creates gentle shadows. Shallow depth of field with a blurred kitchen background. 8k resolution, cinematic lighting, hyper-realistic textures."
        
        print(f"🎯 Constructed Image Prompt: {constructed_prompt}")
        data["image_search_query"] = constructed_prompt

        # 3. Nutrition
        nutrients = recipe.get("nutrition", {})
        data["nutrients"] = {
            "calories": nutrients.get("calories_kcal", 0),
            "protein": nutrients.get("protein_g", 0),
            "carbs": nutrients.get("carbs_g", 0),
            "fat": nutrients.get("fat_g", 0),
            "fiber": nutrients.get("fiber_g", 0),
            "sugar": nutrients.get("sugar_g", 0),
            "sodium": nutrients.get("sodium_mg", 0)
        }
        
        # 4. Ingredients (Convert objects to strings for frontend list)
        data["ingredients"] = []
        for ing in recipe.get("ingredients", []):
            item = ing.get("item", "")
            qty = ing.get("quantity", "")
            data["ingredients"].append(f"{item} : {qty}")
            
        # 5. Instructions
        data["cooking_steps"] = recipe.get("instructions", [])
        
        # 6. Tips
        data["tips"] = recipe.get("cooking_tips", [])
        
        # 7. Weekly Plan (Direct Map)
        data["schedule"] = parsed.get("meal_plan_7_days", {})
        data["grocery"] = parsed.get("grocery_list", {})
        
        # 8. Visualization (Calculate on fly if missing)
        p = data["nutrients"]["protein"]
        c = data["nutrients"]["carbs"]
        f = data["nutrients"]["fat"]
        total_cals = (p*4) + (c*4) + (f*9)
        
        def safe_pct(val, total): return round(val/total*100) if total > 0 else 0
        
        data["macros"] = {
            "protein": {"grams": p, "percent": safe_pct(p*4, total_cals)},
            "carbs": {"grams": c, "percent": safe_pct(c*4, total_cals)},
            "fat": {"grams": f, "percent": safe_pct(f*9, total_cals)}
        }
        data["calories"] = {
            "total": data["nutrients"]["calories"],
            "dailyLimit": 2000
        }
        
        data["nutrition_viz"] = {
            "calories": {"consumed": data["nutrients"]["calories"], "target": 2000, "percentUsed": safe_pct(data["nutrients"]["calories"], 2000)},
            "macros": data["macros"]
        }

    except Exception as e:
        print(f"Error parsing JSON output: {e}")
        print(f"Raw text was: {text[:500]}...")
    
    return data

# ----------------------------
# ROUTES
# ----------------------------
@app.route("/")
def login():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/signup")
def signup():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return render_template("signup.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("index.html")

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    
    user = verify_user(email, password)
    if user:
        session["user"] = user
        session["email"] = email  # Store email separately for history lookups
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Invalid email or password"}), 401

@app.route("/api/signup", methods=["POST"])
def api_signup():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")
    mobile = data.get("mobile", "")
    
    if save_user(email, password, name, mobile):
        session["user"] = {"name": name, "password": generate_password_hash(password)}
        session["email"] = email
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Email or mobile already registered"}), 400


# ----------------------------
# OTP VERIFICATION ROUTES
# ----------------------------
@app.route("/api/send-email-otp", methods=["POST"])
def send_email_otp():
    email = request.json.get("email", "").strip()
    if not email or "@" not in email:
        return jsonify({"success": False, "error": "Invalid email"}), 400
    # Check if email already registered
    users = load_users()
    if email in users:
        return jsonify({"success": False, "error": "Email already registered"}), 400
    otp = str(random.randint(100000, 999999))
    OTP_STORE[f"email:{email}"] = {"otp": otp, "expires": time.time() + 300, "verified": False}
    # In production, send via email service (SendGrid, SES, etc.)
    print(f"📧 Email OTP for {email}: {otp}")
    return jsonify({"success": True, "message": "OTP sent", "debug_otp": otp})

@app.route("/api/verify-email-otp", methods=["POST"])
def verify_email_otp():
    email = request.json.get("email", "").strip()
    otp = request.json.get("otp", "").strip()
    key = f"email:{email}"
    record = OTP_STORE.get(key)
    if not record:
        return jsonify({"success": False, "error": "OTP expired or not sent"}), 400
    if time.time() > record["expires"]:
        return jsonify({"success": False, "error": "OTP expired"}), 400
    if record["otp"] == otp:
        OTP_STORE[key]["verified"] = True
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Invalid OTP"}), 400

@app.route("/api/send-mobile-otp", methods=["POST"])
def send_mobile_otp():
    mobile = request.json.get("mobile", "").strip()
    if not mobile or len(mobile) < 8:
        return jsonify({"success": False, "error": "Invalid mobile number"}), 400
    # Check if mobile already registered
    users = load_users()
    for u in users.values():
        if u.get("mobile") == mobile:
            return jsonify({"success": False, "error": "Mobile already registered"}), 400
    otp = str(random.randint(100000, 999999))
    OTP_STORE[f"mobile:{mobile}"] = {"otp": otp, "expires": time.time() + 300, "verified": False}
    # In production, send via SMS service (Twilio, etc.)
    print(f"📱 Mobile OTP for {mobile}: {otp}")
    return jsonify({"success": True, "message": "OTP sent", "debug_otp": otp})

@app.route("/api/verify-mobile-otp", methods=["POST"])
def verify_mobile_otp():
    mobile = request.json.get("mobile", "").strip()
    otp = request.json.get("otp", "").strip()
    key = f"mobile:{mobile}"
    record = OTP_STORE.get(key)
    if not record:
        return jsonify({"success": False, "error": "OTP expired or not sent"}), 400
    if time.time() > record["expires"]:
        return jsonify({"success": False, "error": "OTP expired"}), 400
    if record["otp"] == otp:
        OTP_STORE[key]["verified"] = True
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Invalid OTP"}), 400

# login_history route removed — consolidated into get_history above

@app.route("/api/stats")
def dashboard_stats():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    users = load_users()
    # Need email to lookup. 
    # Current session['user'] object might stick around, assume we stored email in it? 
    # Wait, verify_user saves whole user dict to session. User dict logic in save_user:
    # does NOT include email inside the dict value, it's the key.
    # FIX: We need to ensure we know the email.
    
    # Checking session structure:
    # api_login -> session["user"] = user (which is users[email])
    # users[email] = { password, name, login_history... }
    # It does NOT have email field inside.
    
    # We need to find the user again or rely on name/pass.
    current_data = session["user"]
    current_email = None
    
    # Inefficient lookup, but necessary given current design
    for e, u in users.items():
        if u.get("name") == current_data.get("name") and u.get("password") == current_data.get("password"):
            current_email = e
            break
            
    if not current_email:
        return jsonify({"total_time": "0m", "accuracy": "100%"})

    stats = calculate_stats(users, current_email)
    return jsonify(stats)

@app.route("/logout")
def logout():
    # Update logout time if possible
    if "user" in session:
        try:
            users = load_users()
            current_data = session["user"]
            current_email = None
            
            # Find email
            for e, u in users.items():
                if u.get("name") == current_data.get("name") and u.get("password") == current_data.get("password"):
                    current_email = e
                    break
            
            if current_email and "login_history" in users[current_email] and users[current_email]["login_history"]:
                last_session = users[current_email]["login_history"][-1]
                
                # If session_id matches (optional check), update logout
                # Only update if logout is None
                if not last_session.get("logout"):
                    now = datetime.datetime.now()
                    last_session["logout"] = now.isoformat()
                    
                    # Calculate duration
                    login_time = datetime.datetime.fromisoformat(last_session["login"])
                    duration = (now - login_time).total_seconds()
                    last_session["duration"] = int(duration)
                    
                    with open(USERS_FILE, 'w') as f:
                        json.dump(users, f, indent=4)
        except Exception as e:
            print(f"Logout Error: {e}")

    session.pop("user", None)
    return redirect(url_for("login"))

# ----------------------------
# CACHE & CONFIG
# ----------------------------
RECIPE_CACHE = {}
# Try various model names including experimental and standard ones
# Try various model names including experimental and standard ones
MODELS = [
    "gemini-2.5-flash-lite",
    "gemini-flash-latest",
    "gemini-2.0-flash-lite-preview-02-05",
    "gemini-2.0-flash",
    "gemini-2.5-flash",
]

@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.json
        
        # Track Usage
        # Find email again (reused logic, ideally refactor to get_current_email helper)
        if "user" in session:
             # Quick Hack: Pass tracking asynchronously or just do it here
             # We need to look up email to save to file.
             # For speed, let's look up once.
             users = load_users()
             c_data = session["user"]
             for e, u in users.items():
                if u.get("name") == c_data.get("name"):
                    # Detailed History Log
                    desc = f"Recipe: {data.get('ingredient', 'General')} ({data.get('goal', 'Any')})"
                    if data.get("strict_mode"):
                         desc = f"Cook Now: {data.get('strict_ingredients', 'Items')}"
                         
                    track_feature_usage(e, desc)
                    break

        # Map frontend "all_features" (gourmet) to something if needed, but the new prompt is strict.
        # We pass the whole data object to the unified prompt
        
        # 1. Check Cache (Construct key from relevant fields)
        food_type = data.get("food_type", "")
        ingredient = data.get("ingredient", "")
        goal = data.get("goal", "")
        
        cache_key = f"RECIPE_{food_type}_{ingredient}_{goal}".lower()
        if cache_key in RECIPE_CACHE:
            print(f"⚡ CACHE HIT: {cache_key}")
            return jsonify(RECIPE_CACHE[cache_key])

        if data.get("strict_mode"):
            prompt = create_unified_prompt("STRICT_INGREDIENTS", data)
        else:
            prompt = create_unified_prompt("RECIPE", data)
        
        last_error = "No models available"
        
        # 2. Try Models in Sequence with auto-retry on rate limits
        import random
        # Create a copy and shuffle to distribute load, but keep preferred models if needed?
        # Actually randomizing the whole list (except maybe the first one if we really want a specific one) is good for now.
        model_queue = MODELS[:]
        random.shuffle(model_queue)
        
        for model_name in model_queue:
            retries = 0
            max_retries = 1  # Reduced from 2 to 1 to fail faster
            
            while retries <= max_retries:
                try:
                    print(f"🤖 Requesting {model_name}... (attempt {retries + 1})")
                    
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt
                    )

                    response_text = response.text.strip()

                    # Parse with new parser
                    result = parse_generated_output(response_text)
                    
                    if not result or not result.get("recipe_name"):
                         raise Exception("Failed to parse valid recipe data")

                    # Update Cache
                    RECIPE_CACHE[cache_key] = result
                    print(f"✅ Success with {model_name}")
                    return jsonify(result)

                except Exception as e:
                    error_msg = str(e)
                    print(f"⚠️ Error with {model_name}: {error_msg}")
                    last_error = error_msg
                    
                    if ("429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg) and retries < max_retries:
                        # Parse retry delay from error message
                        retry_match = re.search(r'retry in (\d+\.?\d*)', error_msg, re.IGNORECASE)
                        wait_time = float(retry_match.group(1)) + 1 if retry_match else 5 
                        wait_time = min(wait_time, 10)  # Cap at 10s (Reduced from 40s)
                        
                        print(f"⏳ Rate limited. Waiting {wait_time:.0f}s before retry...")
                        time.sleep(wait_time)
                        retries += 1
                    else:
                        break  # Move to next model

        # If we get here, all models failed
        print(f"❌ All models failed. Last error: {last_error}")
        return jsonify({"error": f"Recipe generation failed. System is busy or overloaded. ({last_error})"}), 503


    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
             return jsonify({"error": "All AI models are busy! Please wait a minute."}), 429
        print(f"General Error: {e}")
        return jsonify({"error": str(e)}), 500

# ----------------------------
# DISH NAME RECIPE GENERATOR
# ----------------------------
@app.route("/generate_dish", methods=["POST"])
def generate_dish():
    """Generate a complete recipe for any dish name — universal recipe generator."""
    try:
        data = request.json
        dish_name = data.get("dish_name", "").strip()

        if not dish_name or len(dish_name) < 2:
            return jsonify({"error": "Please enter a valid dish name."}), 400

        # Track Usage
        if "user" in session:
            users = load_users()
            c_data = session["user"]
            for e, u in users.items():
                if u.get("name") == c_data.get("name"):
                    track_feature_usage(e, f"Dish Search: {dish_name}")
                    break

        # Check Cache
        cache_key = f"DISH_{dish_name}".lower().replace(" ", "_")
        if cache_key in RECIPE_CACHE:
            print(f"⚡ CACHE HIT: {cache_key}")
            return jsonify(RECIPE_CACHE[cache_key])

        # Specialized dish-name prompt
        prompt = f"""
You are a world-class professional chef and recipe expert. Generate a complete, authentic recipe for the dish: "{dish_name}".

IMPORTANT RULES:
1) Recognize the dish correctly — it can be ANY cuisine, category, or type (dessert, snack, fast food, main course, breakfast, beverage, etc.)
2) Provide the authentic, traditional version of this dish with accurate ingredients and measurements.
3) The recipe must be complete and ready to cook with no missing steps.
4) Do NOT add health restrictions — this is a universal recipe generator, not a diet planner.
5) If the dish name is completely invalid or unrecognizable as food, return {{"error": "Could not recognize this as a valid dish name."}}.
6) The output MUST be valid JSON only. Do NOT add any extra text before or after the JSON.

OUTPUT FORMAT (JSON ONLY):
{{
  "recipe": {{
    "name": "{dish_name}",
    "english_name": "English Name of the Dish",
    "category": "Dessert / Main Course / Snack / Appetizer / Beverage / etc.",
    "cuisine": "Italian / Indian / American / Japanese / etc.",
    "servings": 2,
    "prep_time_minutes": 15,
    "cook_time_minutes": 30,
    "difficulty": "Easy / Medium / Hard",
    "ingredients": [
      {{ "item": "Ingredient Name", "quantity": "1 cup", "notes": "optional notes" }}
    ],
    "instructions": [
      "Step 1: Detailed instruction...",
      "Step 2: Detailed instruction..."
    ],
    "cooking_tips": [
      "Pro tip 1...",
      "Pro tip 2..."
    ],
    "nutrition": {{
      "calories_kcal": 500,
      "protein_g": 20,
      "carbs_g": 60,
      "fat_g": 25,
      "fiber_g": 3,
      "sugar_g": 15,
      "sodium_mg": 300
    }}
  }}
}}
"""

        last_error = "No models available"
        import random
        model_queue = MODELS[:]
        random.shuffle(model_queue)

        for model_name in model_queue:
            retries = 0
            max_retries = 1

            while retries <= max_retries:
                try:
                    print(f"🍽️ Dish Search: '{dish_name}' → {model_name} (attempt {retries + 1})")

                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt
                    )

                    response_text = response.text.strip()
                    result = parse_generated_output(response_text)

                    if not result or not result.get("recipe_name"):
                        raise Exception("Failed to parse valid dish recipe data")

                    # Update Cache
                    RECIPE_CACHE[cache_key] = result
                    print(f"✅ Dish recipe generated: {dish_name}")
                    return jsonify(result)

                except Exception as e:
                    error_msg = str(e)
                    print(f"⚠️ Error with {model_name}: {error_msg}")
                    last_error = error_msg

                    if ("429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg) and retries < max_retries:
                        retry_match = re.search(r'retry in (\d+\.?\d*)', error_msg, re.IGNORECASE)
                        wait_time = float(retry_match.group(1)) + 1 if retry_match else 5
                        wait_time = min(wait_time, 10)
                        print(f"⏳ Rate limited. Waiting {wait_time:.0f}s...")
                        time.sleep(wait_time)
                        retries += 1
                    else:
                        break

        print(f"❌ All models failed for dish: {dish_name}. Last error: {last_error}")
        return jsonify({"error": f"Recipe generation failed. Please try again. ({last_error})"}), 503

    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            return jsonify({"error": "AI models are busy! Please wait a minute."}), 429
        print(f"Dish Gen Error: {e}")
        return jsonify({"error": str(e)}), 500


# ----------------------------
# WEEKLY PLAN GENERATOR
# ----------------------------
# Legacy parsers removed.


@app.route("/generate_plan", methods=["POST"])
def generate_plan():
    data = request.json
    print("Received Plan Request:", data)
    
    # Track Usage
    if "user" in session:
            users = load_users()
            c_data = session["user"]
            for e, u in users.items():
                if u.get("name") == c_data.get("name"):
                    info = f"Weekly Plan: {data.get('goal', 'General')} - {data.get('preference', 'Standard')}"
                    track_feature_usage(e, info)
                    break

    prompt = create_unified_prompt("WEEKLY_PLAN", data)
    
    last_error = None
    
    # Try multiple models
    plan_models = [
        "gemini-2.0-flash-lite", 
        "gemini-flash-latest", 
        "gemini-2.0-flash", 
        "gemini-2.5-flash",
        "gemini-pro-latest"
    ]
    
    for base_name in plan_models:
        variations = [base_name, f"models/{base_name}"]
        for model_name in variations:
            try:
                print(f"🤖 Generating Full Plan with {model_name}...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )

                full_text = response.text.strip()
                print(f"📄 Full Response Generated ({len(full_text)} chars)")
                
                # Parse
                parsed_data = parse_generated_output(full_text)
                
                if not parsed_data or not parsed_data.get("schedule"):
                     raise Exception("Failed to parse valid plan data")
                
                # ── Grocery Optimization Pipeline ──
                raw_grocery = parsed_data.get("grocery", {})
                if raw_grocery:
                    try:
                        optimized = optimize_grocery_list(raw_grocery)
                        optimized = estimate_grocery_cost(optimized)
                        
                        # Budget check if set in session
                        budget_tracker = BudgetTracker(session)
                        budget_status = budget_tracker.check_budget(
                            optimized.get('cost_summary', {}).get('total', 0)
                        )
                        optimized['budget_status'] = budget_status
                        
                        # Pantry deduction if enabled
                        pantry_mgr = PantryManager(session)
                        if pantry_mgr.get_inventory():
                            pantry_result = pantry_mgr.deduct_from_list(optimized)
                            optimized = pantry_result['adjusted_list']
                            optimized['pantry_deductions'] = pantry_result['deductions']
                        
                        parsed_data['optimized_grocery'] = optimized
                        print(f"🛒 Grocery optimized: {optimized.get('total_unique', 0)} unique items")
                    except Exception as gx:
                        print(f"⚠️ Grocery optimization warning: {gx}")
                        parsed_data['optimized_grocery'] = None
                
                print(f"✅ Success with {model_name}")
                return jsonify({
                    "success": True, 
                    "data": parsed_data, 
                    "raw_text": full_text
                })

            except Exception as e:
                error_msg = str(e)
                last_error = error_msg
                
                if any(x in error_msg for x in ["429", "RESOURCE_EXHAUSTED"]):

                    print(f"⚠️ Rate Limit on {model_name}. Switching to next model in 2s...")
                    time.sleep(2) 
                    continue 
                elif any(x in error_msg for x in ["404", "NOT_FOUND"]):
                    print(f"⚠️ Model Not Found: {model_name}")
                    continue 
                else:
                    print(f"⚠️ Plan Gen Error on {model_name}: {e}")
                    continue

    print(f"❌ All plan generation attempts failed. Last error: {last_error}")
    return jsonify({"error": f"Failed to generate plan. (Error: {last_error})"}), 500



# ----------------------------
# TRANSLATION API
# ----------------------------
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

@app.route("/translate", methods=["POST"])
def translate_content():
    try:
        data = request.json
        content = data.get("content")
        language = data.get("language")
        
        if not content or not language:
             return jsonify({"error": "Missing content or language"}), 400

        print(f"🌍 Translating to {language}...")

        # CRITICAL FIX: Protect Image Prompts from Translation
        # We extract them, remove from payload, and re-attach later
        protected_fields = {}
        if isinstance(content, dict):
            if "image_search_query" in content:
                protected_fields["image_search_query"] = content.pop("image_search_query")
            if "image_keywords" in content:
                protected_fields["image_keywords"] = content.pop("image_keywords")
            if "english_name" in content:
                protected_fields["english_name"] = content.pop("english_name")
        
        prompt = create_translation_prompt(content, language)
        
        last_error = None
        
        # Robust Fallback Loop
        for model_name in MODELS:
            try:
                print(f"🔄 Trying translation with {model_name}...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                
                text = response.text.strip()
                print(f"📄 Raw Translation Response: {text[:200]}...") # Debug log

                # Parse output - Try multiple strategies
                # Parse output - Try multiple strategies
                json_match = re.search(r"TRANSLATED_CONTENT:\s*(\{.*\})", text, re.DOTALL)
                
                # Check for "OUTPUT_START ... TRANSLATED_CONTENT ... OUTPUT_END" pattern more loosely
                if not json_match:
                     json_match = re.search(r"TRANSLATED_CONTENT:.*(\{[^{}]*\{.*?\}[^{}]*\})", text, re.DOTALL) # Attempt to find nested json
                
                if not json_match:
                        # Fallback 1: Look for standard JSON block
                        json_match = re.search(r"```json\s*(\{.*\})\s*```", text, re.DOTALL)
                if not json_match:
                        # Fallback 2: Look for any curly brace block that looks like a dict
                        # This matches the first outer {} block
                        json_match = re.search(r"(\{[\s\S]*\})", text)
                        
                if json_match:
                    json_str = json_match.group(1) if len(json_match.groups()) > 0 else json_match.group(0)
                    # Cleanup common markdown issues if any
                    json_str = json_str.strip()
                    try:
                        translated_json = json.loads(json_str)
                        
                        # Re-attach protected fields
                        if isinstance(translated_json, dict):
                            translated_json.update(protected_fields)
                            
                        print(f"✅ Translation success with {model_name}")
                        return jsonify({"success": True, "data": translated_json})
                    except json.JSONDecodeError as je:
                        print(f"⚠️ JSON Parse Error with {model_name}: {je}")
                        # Try to fix unquoted keys or trailing commas if simple? No, too complex.
                        last_error = f"JSON Parse Error: {je} (Substr: {json_str[:50]}...)"
                        continue
                else:
                    print(f"⚠️ No JSON found in response from {model_name}")
                    last_error = "No JSON found in response"
                    continue

            except Exception as e:
                error_msg = str(e)
                last_error = error_msg
                print(f"⚠️ Translation Error with {model_name}: {e}")
                
                if any(x in error_msg for x in ["429", "RESOURCE_EXHAUSTED"]):
                    print(f"⚠️ Rate Limit on {model_name}. Waiting 2s before switching...")
                    time.sleep(2) # Backoff
                elif any(x in error_msg for x in ["404", "NOT_FOUND"]):
                    print(f"⚠️ Model Not Found: {model_name}")

        print(f"❌ All translation attempts failed. Last error: {last_error}")
        return jsonify({"error": "Translation failed. Please try again.", "details": last_error}), 500

    except Exception as e:
        print(f"General Translation Error: {e}")
        return jsonify({"error": str(e)}), 500

# ----------------------------
# GROCERY OPTIMIZATION API
# ----------------------------

@app.route("/api/grocery/optimize", methods=["POST"])
def api_grocery_optimize():
    """Optimize a raw grocery list."""
    data = request.json
    raw_grocery = data.get("grocery_list", {})
    if not raw_grocery:
        return jsonify({"error": "No grocery list provided"}), 400

    optimized = optimize_grocery_list(raw_grocery)
    optimized = estimate_grocery_cost(optimized)

    # Budget check
    budget_tracker = BudgetTracker(session)
    budget_status = budget_tracker.check_budget(
        optimized.get('cost_summary', {}).get('total', 0)
    )
    optimized['budget_status'] = budget_status

    # Pantry deduction
    use_pantry = data.get("use_pantry", False)
    if use_pantry:
        pantry_mgr = PantryManager(session)
        if pantry_mgr.get_inventory():
            result = pantry_mgr.deduct_from_list(optimized)
            optimized = result['adjusted_list']
            optimized['pantry_deductions'] = result['deductions']

    return jsonify({"success": True, "data": optimized})


@app.route("/api/pantry", methods=["GET"])
def api_pantry_get():
    """Get all pantry items."""
    pantry_mgr = PantryManager(session)
    return jsonify({"success": True, "items": pantry_mgr.get_inventory()})


@app.route("/api/pantry", methods=["POST"])
def api_pantry_add():
    """Add or update a pantry item."""
    data = request.json
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "Item name required"}), 400
    pantry_mgr = PantryManager(session)
    result = pantry_mgr.add_item(
        name, data.get("quantity", 1), data.get("unit", "piece")
    )
    return jsonify({"success": True, **result, "items": pantry_mgr.get_inventory()})


@app.route("/api/pantry/remove", methods=["POST"])
def api_pantry_remove():
    """Remove a pantry item."""
    data = request.json
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "Item name required"}), 400
    pantry_mgr = PantryManager(session)
    pantry_mgr.remove_item(name)
    return jsonify({"success": True, "items": pantry_mgr.get_inventory()})


@app.route("/api/pantry/clear", methods=["POST"])
def api_pantry_clear():
    """Clear all pantry items."""
    pantry_mgr = PantryManager(session)
    pantry_mgr.clear_inventory()
    return jsonify({"success": True, "items": []})


@app.route("/api/budget/set", methods=["POST"])
def api_budget_set():
    """Set weekly grocery budget."""
    data = request.json
    amount = data.get("amount", 0)
    if not amount or float(amount) <= 0:
        return jsonify({"error": "Valid budget amount required"}), 400
    budget_tracker = BudgetTracker(session)
    budget = budget_tracker.set_budget(float(amount), data.get("currency", "INR"))
    return jsonify({"success": True, "budget": budget})


@app.route("/api/budget/status", methods=["GET"])
def api_budget_status():
    """Get budget status."""
    budget_tracker = BudgetTracker(session)
    budget = budget_tracker.get_budget()
    return jsonify({"success": True, "budget": budget})


@app.route("/api/budget/clear", methods=["POST"])
def api_budget_clear():
    """Clear budget."""
    budget_tracker = BudgetTracker(session)
    budget_tracker.clear_budget()
    return jsonify({"success": True})

# ----------------------------
# RECIPE IMAGE FETCHER (Pexels API)
# ----------------------------
import requests as http_requests  # alias to avoid conflict with flask request

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

@app.route("/api/food-image", methods=["GET"])
def api_food_image():
    """Fetch a high-quality food image matching the recipe name."""
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify({"image_url": None, "source": None})

    # Clean query — keep only alphanumeric food-relevant words
    safe_query = re.sub(r'[^a-zA-Z0-9\s]', '', query).strip()
    search_terms = safe_query.split()[:5]

    # --- Strategy 1: Pexels API (if key is configured) ---
    if PEXELS_API_KEY and PEXELS_API_KEY not in ("", "YOUR_PEXELS_API_KEY_HERE"):
        headers = {"Authorization": PEXELS_API_KEY}

        # Full recipe name search — use just "food" suffix for cleaner matching
        search_query = " ".join(search_terms) + " food"
        try:
            resp = http_requests.get(
                "https://api.pexels.com/v1/search",
                headers=headers,
                params={"query": search_query, "per_page": 5, "orientation": "landscape"},
                timeout=6
            )
            if resp.status_code == 200:
                data = resp.json()
                photos = data.get("photos", [])
                if photos:
                    img_url = photos[0]["src"].get("medium", photos[0]["src"].get("large"))
                    print(f"🖼️ Pexels image found for '{query}': {img_url}")
                    return jsonify({"image_url": img_url, "source": "pexels"})
        except Exception as e:
            print(f"⚠️ Pexels search failed: {e}")

        # Shorter keyword fallback
        if len(search_terms) > 2:
            short_query = " ".join(search_terms[:2]) + " food"
            try:
                resp = http_requests.get(
                    "https://api.pexels.com/v1/search",
                    headers=headers,
                    params={"query": short_query, "per_page": 3, "orientation": "landscape"},
                    timeout=6
                )
                if resp.status_code == 200:
                    data = resp.json()
                    photos = data.get("photos", [])
                    if photos:
                        img_url = photos[0]["src"].get("medium", photos[0]["src"].get("large"))
                        print(f"🖼️ Pexels fallback image for '{query}': {img_url}")
                        return jsonify({"image_url": img_url, "source": "pexels_fallback"})
            except Exception as e:
                print(f"⚠️ Pexels fallback also failed: {e}")

    # --- Strategy 2: Wikipedia REST API (FREE — huge coverage) ---
    import urllib.parse
    # Convert dish name to Wikipedia article format: "Chicken Burger" → "Chicken_burger"
    wiki_title = "_".join(search_terms).title()
    # Also try the original query as-is
    wiki_variants = [wiki_title, "_".join(search_terms), safe_query.replace(" ", "_")]
    # Remove duplicates while preserving order
    seen = set()
    wiki_variants = [x for x in wiki_variants if not (x in seen or seen.add(x))]

    for wiki_name in wiki_variants:
        try:
            resp = http_requests.get(
                f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(wiki_name)}",
                timeout=6,
                headers={"User-Agent": "NutriGenAI/1.0 (Recipe Image Fetcher)"}
            )
            if resp.status_code == 200:
                data = resp.json()
                # Prefer originalimage (higher res), fall back to thumbnail
                img_url = None
                if data.get("originalimage", {}).get("source"):
                    img_url = data["originalimage"]["source"]
                elif data.get("thumbnail", {}).get("source"):
                    img_url = data["thumbnail"]["source"]
                if img_url:
                    print(f"🖼️ Wikipedia image found for '{query}' (wiki: {wiki_name}): {img_url}")
                    return jsonify({"image_url": img_url, "source": "wikipedia"})
        except Exception as e:
            print(f"⚠️ Wikipedia search failed for '{wiki_name}': {e}")

    # --- Strategy 3: TheMealDB (FREE — smaller database but good matches) ---
    mealdb_query = urllib.parse.quote(safe_query)
    try:
        resp = http_requests.get(
            f"https://www.themealdb.com/api/json/v1/1/search.php?s={mealdb_query}",
            timeout=6
        )
        if resp.status_code == 200:
            data = resp.json()
            meals = data.get("meals")
            if meals and len(meals) > 0:
                img_url = meals[0].get("strMealThumb")
                if img_url:
                    print(f"🖼️ TheMealDB image found for '{query}': {img_url}")
                    return jsonify({"image_url": img_url, "source": "themealdb"})
    except Exception as e:
        print(f"⚠️ TheMealDB search failed: {e}")

    # --- Strategy 4: Wikipedia search API (keyword-based fallback) ---
    try:
        wiki_search_query = urllib.parse.quote(safe_query + " food")
        resp = http_requests.get(
            f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={wiki_search_query}&format=json&srlimit=3",
            timeout=6,
            headers={"User-Agent": "NutriGenAI/1.0 (Recipe Image Fetcher)"}
        )
        if resp.status_code == 200:
            data = resp.json()
            results = data.get("query", {}).get("search", [])
            for result in results:
                page_title = result.get("title", "").replace(" ", "_")
                try:
                    page_resp = http_requests.get(
                        f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(page_title)}",
                        timeout=5,
                        headers={"User-Agent": "NutriGenAI/1.0 (Recipe Image Fetcher)"}
                    )
                    if page_resp.status_code == 200:
                        page_data = page_resp.json()
                        img_url = None
                        if page_data.get("originalimage", {}).get("source"):
                            img_url = page_data["originalimage"]["source"]
                        elif page_data.get("thumbnail", {}).get("source"):
                            img_url = page_data["thumbnail"]["source"]
                        if img_url:
                            print(f"🖼️ Wikipedia search image for '{query}': {img_url}")
                            return jsonify({"image_url": img_url, "source": "wikipedia_search"})
                except Exception:
                    continue
    except Exception as e:
        print(f"⚠️ Wikipedia search API failed: {e}")

    print(f"⚠️ No relevant image found for '{query}' — showing placeholder")
    return jsonify({"image_url": None, "source": None})


# ----------------------------
# IMAGE-BASED INGREDIENT DETECTION
# ----------------------------
@app.route("/api/detect-ingredients", methods=["POST"])
def api_detect_ingredients():
    """Detect ingredients from an uploaded image using Gemini Vision."""
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    # Validate file type
    allowed_types = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    mime_type = file.content_type or "image/jpeg"
    if mime_type not in allowed_types:
        return jsonify({"error": f"Unsupported image type: {mime_type}"}), 400

    # Read image bytes (limit to 10MB)
    image_bytes = file.read()
    if len(image_bytes) > 10 * 1024 * 1024:
        return jsonify({"error": "Image too large (max 10MB)"}), 400

    # Track usage
    if "user" in session:
        users = load_users()
        c_data = session["user"]
        for e, u in users.items():
            if u.get("name") == c_data.get("name"):
                track_feature_usage(e, "Image Ingredient Detection")
                break

    result = detect_ingredients(image_bytes, mime_type)
    return jsonify({"success": True, **result})


# ----------------------------
# RUN
# ----------------------------
if __name__ == "__main__":
    print("🚀 Server running at http://127.0.0.1:5000")
    app.run(debug=True, exclude_patterns=['*\\Lib\\site-packages\\*', '*\\venv\\*'])
