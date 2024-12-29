from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from dotenv import dotenv_values, set_key
from Controller.waifu import Waifu

import os
import aiofiles
import asyncio
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Setup Templates dan Static Files
app.mount('/static', StaticFiles(directory='static', html=True), name='static')
templates = Jinja2Templates(directory="templates")

# Initialize Waifu instance
waifu = Waifu()

waifu.initialize(
    user_input_service='google',
    stt_duration=0.5,
    mic_index=None,
    chatbot_service='openai',
    chatbot_model='gpt-3.5-turbo',
    chatbot_temperature=0.7,
    personality_file='Assets/personality.txt',
    tts_service='edge',
    output_device=7,
    tts_voice='ja-JP-NanamiNeural'
)

@app.get("/")
async def index(request: Request):
    """
    Endpoint untuk menampilkan halaman utama.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/chat")
async def chat(request: Request):
    """
    Endpoint untuk menampilkan halaman chat.
    """
    return templates.TemplateResponse("chat.html", {"request": request})

@app.post("/send_message")
async def send_message(user_input: str = Form(...)):
    """
    Endpoint untuk mengirim pesan teks ke Waifu dan mendapatkan respons.
    """
    if not user_input.strip():
        raise HTTPException(status_code=400, detail="User input cannot be empty.")

    try:
        response = waifu.get_chatbot_response(user_input)  # Tidak menggunakan await
        await waifu.tts_say(response)  # Tetap gunakan await jika ini coroutine
        return JSONResponse({"response": response})
    except Exception as e:
        logger.error(f"Error in send_message: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process the request.")

@app.post("/talking_mode")
async def talking_mode(talking_mode: bool = Form(...)):
    """
    Endpoint untuk mode percakapan suara dengan Waifu.
    """
    try:
        if talking_mode:
            user_input = waifu.get_user_input()  # Jika ini synchronous, tidak perlu await
            response = waifu.get_chatbot_response(user_input)  # Pastikan ini coroutine
            await waifu.tts_say(response)  # Pastikan ini coroutine
            return JSONResponse({"response": response})
        else:
            return JSONResponse({"response": "Talking mode deactivated."})
    except Exception as e:
        logger.error(f"Error in talking_mode: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to toggle talking mode.")
    
@app.get("/status")
async def status():
    """
    Endpoint to return the status of the API.
    """
    try:
        # Simulate a status check or add actual logic if needed
        return JSONResponse({"status": "online", "code": 200})
    except Exception as e:
        logger.error(f"Error checking status: {str(e)}")
        return JSONResponse({"status": "offline", "code": 500})

# Paths
assets_path = "Assets"
env_file = ".env"
personality_file = os.path.join(assets_path, "personality.txt")
log_file = "waifu_error.log"
message_history_file = os.path.join(assets_path, "message_history.txt")

# Dashboard route
@app.get("/admin", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

# API to fetch and update .env
@app.get("/api/env")
async def get_env():
    return dotenv_values(env_file)

@app.post("/api/env")
async def save_env(data: dict):
    content = data.get('content')
    async with aiofiles.open(env_file, mode="w") as f:
        await f.write(content)
    return {"status": "success"}

# API to fetch and update personality.txt
@app.get("/api/personality")
async def get_personality():
    async with aiofiles.open(personality_file, mode="r") as f:
        content = await f.read()
    return {"content": content}

@app.post("/api/personality")
async def save_personality(data: dict):
    content = data.get('content')
    async with aiofiles.open(personality_file, mode="w") as f:
        await f.write(content)
    return {"status": "success"}

# API to fetch waifu_error.log
@app.get("/api/log")
async def get_log():
    async with aiofiles.open(log_file, mode="r") as f:
        content = await f.read()
    return {"content": content}

# API to fetch message_history.txt
@app.get("/api/message_history")
async def get_message_history():
    async with aiofiles.open(message_history_file, mode="r") as f:
        content = await f.read()
    return {"content": content}

# API to list mp3 files
@app.get("/api/mp3")
async def list_mp3():
    files = [f for f in os.listdir(assets_path) if f.endswith(".mp3")]
    return {"files": files}

@app.get("/api/mp3/{filename}")
async def get_mp3(filename: str):
    file_path = os.path.join(assets_path, filename)
    return FileResponse(file_path)