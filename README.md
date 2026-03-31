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
- **Database**: DB Browser(SQLite)
- **Real-Time Communication**: WebSocket
- **Email Notifications**: SMTP
- **Security**: Google reCAPTCHA v2, PyCryptodome, python-jose, passlib
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

## Screenshots
<img width="1920" height="1080" alt="Screenshot 2026-03-02 223043" src="https://github.com/user-attachments/assets/a676f071-0bdc-483d-9a79-f0fe5c00775f" />
<img width="1920" height="1080" alt="Screenshot 2026-03-02 223020" src="https://github.com/user-attachments/assets/6ca0517b-ae08-437b-9541-5ef71020ebbb" />
<img width="1920" height="1080" alt="Screenshot 2026-03-02 221604" src="https://github.com/user-attachments/assets/6026ac69-4874-45e1-a7a9-81ea7461d53e" />
<img width="1920" height="1080" alt="Screenshot 2026-03-02 221309" src="https://github.com/user-attachments/assets/736e2fbe-e514-4002-9f6f-618c1fa44b8c" />
<img width="1920" height="1080" alt="Screenshot 2026-03-02 220520" src="https://github.com/user-attachments/assets/a86f0cad-b49a-43f8-842e-80e487891067" />
<img width="1920" height="1080" alt="Screenshot 2026-03-02 220349" src="https://github.com/user-attachments/assets/2cd8940f-936f-44f5-b312-a9fb04c7b7e5" />
<img width="1920" height="1080" alt="Screenshot 2026-03-31 121305" src="https://github.com/user-attachments/assets/dc876ebf-31ba-4e5e-9e94-34335106b35a" />


## How to Run 
.\venv\Scripts\Activate.ps1
Python app.py 
