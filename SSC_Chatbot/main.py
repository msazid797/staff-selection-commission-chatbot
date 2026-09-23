from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from rag_service import ask_chatbot


# -------------------------------------------------
# PATH CONFIGURATION
# -------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"


# -------------------------------------------------
# CREATE FASTAPI APPLICATION
# -------------------------------------------------

app = FastAPI(
    title="SSC Applicant Support Chatbot API",
    description="RAG-based chatbot API for SSC examination FAQs",
    version="1.0.0"
)


# -------------------------------------------------
# CORS CONFIGURATION
# -------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------
# STATIC FRONTEND FILES
# -------------------------------------------------

app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static"
)


# -------------------------------------------------
# REQUEST / RESPONSE MODELS
# -------------------------------------------------

class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str


# -------------------------------------------------
# FRONTEND
# -------------------------------------------------

@app.get("/")
def home():

    return FileResponse(
        FRONTEND_DIR / "index.html"
    )


# -------------------------------------------------
# HEALTH CHECK
# -------------------------------------------------

@app.get("/health")
def health():

    return {
        "status": "online",
        "message": "SSC Applicant Support Chatbot API is running."
    }


# -------------------------------------------------
# CHAT ENDPOINT
# -------------------------------------------------

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    question = request.question.strip()

    if not question:

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    try:

        answer = ask_chatbot(question)

        return ChatResponse(
            answer=answer
        )

    except Exception as error:

        print(f"Chat API Error: {error}")

        raise HTTPException(
            status_code=500,
            detail="Unable to process the question at this time."
        )