from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv(override=True)

from agent_logic import manager

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Ensure API key is set
if "GOOGLE_API_KEY" not in os.environ:
    print("Warning: GOOGLE_API_KEY not found in environment variables.")


class StartRequest(BaseModel):
    target_language: str
    level: str
    native_language: str = "English"


class ChatRequest(BaseModel):
    session_id: str
    message: str
    target_language: str
    level: str
    native_language: str = "English"


@app.post("/start")
async def start_adventure(req: StartRequest):
    session_id = await manager.create_session(
        req.target_language, req.level, req.native_language
    )

    initial_query = f"Hello! I want to learn {req.target_language}. My native language is {req.native_language}. Please start a {req.level} level adventure story in {req.native_language}. Teach me {req.target_language} words by putting them in parentheses after the {req.native_language} word. Example: 'It is morning (**sabah**)'."

    response = await manager.send_message(
        session_id=session_id,
        message_text=initial_query,
        target_language=req.target_language,
        level=req.level,
        native_language=req.native_language,
    )

    return {"session_id": session_id, "response": response}


@app.post("/chat")
async def chat(req: ChatRequest):
    response = await manager.send_message(
        session_id=req.session_id,
        message_text=req.message,
        target_language=req.target_language,
        level=req.level,
        native_language=req.native_language,
    )
    return {"response": response}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
