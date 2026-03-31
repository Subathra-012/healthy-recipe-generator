CHAPTER 2
2. LOGICAL DEVELOPMENT
2.1 ARCHITECTURAL DESIGN
Healthy Recipe Generator relies on a React (TypeScript) frontend interface and FastAPI (Python) backend interface combined with Firebase Firestore (NoSQL) cloud storage system to streamline recipe generation and meal planning. The FastAPI backend architecture features multiple service modules for AI recipe generation, ingredient detection, user authentication, smart filtering, voice processing, nutrition tracking, cost estimation, and PDF generation, which enable smooth connections between frontend components and the database. The system relies on the secure Firebase Firestore NoSQL database to keep user details, generated recipes, pantry inventory, meal plans, usage history, and saved preferences working together to provide steady system operation. The frontend layer is built with React 18 and TypeScript using the Vite build tool, and includes dedicated pages for Landing, Recipe Generator, Smart Recipe Assistant (Image/Voice), My Ingredients, Meal Plans, Saved Recipes, and a comprehensive Admin Panel (User Management, Recipe Analytics, API Usage Dashboard). The backend service layer follows a modular architecture pattern with dedicated service classes — GenerativeAIService, IngredientDetectionService, VoiceInputService, NutritionCalculationService, CostEstimationService, PDFReportService, AuthenticationService, and WebSocketManager — each handling a specific domain of the application logic. Real-time communication between the frontend and backend is achieved through WebSocket connections for live recipe generation progress updates. Firebase Authentication handles user identity verification with support for Google OAuth and email/password login, while Gemini API integration enables advanced AI-driven recipe generation based on user preferences.
Fig 2.1.1 Architectural Design of the System
•	Top Layer — User
•	Frontend (React, TypeScript, Vite, Tailwind CSS)
•	Login / Signup | Landing | Recipe Generator | Smart Assistant | My Ingredients | Meal Plans | Saved Recipes | Profile
•	Admin Panel: User Management | Recipe Analytics | API Usage Dashboard
•	Real-Time Layer — WebSocket (Generation Progress Updates)
•	Backend (Python, FastAPI)
•	Router Layer (API Endpoints — Recipes, AI Assistant, Nutrition, Pantry, Users, Admin)
•	Service Layer (GenerativeAIService | IngredientDetectionService | VoiceInputService | NutritionCalculationService | CostEstimationService | PDFReportService | AuthenticationService | WebSocketManager)
•	Model Layer (Pydantic Models — RecipeRequest, ImageDetectionRequest, VoiceCommand, UserPreferences, MealPlanCreate, NutritionInfo)
•	External Services
•	Firebase Authentication | Google Gemini API (AI text/image) | SMTP Email
•	Database — Firebase Firestore (NoSQL)
•	Collections: users | recipes | pantry_items | meal_plans | generation_history | saved_recipes
2.2 DATA FLOW DIAGRAM
A system data flow gets displayed in Data Flow Diagrams (DFDs) through illustration of process and data store interactions and external information exchanges. It leverages the understanding of information handling procedures to enable useful analysis for design creation. The Healthy Recipe Generator system project should utilize multiple levels of abstraction to depict data movement starting at the overall system context then progressing into increased detail.

Level 0
The Level 0 Data Flow Diagram (DFD) of the Healthy Recipe Generator system illustrates the interaction between key components. Users provide recipe generation parameters (ingredients, dietary preferences, goals) and authentication credentials, which are processed by the system and stored in the Firebase Firestore database. The FastAPI application handles ingredient detection, AI generation, and nutrition calculation tasks based on user data and retrieves results from the system. External services including Firebase Authentication and the Google Gemini API interact with the system for identity verification and AI processing respectively. The system then returns processed results including generated recipe recipes, pantry updates, and nutritional analysis to the user, ensuring efficient and customized meal planning management.
Fig 2.2.1 Data Flow Diagram (Level 0)

Level 1
The Level 1 Data Flow Diagram (DFD) of the Healthy Recipe Generator system provides a detailed view of data interactions. Users authenticate through the Firebase Authentication system (supporting Google OAuth and email/password login) before initiating the generation process. Upon entering the smart assistant, users pass through the Image/Voice Detection Module which performs image classification, speech-to-text translation, and ingredient extraction to map inputs to searchable food items. Verified inputs are passed into the Generative AI Engine where the Gemini API processes user preferences (dietary restrictions, macros, specific cuisines) alongside available ingredients to produce comprehensive culinary instructions. Real-time generation progress updates are broadcast to users via WebSocket connections. When the recipe is finalized, the user proceeds to the Nutrition Calculation Engine for interactive macronutrient analysis, allergy validation, and cost estimation logic. The finalized meal plan is then processed through the PDF Generation Module to create downloadable premium recipe cards. Upon successful creation, the Notification Service (SMTP) sends the generated recipe and grocery list to the user via email. The Background Worker continuously parses usage history to optimize pantry suggestions and cleanup expired session data. The Analytics Service aggregates platform-wide metrics including popular ingredients, API usage, average recipe cost, and generation speed for the admin dashboard. The Voice Input Service manages continuous listening buffers for users experiencing hand-free cooking scenarios, preserving their voice state for seamless execution. All data interactions are managed through the FastAPI REST API endpoints, while responses, generated outputs, and real-time generation metrics are delivered to both users and administrators.
CHAPTER 3
3.1 DATABASE DESIGN
Since Healthy Recipe Generator uses Firebase Firestore (NoSQL), data is stored as collections containing documents with fields, rather than traditional relational tables. Each collection is analogous to a table, and each document is analogous to a row. Below are the primary collections used in the system.

3.1.1 Collection Name: users
S. No.	Field	Type	Constraint
1.	uid	String	Primary (Document ID)
2.	name	String	Not Null
3.	email	String	Unique, Not Null
4.	role	String	Not Null (user / admin)
5.	membership_type	String	Default: "FREE" (FREE / PRO / PREMIUM)
6.	health_score	Integer	Default: 0
7.	account_status	String	Default: "active"
8.	dietary_preference	String	Optional
9.	created_at	Timestamp	Auto-generated
10.	last_login	Timestamp	Optional

3.1.2 Collection Name: recipes
S. No.	Field	Type	Constraint
1.	recipe_id	String	Primary (Document ID)
2.	title	String	Not Null
3.	description	String	Not Null
4.	cuisine_type	String	Not Null (e.g., Italian, Mexican, Indian)
5.	prep_time_minutes	Integer	Not Null
6.	complexity	String	Not Null (easy / medium / hard)
7.	image_url	String	Optional
8.	status	String	Not Null (draft / published / archived)
9.	total_calories	Integer	Auto-calculated
10.	protein_grams	Integer	Dynamic
11.	ingredients	Array[Map]	Nested (categories: [{name, quantity, unit, is_core}])
12.	instructions	Array[String]	List of steps
13.	health_tags	Array[String]	List of dietary tags (e.g., keto, vegan)
14.	ai_metadata	Map	Nested (model_used, token_count, confidence_score)
15.	voice_config	Map	Nested (voice_enabled, read_speed, language)
16.	cost_config	Map	Nested (estimated_cost, currency)
17.	analytics_enabled	Boolean	Default: true
18.	created_by	String	Foreign Key → users.uid
19.	created_at	Timestamp	Auto-generated

3.1.3 Collection Name: pantry_items
S. No.	Field	Type	Constraint
1.	item_id	String	Primary (Document ID)
2.	user_id	String	Foreign Key → users.uid
3.	category	String	Not Null (e.g., Produce, Dairy, Spices)
4.	item_name	String	Not Null
5.	quantity	Float	Not Null
6.	unit	String	Not Null (e.g., grams, cups, pieces)
7.	status	String	Not Null (available / expired / low_stock)
8.	expiry_date	Timestamp	Optional
9.	added_at	Timestamp	Auto-generated
10.	last_updated	Timestamp	Auto-generated

3.1.4 Collection Name: meal_plans
S. No.	Field	Type	Constraint
1.	plan_id	String	Primary (Document ID)
2.	user_id	String	Foreign Key → users.uid
3.	start_date	Timestamp	Not Null
4.	end_date	Timestamp	Not Null
5.	plan_title	String	Not Null
6.	daily_meals	Array[Map]	Nested ({day, breakfast_id, lunch_id, dinner_id})
7.	target_calories	Integer	Not Null
8.	actual_calories	Integer	Auto-calculated
9.	cost_estimate	Float	Default: 0
10.	total_cost	Float	Not Null
11.	membership_tier	String	Not Null (FREE / PRO / PREMIUM)
12.	status	String	Not Null (active / completed / abandoned)
13.	grocery_list_id	String	Optional
14.	pdf_report_id	String	Optional
15.	created_at	Timestamp	Auto-generated
16.	expires_at	Timestamp	Auto-generated
17.	completed_at	Timestamp	Optional

3.1.5 Collection Name: generation_history
S. No.	Field	Type	Constraint
1.	history_id	String	Primary (Document ID)
2.	recipe_id	String	Optional (Foreign Key → recipes.recipe_id)
3.	user_id	String	Foreign Key → users.uid
4.	generation_type	String	Not Null (TEXT / IMAGE / VOICE)
5.	input_prompt	String	Not Null
6.	status	String	Not Null (PROCESSING / COMPLETED / FAILED)
7.	retry_count	Integer	Default: 0
8.	created_at	Timestamp	Auto-generated
9.	completed_at	Timestamp	Auto-updated

3.1.6 Collection Name: saved_recipes
S. No.	Field	Type	Constraint
1.	save_id	String	Primary (Auto-generated)
2.	user_id	String	Foreign Key → users.uid
3.	recipe_id	String	Foreign Key → recipes.recipe_id
4.	folder_name	String	Default: "Favorites"
5.	rating	Integer	Optional (1-5)
6.	saved_at	Timestamp	Auto-generated

3.1.7 Collection Name: voice_sessions
S. No.	Field	Type	Constraint
1.	session_id	String	Primary (Document ID)
2.	user_id	String	Foreign Key → users.uid
3.	recipe_id	String	Optional (Foreign Key → recipes.recipe_id)
4.	status	String	Not Null (listening / processing / closed)
5.	created_at	Timestamp	Auto-generated
6.	expires_at	Timestamp	Not Null
7.	last_interaction	Timestamp	Optional

3.1.8 Collection Name: detection_logs
S. No.	Field	Type	Constraint
1.	log_id	String	Primary (Document ID)
2.	item_id	String	Not Null (image_upload_id)
3.	item_type	String	Not Null (ingredient_scan / receipt_scan)
4.	action	String	Not Null (auto_add_pantry / generation_input)
5.	confidence_score	Float	Optional
6.	timestamp	Timestamp	Auto-generated

3.1.9 Collection Name: membership_logs
S. No.	Field	Type	Constraint
1.	log_id	String	Primary (Auto-generated)
2.	uid	String	Foreign Key → users.uid
3.	plan	String	Not Null (PRO / PREMIUM)
4.	amount	Float	Not Null
5.	razorpay_payment_id	String	Not Null
6.	timestamp	Timestamp	Auto-generated

3.1.10 Collection Name: analytics_recipe
S. No.	Field	Type	Constraint
1.	recipe_id	String	Primary (Document ID), Foreign Key → recipes.recipe_id
2.	views	Integer	Default: 0
3.	generations_success	Integer	Default: 0
4.	generations_failed	Integer	Default: 0
5.	cost_saved	Float	Default: 0.0
6.	abandoned_generations	Integer	Default: 0

3.3 RELATIONSHIP DIAGRAM
Fig 3.3.1 Relationship Diagram for Healthy Recipe Generator System
(Diagram Description: Create an Entity-Relationship (ER) diagram showing the following entities and their attributes connected through relationships)

Entity: User (users)
•	Attributes: uid, name, email, role, membership_type, health_score, account_status, dietary_preference, created_at, last_login

Entity: Recipe (recipes)
•	Attributes: recipe_id, title, description, cuisine_type, prep_time_minutes, complexity, image_url, status, total_calories, protein_grams, ingredients, instructions, health_tags, ai_metadata, voice_config, cost_config, analytics_enabled, created_by, created_at

Entity: Pantry Item (pantry_items)
•	Attributes: item_id, user_id, category, item_name, quantity, unit, status, expiry_date, added_at, last_updated

Entity: Meal Plan (meal_plans)
•	Attributes: plan_id, user_id, start_date, end_date, plan_title, daily_meals, target_calories, actual_calories, cost_estimate, total_cost, membership_tier, status, grocery_list_id, pdf_report_id, created_at, expires_at, completed_at

Entity: Generation History (generation_history)
•	Attributes: history_id, recipe_id, user_id, generation_type, input_prompt, status, retry_count, created_at, completed_at

Entity: Saved Recipe (saved_recipes)
•	Attributes: save_id, user_id, recipe_id, folder_name, rating, saved_at

Entity: Voice Session (voice_sessions)
•	Attributes: session_id, user_id, recipe_id, status, created_at, expires_at, last_interaction

Entity: Detection Log (detection_logs)
•	Attributes: log_id, item_id, item_type, action, confidence_score, timestamp

Entity: Membership Log (membership_logs)
•	Attributes: log_id, uid, plan, amount, razorpay_payment_id, timestamp

Entity: Analytics Recipe (analytics_recipe)
•	Attributes: recipe_id, views, generations_success, generations_failed, cost_saved, abandoned_generations

Relationships:
•	User → creates → Recipe (One-to-Many)
•	User → manages → Pantry Item (One-to-Many)
•	User → schedules → Meal Plan (One-to-Many)
•	User → triggers → Generation History (One-to-Many)
•	User → saves → Saved Recipe (One-to-Many)
•	User → initiates → Voice Session (One-to-Many)
•	User → upgrades → Membership Log (One-to-Many)
•	Recipe → included in → Saved Recipe (One-to-Many)
•	Recipe → logged in → Generation History (One-to-Many)
•	Recipe → discussed in → Voice Session (One-to-Many)
•	Recipe → has → Analytics Recipe (One-to-One)
•	Meal Plan → contains → Recipe (Many-to-Many via daily_meals array)

CHAPTER 4
4. PROGRAM DESIGN
The Healthy Recipe Generator system contains eight essential component modules. User Management & Authentication provides secure access control features to authenticate users through Firebase Authentication with support for Google OAuth and email/password login. Administrators have access to full system insights while standard users can manage their dietary preferences and saved recipes. Through the Generative AI Engine module, users utilize the Google Gemini API to process preferences and available ingredients to produce comprehensive culinary instructions. The Smart Input Processing module enables users to upload images of their fridge or speak directly to the assistant, converting visual and audio inputs into structured ingredient lists. The Pantry & Inventory Management module allows users to track their available ingredients, manage quantities, and receive alerts for soon-to-expire items. The Meal Planning & Nutrition Tracking module enables users to organize their weekly meals while automatically calculating total calories, macros, and estimated costs based on their profile settings. The Real-Time Generation & WebSockets module provides an interactive experience by streaming the AI's recipe generation progress directly to the user's screen in real-time. The PDF Generation & Notification System module produces premium digital recipe cards and automatically emails them along with generated grocery lists to the user's inbox. The Dashboard, Analytics & System Health module provides visual information about popular recipes, API usage, average recipe cost, and generation performance metrics for the admin dashboard.
The Healthy Recipe Generator system consists of the following core modules:
1.	User Management & Authentication
2.	Generative AI Engine
3.	Smart Input Processing (Image & Voice)
4.	Pantry & Inventory Management
5.	Meal Planning & Nutrition Tracking
6.	Real-Time Generation & WebSockets
7.	PDF Generation & Notification System
8.	Dashboard, Analytics & System Health

4.1 MODULE DESCRIPTION

4.1.1 User Management & Authentication
The User Management & Authentication module of the Healthy Recipe Generator executes operations to authenticate users while managing their profiles, dietary preferences, and access controls for secure user experiences. The module performs new user registration through Firebase Authentication which supports both Google OAuth single sign-on and traditional email/password authentication to safeguard against unauthorized system entry. After successful registration, the system allows users to log in and verifies the Firebase ID token with the backend server via FastAPI to establish their identity. Authentication procedures verify that only legitimate users can access protected system endpoints. A central functionality of the module depends on Role-Based Access Control (RBAC) that segments users into roles — admin and user — with defined authorization permissions. The application offers regular users authentication to manage personal profiles, view recipe generation history, update pantry items, and access the core generation features based on their membership tier (FREE, PRO, PREMIUM) which determines their daily generation limits and advanced tool access. The administrative role contains advanced permissions which enable the admin to view registered accounts, modify user roles, and monitor system-wide usage through the dedicated admin dashboard. The system's hierarchical authorization system locks down vital admin endpoints using dependency injection to prevent unauthorized actions. User profiles are stored in the Firebase Firestore users collection with fields including uid, name, email, role, membership_type, health_score, account_status, dietary_preference, and timestamps. This module also handles account status tracking and subscription upgrades using the Razorpay payment gateway (logged in membership_logs). The user management system functions as the backbone for personalized recipe generation and secure access across all other modules of the platform.

4.1.2 Generative AI Engine
The Generative AI Engine module of the Healthy Recipe Generator creates a comprehensive processing pipeline that translates user requirements into detailed, actionable culinary instructions using advanced language models. This module integrates directly with the Google Gemini API through the GenerativeAIService layer to process complex requests involving dietary restrictions, macro-nutrient targets, specific cuisines, and available ingredients. When a user requests a recipe, the engine constructs a sophisticated prompt structure that enforces the output to comply strictly with the user's active health profile (e.g., keto, vegan, nut-free). The system provides highly granular configuration for generation parameters — controlling the complexity (easy, medium, hard), preparation time limits, and the exact balancing of proteins, carbohydrates, and fats. The generated recipes are structured into standardized JSON or Markdown formats containing the recipe title, a brief description, estimated prep time, categorical ingredients with exact measurements, step-by-step instructions, and calculated total calories. Upon successful generation, the system automatically saves the output as an individual document in the recipes collection, complete with ai_metadata tracking the model used and generation confidence scores. This module also manages the retry logic and failure handling, appending detailed records into the generation_history collection to track success rates, prompt variants, and any abandoned generation attempts.

4.1.3 Smart Input Processing (Image & Voice)
The Smart Input Processing module of the Healthy Recipe Generator implements an accessible, hands-free interface that allows users to interact with the platform through visual and auditory channels, bypassing manual text entry. The Image Detection component utilizes computer vision models to scan uploaded photographs of the user's refrigerator, pantry, or grocery receipts. It identifies food items, extracts text from labels, and intelligently maps the detected objects to a standardized ingredient database. The Voice Input component manages continuous listening sessions for users experiencing hands-free cooking scenarios or rapid ingredient dictation. It employs speech-to-text algorithms to transcribe spoken commands into text, intelligently parsing out quantities and ingredient names. To maintain context during speech interaction, the VoiceInputService establishes a temporary state stored in the voice_sessions collection, keeping track of the user's active context (listening, processing, closed). Any detection events, whether from image scanning or voice transcription, are recorded in the detection_logs collection along with confidence scores to continuously improve matching accuracy. These processed inputs are seamlessly fed into the Generative AI Engine to produce context-aware recipes based exactly on what the user has currently available in their kitchen.

4.1.4 Pantry & Inventory Management
The Pantry & Inventory Management module handles the complete lifecycle of a user's food inventory, incorporating intelligent categorization, quantity tracking, and expiry date management to minimize food waste and optimize meal planning. When users log their available ingredients—either manually or automatically via the Smart Input Processing module—the items are assigned to specific categories (Produce, Dairy, Spices, Meat) and stored as active documents in the pantry_items collection. Each item tracks its exact quantity, standard unit of measurement (grams, cups, pieces), and dynamic status (available, expired, low_stock). The system performs continuous cross-referencing between the user's active pantry and the ingredients required for their generated or saved recipes. When a user creates a Meal Plan, the required ingredients are evaluated against current pantry stock, and any deficits are automatically flagged to generate a supplemental grocery shopping list. Additionally, the backend service runs periodic scans on the pantry_items collection to calculate nearing expiration dates and actively switches statuses to 'expired' when limits are passed. This inventory data directly dictates the boundaries for the Generative AI Engine, ensuring the assistant prioritizes recipes that exhaust perishable, soon-to-expire ingredients before they spoil, promoting a highly cost-effective and environmentally friendly cooking lifecycle.

4.1.5 Meal Planning & Nutrition Tracking
The Meal Planning & Nutrition Tracking module provides structured weekly meal organization combined with precise macronutrient calculation and financial cost estimation for budget-conscious household management. Users can create comprehensive meal schedules stored in the meal_plans collection, selecting start and end dates, assigning specific recipes to daily slots (breakfast, lunch, dinner), and establishing target calorie thresholds for the week. The NutritionCalculationService automatically aggregates the nutritional data—total calories and protein grams—from every recipe scheduled in the plan, calculating the actual_calories to compare against the user's predefined targets. This ensures users adhere strictly to their health goals (e.g., muscle gain, weight loss). Simultaneously, the CostEstimationService analyzes the aggregated ingredient list against regional pricing data and standard unit costs to populate the cost_estimate and total_cost fields. If a user exceeds their weekly budget, the system can selectively suggest cheaper alternative ingredients (e.g., swapping chicken breast for chickpeas) to bring the total cost down. Membership tiers influence the depth of this tracking—PRO and PREMIUM members unlock highly detailed micronutrient breakdowns across their entire weekly plan. The module actively updates the completion status of meal plans (active, completed, abandoned) as time progresses, linking directly to automated grocery lists and downloadable PDF reports.

4.1.6 Real-Time Generation & WebSockets
The Real-Time Generation & WebSockets module implements an asynchronous streaming layer that serves as the primary communication bridge between the Generative AI backend and the React frontend interface, ensuring a highly responsive and engaging user experience during intensive AI processing operations. Due to the inherent latency of complex LLM inferences, rather than forcing the user to wait for a long-polling HTTP request to complete, the FastAPI server utilizes the WebSocketManager to establish a persistent, bidirectional WebSocket connection under the /ws/generation/{client_id} endpoint. As the Gemini API streams chunks of tokens representing the recipe's title, ingredients, and step-by-step instructions, the WebSocket layer instantly broadcasts these payloads back to the client interface. This allows the frontend to apply a visually appealing typewriter effect, rendering the recipe dynamically as it is "thought" of by the AI. This real-time progress update mechanism prevents frontend timeouts, minimizes perceived waiting time, and dramatically enhances user engagement. The module securely authenticates WebSocket connections using the same Firebase JWT validation as the HTTP REST endpoints, guaranteeing that active streams are securely tied to the verified user's session without exposing public sockets to unauthorized listeners.

4.1.7 PDF Generation & Notification System
The PDF Generation & Notification System module produces premium digital recipe cards, printable grocery lists, and handles all automated email communications to keep users informed about their generation history and meal plan statuses. The PDFReportService generates high-quality, printable PDFs using specialized report generation libraries in Python. Upon a user's request to save or print a meal plan, the system compiles the entire week's schedule, corresponding recipes, cooking instructions, required ingredients, grouped grocery lists, and nutrition/cost summaries into a professionally branded document. Each PDF is assigned a unique pdf_report_id, linked back to the originating meal plan or recipe, and is generated as a downloadable streaming response for immediate access. The NotificationService handles all outbound communication using secure SMTP configurations. For users who prefer async operations, whenever a lengthy meal plan generation completes, the service dispatches a beautifully formatted HTML email containing a summary of the weekly meals, the exact macros achieved, and a direct download link for the PDF report. The module is also responsible for sending critical system alerts, such as imminent pantry expiry notifications or payment receipts following a successful subscription upgrade, operating entirely on background tasks to prevent blocking the primary API responsiveness.

4.1.8 Dashboard, Analytics & System Health
The Dashboard, Analytics & System Health module provides administrators with comprehensive real-time operational data accompanied by API usage metrics, global recipe generation trends, and platform health indicators. The AnalyticsService aggregates platform-wide metrics from the analytics_recipe, detection_logs, and generation_history collections to deliver a unified dashboard summary inside the Admin Panel. The module computes total active users, total successful recipe generations, peak API usage times across a 24-hour timeline, total abandoned generations, and cumulative cost savings achieved by users through optimized pantry utilization. The interactive data visualization feature represents a standout component of this module, rendering complex backend metrics into intuitive frontend charts—such as line charts for daily generation volume, donut charts mapping the most popular cuisine types, and metric cards tracking the precise Google Gemini API token usage latency. Furthermore, the dashboard provides a granular view into the performance of the Smart Input capabilities by aggregating the confidence_score distributions from the Image and Voice detection engines, allowing administrators to pinpoint areas where the AI classification models may need fine-tuning. This module equips platform operators with complete visibility into resource utilization, active user engagement, and algorithmic efficiency to continuously refine and optimize the Healthy Recipe Generator ecosystem.
