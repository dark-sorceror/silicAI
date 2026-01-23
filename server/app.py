import os
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from main import gemini_chat

app = FastAPI(
    title = "silicAI Backend",
    description = "Gemini 3",
    version = "1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins = [
        "http://localhost:3000"
    ],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

class PromptRequest(BaseModel):
    user_prompt: str
    
@app.post("/chat")
async def chat(request: PromptRequest):
    response, sources = gemini_chat(request.user_prompt)

    return {
        "text": response,
        "sources": sources
    }

if __name__ == "__main__":
    os.system('cls')
    
    uvicorn.run(
        "__main__:app", 
        host = "127.0.0.1", 
        port = 5000, 
        reload = True,
        reload_dirs = ["."]
    )