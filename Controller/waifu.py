import openai
import speech_recognition as sr
import edge_tts
import sounddevice as sd
import soundfile as sf
import logging

from threading import Thread
from functools import lru_cache
from os import getenv, path
from dotenv import load_dotenv
from json import load, dump, JSONDecodeError

# Configure logging
logging.basicConfig(
    filename="waifu_error.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Waifu:
    def __init__(self) -> None:
        self.mic = None
        self.recogniser = None

        self.user_input_service = None
        self.stt_duration = None

        self.chatbot_service = None
        self.chatbot_model = None
        self.chatbot_temperature = None
        self.chatbot_personality_file = None

        self.message_history = []
        self.context = []

        self.tts_service = None
        self.tts_voice = None

    def initialize(self, **kwargs) -> None:
        """Initialize Waifu configuration."""
        load_dotenv()

        self.user_input_service = kwargs.get("user_input_service", "whisper")
        self.stt_duration = kwargs.get("stt_duration", 0.5)
        self.mic = sr.Microphone(device_index=kwargs.get("mic_index"))
        self.recogniser = sr.Recognizer()

        # OpenAI configuration
        openai.api_key = getenv("OPENAI_API_KEY")
        openai.api_base = "https://api.zukijourney.com/v1"  # Custom API Base URL
        if not openai.api_key:
            raise ValueError("OpenAI API key not found.")

        self.chatbot_service = kwargs.get("chatbot_service", "openai")
        self.chatbot_model = kwargs.get("chatbot_model", "gpt-3.5-turbo")
        self.chatbot_temperature = kwargs.get("chatbot_temperature", 0.7)
        self.chatbot_personality_file = kwargs.get("personality_file")

        self.tts_service = kwargs.get("tts_service", "edge")
        self.tts_voice = kwargs.get("tts_voice", "id-ID-GadisNeural")
        self.output_device = kwargs.get("output_device")

        # Load personality and message history
        self.__load_personality()
        self.__load_message_history()

    def __load_personality(self) -> None:
        """Load personality from the configured file."""
        try:
            if self.chatbot_personality_file and path.isfile(self.chatbot_personality_file):
                with open(self.chatbot_personality_file, 'r') as f:
                    personality = f.read().strip()
            else:
                personality = "You are an AI assistant designed to help users in a friendly and informative way."
            self.context = [{'role': 'system', 'content': personality}]
        except Exception as e:
            logger.error(f"Error loading personality: {e}")
            self.context = [{'role': 'system', 'content': "You are an AI assistant."}]

    def __load_message_history(self) -> None:
        """Load message history from a file, if it exists."""
        try:
            if path.isfile('./Assets/message_history.txt'):
                with open('./Assets/message_history.txt', 'r') as f:
                    content = f.read().strip()
                    if content:  # Only attempt to parse if the file is not empty
                        self.message_history = load(f)
                    else:
                        self.message_history = []
            else:
                self.message_history = []
            logger.info("Message history successfully loaded.")
        except (JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error loading message history: {e}")
            self.message_history = []

    def __save_message_history(self) -> None:
        """Save message history to a file."""
        try:
            with open('./Assets/message_history.txt', 'w') as f:
                dump(self.message_history, f, indent=4)  # Save history in JSON format
            logger.info("Message history successfully saved.")
        except Exception as e:
            logger.error(f"Error saving message history: {e}")

    def __add_message(self, role: str, content: str) -> None:
        """Add a message to the history."""
        self.message_history.append({'role': role, 'content': content})

    def get_user_input(self) -> str:
        """Capture user input via microphone."""
        with self.mic as source:
            print("Listening...")
            self.recogniser.adjust_for_ambient_noise(source, duration=0.5)
            audio = self.recogniser.listen(source)
            print("Processing input...")

            if self.user_input_service == "whisper":
                return self.__whisper_sr(audio)
            elif self.user_input_service == "google":
                return self.recogniser.recognize_google(audio)
            else:
                raise ValueError(f"Unsupported service: {self.user_input_service}")

    @lru_cache(maxsize=100)
    def get_chatbot_response(self, prompt: str) -> str:
        """Get response from chatbot and update message history."""
        try:
            # Combine context and message history with the current prompt
            messages = self.context + self.message_history + [{"role": "user", "content": prompt}]
            response = openai.ChatCompletion.create(
                model=self.chatbot_model,
                messages=messages,
                temperature=self.chatbot_temperature
            )

            # Add messages to history
            self.__add_message("user", prompt)
            assistant_reply = response.choices[0].message["content"]
            self.__add_message("assistant", assistant_reply)

            # Save updated history
            self.__save_message_history()

            return assistant_reply
        except Exception as e:
            logger.error(f"Error getting chatbot response: {e}")
            return "I'm sorry, something went wrong."

    async def tts_say(self, text: str) -> None:
        """Generate and play text-to-speech audio."""
        if self.tts_service == "edge":
            await self.__edge_tts_generate(text, self.tts_voice)
            Thread(target=self.__play_audio, args=("./Assets/output.mp3", self.output_device)).start()

    async def __edge_tts_generate(self, text: str, voice: str) -> None:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save("./Assets/output.mp3")

    @staticmethod
    def __play_audio(file_path: str, output_device: int = None) -> None:
        """Play audio using the specified output device."""
        data, fs = sf.read(file_path)
        sd.play(data, fs, device=output_device)  # Tentukan perangkat output
        sd.wait()

    def __whisper_sr(self, audio) -> str:
        """Transcribe speech using Whisper."""
        with open('./Assets/speech.wav', 'wb') as f:
            f.write(audio.get_wav_data())
            transcript = openai.Audio.transcribe("whisper-1", open('./Assets/speech.wav', 'rb'))
        return transcript['text']

    def save_state(self) -> None:
        """Save all necessary states, including message history."""
        self.__save_message_history()
