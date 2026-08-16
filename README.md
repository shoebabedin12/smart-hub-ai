---
title: Student Portal AI
emoji: 🐳
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
---

# Student Portal AI Service

Flask-based RAG/AI microservice for the Student Portal project (chat, notice summarization, document indexing).

## Setup

### 1. Create a virtual environment (first time only)

```bash
python3 -m venv venv
```

### 2. Activate the virtual environment

**macOS / Linux (bash or zsh):**

```bash
source venv/bin/activate
```

**Windows (Command Prompt):**

```cmd
venv\Scripts\activate.bat
```

**Windows (PowerShell):**

```powershell
venv\Scripts\Activate.ps1
```

Once active, your terminal prompt will be prefixed with `(venv)`.

To deactivate at any time, on any OS:

```bash
deactivate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `example.env` to `.env` and fill in the real values:

```bash
cp example.env .env       # macOS/Linux
copy example.env .env     # Windows
```

Required variables:

| Variable | Description |
|---|---|
| `DATABASE_URL` | Connection string for the shared database |
| `GEMINI_API_KEY` | Google Gemini API key used for AI summarization/chat |
| `PORT` | Port to run the Flask server on (defaults to `7860`) |
| `HF_TOKEN` | Hugging Face token for model downloads |

## Running the project

With the virtual environment active:

```bash
python app.py
```

The service starts on `http://localhost:7860` (or whatever `PORT` is set to).

### Running with Docker (alternative, no venv needed)

```bash
docker build -t student-portal-ai .
docker run -p 7860:7860 --env-file .env student-portal-ai
```