import openai
import speech_recognition as sr
import edge_tts
import sounddevice as sd
import soundfile as sf
from datetime import datetime
from dotenv import load_dotenv
from os import getenv, path
from json import load, dump, JSONDecodeError

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
        self.tts_model = None

    def initialize(self, user_input_service: str = None, stt_duration: float = None, mic_index: int = None,
                   chatbot_service: str = None, chatbot_model: str = None, chatbot_temperature: float = None, personality_file: str = None,
                   tts_service: str = None, output_device=None, tts_voice: str = None, tts_model: str = None) -> None:
        load_dotenv()

        self.update_user_input(user_input_service=user_input_service, stt_duration=stt_duration)
        self.mic = sr.Microphone(device_index=mic_index)
        self.recogniser = sr.Recognizer()

        # Set up OpenAI API configuration
        openai.api_key = getenv("OPENAI_API_KEY")
        openai.api_base = "https://api.zukijourney.com/v1"  # Custom API Base URL

        if not openai.api_key:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in your environment variables.")

        self.update_chatbot(service=chatbot_service, model=chatbot_model, temperature=chatbot_temperature, personality_file=personality_file)
        self.__load_chatbot_data()

        self.update_tts(service=tts_service, output_device=output_device, voice=tts_voice, model=tts_model)

    def update_user_input(self, user_input_service:str = 'whisper', stt_duration:float = 0.5) -> None:
        self.user_input_service = user_input_service or 'whisper'
        self.stt_duration = stt_duration or 0.5

    def update_chatbot(self, service:str = 'openai', model:str = 'gpt-3.5-turbo', temperature:float = 0.5, personality_file:str = 'personality.txt') -> None:
        self.chatbot_service = service or 'openai'
        self.chatbot_model = model or 'gpt-3.5-turbo'
        self.chatbot_temperature = temperature or 0.5
        self.chatbot_personality_file = personality_file or 'personality.txt'

    def update_tts(self, service:str = 'edge', output_device=None, voice:str = None, model:str = None) -> None:
        self.tts_service = service or 'edge'
        self.tts_voice = voice or 'en-US-JennyNeural'  # Default voice for Edge TTS

        if output_device is not None:
            try:
                sd.check_output_settings(output_device)
                sd.default.samplerate = 44100
                sd.default.device = output_device
            except sd.PortAudioError as e:
                print(f"Invalid output device: {e}")
                print(sd.query_devices())
                raise

    def get_audio_devices(self):
        return sd.query_devices()

    def get_user_input(self, service:str = None, stt_duration:float = None) -> str:
        service = self.user_input_service if service is None else service
        stt_duration = self.stt_duration if stt_duration is None else stt_duration

        supported_stt_services = ['whisper', 'google']
        supported_text_services = ['console']

        result = ""
        if service in supported_stt_services:
            result = self.__recognise_speech(service, duration=stt_duration)
        elif service in supported_text_services:
            result = self.__get_text_input(service)
        else:
            raise ValueError(f"{service} service doesn't support. Please, use one of the following services: {supported_stt_services + supported_text_services}")
        
        return result

    def get_chatbot_response(self, prompt:str, service:str = None, model:str = None, temperature:float = None) -> str:
        service = self.chatbot_service if service is None else service
        model = self.chatbot_model if model is None else model
        temperature = self.chatbot_temperature if temperature is None else temperature

        supported_chatbot_services = ['openai', 'test']

        result = ""
        if service == 'openai':
            result = self.__get_openai_response(prompt, model=model, temperature=temperature)
        elif service == 'test':
            result = "This is test answer from Waifu. Nya kawaii, senpai!"
        else:
            raise ValueError(f"{service} service doesn't support. Please, use one of the following services: {supported_chatbot_services}")
        
        return result

    # Use Edge TTS for speech output (async method)
    async def tts_say(self, text:str, service:str = None, voice:str = None, model:str = None) -> None:
        service = self.tts_service if service is None else service
        voice = self.tts_voice if voice is None else voice

        if service == 'edge':
            await self.__edge_tts_generate(text, voice)

        data, fs = sf.read("./Assets/output.mp3")
        sd.play(data, fs)
        sd.wait()

    # Asynchronous function to generate speech using Edge TTS
    async def __edge_tts_generate(self, text:str, voice:str) -> None:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save("./Assets/output.mp3")

    async def conversation_cycle(self) -> None:
        user_input = self.get_user_input()  # Get user input synchronously
        response = self.get_chatbot_response(user_input)  # Get chatbot response synchronously
        await self.tts_say(response)  # Await the asynchronous TTS method
        print(f"User: {user_input}\nAssistant: {response}")

    def __get_openai_response(self, prompt:str, model:str, temperature:float) -> str:
        self.__add_message('user', prompt)
        messages = self.context + self.message_history

        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature, 
        )
        response = response.choices[0].message["content"]

        self.__add_message('assistant', response)
        self.__update_message_history()

        return response

    # def __add_message(self, role:str, content:str) -> None:
    #     self.message_history.append({'role': role, 'content': content})

    # def __load_chatbot_data(self, file_name:str = None) -> None:
    #     file_name = self.chatbot_personality_file if file_name is None else file_name

    #     with open(file_name, 'r') as f:
    #         personality = f.read()
    #     self.context = [{'role': 'system', 'content': personality}]

    #     if path.isfile('./message_history.txt'):
    #         with open('message_history.txt', 'r') as f:
    #             try:
    #                 self.message_history = load(f)
    #             except JSONDecodeError:
    #                 pass

    # def __update_message_history(self) -> None:
    #     with open('message_history.txt', 'w') as f:
    #         dump(self.message_history, f)

    # Dengan Timestamp dan Newline

    def __add_message(self, role: str, content: str) -> None:
        # Add a timestamp and a newline to each message
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")  # Format: [YYYY-MM-DD HH:MM:SS]
        formatted_content = f"{timestamp} {content}\n"  # Add newline at the end
        self.message_history.append({'role': role, 'content': formatted_content})

    def __load_chatbot_data(self, file_name: str = None) -> None:
        file_name = self.chatbot_personality_file if file_name is None else file_name

        with open(file_name, 'r') as f:
            personality = f.read()
        self.context = [{'role': 'system', 'content': personality}]

        if path.isfile('./Assets/message_history.txt'):
            with open('./Assets/message_history.txt', 'r') as f:
                try:
                    self.message_history = load(f)
                except JSONDecodeError:
                    pass

    def __update_message_history(self) -> None:
        with open('./Assets/message_history.txt', 'w') as f:
            # Save messages with consistent formatting
            dump(self.message_history, f, indent=4)

    def __get_text_input(self, service:str) -> str:
        user_input = ""
        if service == 'console':
            user_input = input('\n\33[42m' + "User:" + '\33[0m' + " ")
        return user_input

    def __recognise_speech(self, service:str, duration:float) -> str:
        with self.mic as source:
            print('(Start listening)')
            self.recogniser.adjust_for_ambient_noise(source, duration=duration)
            audio = self.recogniser.listen(source)
            print('(Stop listening)')

            result = ""
            try:
                if service == 'whisper':
                    result = self.__whisper_sr(audio)
                elif service == 'google':
                    result = self.recogniser.recognize_google(audio)
            except Exception as e:
                print(f"Exception: {e}")
        return result

    def __whisper_sr(self, audio) -> str:
        with open('./Assets/speech.wav', 'wb') as f:
            f.write(audio.get_wav_data())
            audio_file = open('./Assets/speech.wav', 'rb')
            transcript = openai.Audio.transcribe(model="whisper-1", file=audio_file)
        return transcript['text']

# import openai
# import speech_recognition as sr
# # from gtts import gTTS
# # from elevenlabs import generate, save, set_api_key, voices
# import edge_tts
# import sounddevice as sd
# import soundfile as sf

# from dotenv import load_dotenv
# from os import getenv, path
# from json import load, dump, JSONDecodeError
# import asyncio

# class Waifu:
#     def __init__(self) -> None:
#         self.mic = None
#         self.recogniser = None

#         self.user_input_service = None
#         self.stt_duration = None

#         self.chatbot_service = None
#         self.chatbot_model = None
#         self.chatbot_temperature = None
#         self.chatbot_personality_file = None

#         self.message_history = []
#         self.context = []

#         self.tts_service = None
#         self.tts_voice = None
#         self.tts_model = None

#     def initialize(self, user_input_service: str = None, stt_duration: float = None, mic_index: int = None,
#                    chatbot_service: str = None, chatbot_model: str = None, chatbot_temperature: float = None, personality_file: str = None,
#                    tts_service: str = None, output_device=None, tts_voice: str = None, tts_model: str = None) -> None:
#         load_dotenv()

#         self.update_user_input(user_input_service=user_input_service, stt_duration=stt_duration)
#         self.mic = sr.Microphone(device_index=mic_index)
#         self.recogniser = sr.Recognizer()

#         # Set up OpenAI API configuration
#         openai.api_key = getenv("OPENAI_API_KEY")
#         openai.api_base = "https://api.zukijourney.com/v1"  # Custom API Base URL

#         if not openai.api_key:
#             raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in your environment variables.")

#         self.update_chatbot(service=chatbot_service, model=chatbot_model, temperature=chatbot_temperature, personality_file=personality_file)
#         self.__load_chatbot_data()

#         self.update_tts(service=tts_service, output_device=output_device, voice=tts_voice, model=tts_model)

#     # Rest of the class methods remain unchanged...

#     def update_user_input(self, user_input_service:str = 'whisper', stt_duration:float = 0.5) -> None:
#         if user_input_service:
#             self.user_input_service = user_input_service
#         elif self.user_input_service is None:
#             self.user_input_service = 'whisper'

#         if stt_duration:
#             self.stt_duration = stt_duration
#         elif self.stt_duration is None:
#             self.stt_duration = 0.5

#     def update_chatbot(self, service:str = 'openai', model:str = 'gpt-3.5-turbo', temperature:float = 0.5, personality_file:str = 'personality.txt') -> None:
#         if service:
#             self.chatbot_service = service
#         elif self.chatbot_service is None:
#             self.chatbot_service = 'openai'

#         if model:
#             self.chatbot_model = model
#         elif self.chatbot_model is None:
#             self.chatbot_model = 'gpt-3.5-turbo'

#         if temperature:
#             self.chatbot_temperature = temperature
#         elif self.chatbot_temperature is None:
#             self.chatbot_temperature = 0.5

#         if personality_file:
#             self.chatbot_personality_file = personality_file
#         elif self.chatbot_personality_file is None:
#             self.chatbot_personality_file = 'personality.txt'

#     # def update_tts(self, service:str = 'google', output_device = None, voice:str = None, model:str = None) -> None:
#     #     if service:
#     #         self.tts_service = service
#     #     elif self.tts_service is None:
#     #         self.tts_service = 'google'

#     #     set_api_key(getenv('ELEVENLABS_API_KEY'))

#     #     if voice:
#     #         self.tts_voice = voice
#     #     elif self.tts_voice is None:
#     #         self.tts_voice = 'Elli'

#     #     if model:
#     #         self.tts_model = model
#     #     elif self.tts_model is None:
#     #         self.tts_model = 'eleven_multilingual_v2'

#     #     if output_device is not None:
#     #         try:
#     #             sd.check_output_settings(output_device)
#     #             sd.default.samplerate = 44100
#     #             sd.default.device = output_device
#     #         except sd.PortAudioError:
#     #             print("Invalid output device! Make sure you've launched VB-Cable.\n",
#     #                    "Check that you've choosed the correct output_device in initialize method.\n", 
#     #                    "From the list below, select device that starts with 'CABLE Input' and set output_device to it's id in list.\n",
#     #                    "If you still have this error try every device that starts with 'CABLE Input'. If it doesn't help please create GitHub issue.")
#     #             print(sd.query_devices())
#     #             raise

#     def update_tts(self, service: str = 'edge', output_device=None, voice: str = None, model: str = None) -> None:
#         self.tts_service = service or 'edge'
#         self.tts_voice = voice or 'en-US-JennyNeural'  # Default voice for Edge TTS

#         if output_device is not None:
#             try:
#                 sd.check_output_settings(output_device)
#                 sd.default.samplerate = 44100
#                 sd.default.device = output_device
#             except sd.PortAudioError as e:
#                 print(f"Invalid output device: {e}")
#                 print(sd.query_devices())
#                 raise

#     def get_audio_devices(self):
#         return sd.query_devices()

#     def get_user_input(self, service:str = None, stt_duration:float = None) -> str:
#         service = self.user_input_service if service is None else service
#         stt_duration = self.stt_duration if stt_duration is None else stt_duration

#         supported_stt_services = ['whisper', 'google']
#         supported_text_services = ['console']

#         result = ""
#         if service in supported_stt_services:
#             result = self.__recognise_speech(service, duration=stt_duration)
#         elif service in supported_text_services:
#             result = self.__get_text_input(service)
#         else:
#             raise ValueError(f"{service} servise doesn't supported. Please, use one of the following services: {supported_stt_services + supported_text_services}")
        
#         return result

#     def get_chatbot_response(self, prompt:str, service:str = None, model:str = None, temperature:float = None) -> str:
#         service = self.chatbot_service if service is None else service
#         model = self.chatbot_model if model is None else model
#         temperature = self.chatbot_temperature if temperature is None else temperature

#         supported_chatbot_services = ['openai', 'test']

#         result = ""
#         if service == 'openai':
#             result = self.__get_openai_response(prompt, model=model, temperature=temperature)
#         elif service == 'test':
#             result = "This is test answer from Waifu. Nya kawaii, senpai!"
#         else:
#             raise ValueError(f"{service} servise doesn't supported. Please, use one of the following services: {supported_chatbot_services}")
        
#         return result

#     # def tts_say(self, text:str, service:str = None, voice:str = None, model:str = None) -> None:
#     #     service = self.tts_service if service is None else service
#     #     voice = self.tts_voice if voice is None else voice
#     #     model = self.tts_model if model is None else model

#     #     supported_tts_services = ['google', 'elevenlabs', 'console']

#     #     if service not  in supported_tts_services:
#     #         raise ValueError(f"{service} servise doesn't supported. Please, use one of the following services: {supported_tts_services}")
        


#     #     if service == 'google':
#     #         gTTS(text=text, lang='en', slow=False, lang_check=False).save('output.mp3')
#     #     elif service == 'elevenlabs':
#     #         self.__elevenlabs_generate(text=text, voice=voice, model=model)

#     #     elif service == 'console':
#     #         print('\n\33[7m' + "Waifu:" + '\33[0m' + f' {text}')
#     #         return

#     #     data, fs = sf.read('output.mp3')
#     #     sd.play(data, fs)
#     #     sd.wait()

#     async def tts_say(self, text: str, service: str = None, voice: str = None, model: str = None) -> None:
#         service = self.tts_service if service is None else service
#         voice = self.tts_voice if voice is None else voice

#         if service == 'edge':
#             await self.__edge_tts_generate(text, voice)

#         data, fs = sf.read("output.mp3")
#         sd.play(data, fs)
#         sd.wait()

#     def conversation_cycle(self) -> dict:
#         input = self.get_user_input()

#         response = self.get_chatbot_response(input)

#         self.tts_say(response)
        
#         return dict(user = input, assistant = response)

#     def __get_openai_response(self, prompt:str, model:str, temperature:float) -> str:
#         self.__add_message('user', prompt)
#         messages = self.context + self.message_history

#         response = openai.ChatCompletion.create(
#             model=model,
#             messages=messages,
#             temperature=temperature, 
#         )
#         response = response.choices[0].message["content"]

#         self.__add_message('assistant', response)
#         self.__update_message_history()

#         return response

#     def __add_message(self, role:str, content:str) -> None:
#         self.message_history.append({'role': role, 'content': content})

#     def __load_chatbot_data(self, file_name:str = None) -> None:
#         file_name = self.chatbot_personality_file if file_name is None else file_name

#         with open(file_name, 'r') as f:
#             personality = f.read()
#         self.context = [{'role': 'system', 'content': personality}]

#         if path.isfile('./message_history.txt'):
#             with open('message_history.txt', 'r') as f:
#                 try:
#                     self.message_history = load(f)
#                 except JSONDecodeError:
#                     pass

#     def __update_message_history(self) -> None:
#         with open('message_history.txt', 'w') as f:
#                 dump(self.message_history, f)

#     def __get_text_input(self, service:str) -> str:
#         user_input = ""
#         if service == 'console':
#             user_input = input('\n\33[42m' + "User:" + '\33[0m' + " ")
#         return user_input

#     # def __elevenlabs_generate(self, text:str, voice:str, model:str, filename:str='output.mp3'):
#     #     audio = generate(
#     #              text=text,
#     #              voice=voice,
#     #              model=model
#     #             )
#     #     save(audio, filename)

#     async def __edge_tts_generate(self, text: str, voice: str) -> None:
#         communicate = edge_tts.Communicate(text, voice)
#         await communicate.save("output.mp3")

#     def __recognise_speech(self, service:str, duration:float) -> str:
#         with self.mic as source:
#             print('(Start listening)')
#             self.recogniser.adjust_for_ambient_noise(source, duration=duration)
#             audio = self.recogniser.listen(source)
#             print('(Stop listening)')

#             result = ""
#             try:
#                 if service == 'whisper':
#                     result = self.__whisper_sr(audio)
#                 elif service == 'google':
#                     result = self.recogniser.recognize_google(audio)
#             except Exception as e:
#                 print(f"Exeption: {e}")
#         return result

#     def __whisper_sr(self, audio) -> str:
#         with open('speech.wav', 'wb') as f:
#             f.write(audio.get_wav_data())
#             audio_file = open('speech.wav', 'rb')
#             transcript = openai.Audio.transcribe(model="whisper-1", file=audio_file)
#         return transcript['text']

# def main():
#     w = Waifu()
#     w.initialize(user_input_service='console', 
#                  chatbot_service='test', 
#                  tts_service='google', output_device=8)

#     w.conversation_cycle()

#     #while True:
#     #    w.conversation_cycle()

# async def conversation_cycle(self) -> None:
#     # Get user input
#     user_input = self.get_user_input()  # This is synchronous
#     # Get chatbot response
#     response = self.get_chatbot_response(user_input)  # This is synchronous
#     # Say the response asynchronously
#     await self.tts_say(response)  # Await the async TTS method

#     # Log or store the conversation (if needed)
#     print(f"User: {user_input}\nAssistant: {response}")



# if __name__ == "__main__":
#     main()