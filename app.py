from flask import Flask, render_template, request, jsonify
from Controller.waifu import Waifu
import os
import pyaudio
import time
from pydub import AudioSegment
from io import BytesIO
import asyncio

app = Flask(__name__)

# Initialize Waifu instance
waifu = Waifu()

# Configure Waifu
waifu.initialize(
    user_input_service='whisper',
    stt_duration=0.5,
    mic_index=None,
    chatbot_service='openai',
    chatbot_model='gpt-3.5-turbo',
    chatbot_temperature=0.7,
    personality_file=os.path.join('Assets', 'personality.txt'),
    tts_service='edge',
    output_device=12,
    tts_voice='id-ID-GadisNeural'
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
async def send_message():
    user_input = request.form['user_input']
    if user_input:
        response = waifu.get_chatbot_response(user_input)
        await waifu.tts_say(response)  # Await the coroutine
        return jsonify({"response": response})
    return jsonify({"response": "Sorry, I couldn't understand."})

@app.route('/talking_mode', methods=['POST'])
async def talking_mode():
    """Activate talking mode: Continuously listens and returns chatbot responses."""
    try:
        talking_mode = request.form.get('talking_mode', False)
        if talking_mode:
            user_input = waifu.get_user_input()  # Capture voice input
            response = waifu.get_chatbot_response(user_input)
            await waifu.tts_say(response)  # Await the TTS output to play audio
            return jsonify({"response": response})
        else:
            return jsonify({"response": "Talking mode deactivated."})
    except Exception as e:
        return jsonify({"response": f"Error: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True)
