# BrandVoice AI – AI-Powered Brand Tweet Generator

An AI-powered application that generates 10 creative, engaging, and brand-aligned tweets based on a brand's industry, campaign objective, and product details.

## 🚀 Overview

BrandVoice AI helps businesses and content creators generate social media content that reflects their brand identity. It analyzes the provided brand information, identifies a suitable communication style, and generates 10 unique tweets.

## ✨ Features

- **Brand Voice Analysis:** Identifies brand tone, target audience, and content themes.
- **AI-Powered Tweet Generation:** Generates 10 tweets based on the provided details.
- **Multiple Content Styles:** Includes conversational, promotional, witty, and informative tweets.
- **Brand Voice Summary:** Provides a concise summary of the identified brand voice.
- **Simple User Interface:** Easy-to-use form for entering brand and campaign details.

## 🛠️ Tech Stack

**Frontend**
- React.js
- Vite
- JavaScript
- CSS / Tailwind CSS

**Backend**
- Python
- FastAPI
- Pydantic
- Google Gemini API

**Tools**
- Git and GitHub
- VS Code
- Postman
- Swagger UI

## ⚙️ How It Works

1. Enter the brand name and industry.
2. Provide the campaign objective and product details.
3. The application analyzes the brand information.
4. AI identifies the brand's tone, target audience, and content themes.
5. The application generates 10 brand-aligned tweets.
6. Review the brand voice summary and generated tweets.

## 📁 Project Structure

```text
BrandVoice-AI/
│
├── backend/
│   ├── app/
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── README.md
└── APPROACH.md
```

## 💻 Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/BharathHU/AI-Powered-Brand-Tweet-Generator.git
cd AI-Powered-Brand-Tweet-Generator
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
```

Activate the virtual environment in Windows PowerShell:

```powershell
.\venv\Scripts\Activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file inside the backend folder and configure your Gemini API credentials using the environment variable names required by the application.

Start the backend server using the command configured for your FastAPI application.

### 3. Frontend Setup

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the local frontend URL displayed in your terminal.

## 🔑 API Configuration

This project uses the Google Gemini API for AI-powered brand analysis and tweet generation.

- Obtain an API key from Google AI Studio.
- Store it in your local `.env` file.
- Never upload your actual API key or `.env` file to GitHub.

## 📄 Approach

The application uses prompt-based brand voice inference. It analyzes the information provided by the user and uses AI to identify the brand's communication style, target audience, and content themes.

The identified voice guides the generation of 10 tweets with different content styles to improve variety and relevance.

For more details, refer to **APPROACH.md**.

## 🔮 Future Enhancements

- Social media platform integration.
- Save and export generated tweets.
- Support for additional social media platforms.
- More customizable brand voice settings.

## 👨‍💻 Author

**Bharath H U**

GitHub: [BharathHU](https://github.com/BharathHU)

---

⭐ If you find this project useful, consider giving it a star!
