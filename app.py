from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import asyncio
from Controller.waifu import Waifu
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
    user_input_service='whisper',
    stt_duration=0.5,
    mic_index=None,
    chatbot_service='openai',
    chatbot_model='gpt-3.5-turbo',
    chatbot_temperature=0.7,
    personality_file='Assets/personality.txt',
    tts_service='edge',
    output_device=7,
    tts_voice='id-ID-GadisNeural'
)

@app.get("/")
async def index(request: Request):
    """
    Endpoint untuk menampilkan halaman utama.
    """
    return templates.TemplateResponse("index.html", {"request": request})

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