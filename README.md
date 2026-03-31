# Healthy Recipe Generator 🥗

An AI-powered web application that generates healthy, customized recipes using Google's Gemini API.

## Features

- **Custom Recipe Generation**: Input your food preferences, main ingredient, and health goals
- **All Features Recipe**: Generate a comprehensive, well-balanced recipe with one click
- **Beautiful UI**: Modern, responsive design with gradient backgrounds
- **Nutritional Charts**: Interactive bar charts showing macronutrient breakdown
- **Health Benefits**: Detailed health benefits for each ingredient
- **Step-by-step Instructions**: Clear, numbered cooking instructions

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd healthy-recipe-generator
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

5. Get your Gemini API key from: https://makersuite.google.com/app/apikey

## Usage

1. Run the Flask application:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Choose one of two options:
   - Fill in the form and click "Generate Recipe"
   - Click "All Features Recipe" for an instant comprehensive recipe

## Technologies Used

- **Application Server**: Python FastAPI with Uvicorn
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Radix UI, Framer Motion, Recharts, Lucide Icons
- **Backend Development**: Python (3.8+), FastAPI, Pydantic
- **Database**: Firebase Firestore (NoSQL)
- **Authentication**: Firebase Authentication (Google OAuth, Email/Password)
- **Payment Gateway**: Razorpay
- **Real-Time Communication**: WebSocket
- **PDF Generation**: ReportLab, QRCode
- **Email Notifications**: SMTP
- **Security**: Google reCAPTCHA v2, PyCryptodome, python-jose, passlib
- **Deployment**: Google Cloud Run, Firebase Hosting
- **Load Testing**: Locust
- **Version Control**: Git
- **AI**: Google Gemini API
## Project Structure
```
healthy-recipe-generator/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables
├── templates/
│   └── index.html        # Main HTML template
└── static/
    ├── css/
    │   └── style.css     # Styles
    └── js/
        └── main.js       # JavaScript functions
```

## License

MIT License