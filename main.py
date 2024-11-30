import asyncio
from Controller.waifu import Waifu

def main():
    try:
        waifu = Waifu()

        waifu.initialize(
            user_input_service='whisper',       # Speech-to-text service
            stt_duration=0.5,                   # Default duration for STT adjustments
            mic_index=None,                     # None will auto-select the default microphone
            
            chatbot_service='openai',
            chatbot_model='gpt-3.5-turbo',      # Default OpenAI model
            chatbot_temperature=0.7,
            personality_file='./Assets/personality.txt',
            
            tts_service='edge',                 # Edge TTS service
            output_device=12,                   # Audio output device
            tts_voice='id-ID-GadisNeural'       # Pilihan Voice Over, list ada di file Voice Over Sheet.txt
        )

        # Conversation Loop
        while True:
            asyncio.run(waifu.conversation_cycle())  # Use asyncio.run to handle async methods

    except KeyboardInterrupt:
        print("Exiting...")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()


# from waifu import Waifu
# import asyncio

# def main():
#     try:
#         # Create an instance of Waifu
#         waifu = Waifu()

#         # Initialize Waifu with desired parameters
#         waifu.initialize(
#             user_input_service='whisper',       # Speech-to-text service
#             stt_duration=0.5,                   # Default duration for STT adjustments
#             mic_index=None,                     # None will auto-select the default microphone
            
#             chatbot_service='openai',           # Use OpenAI for chatbot responses
#             chatbot_model='gpt-3.5-turbo',      # Default OpenAI model
#             chatbot_temperature=0.7,            # Creative response style
#             personality_file='personality.txt', # Personality file
            
#             # Elevenlabs TTS

#             # tts_service='elevenlabs',           # ElevenLabs for text-to-speech
#             # output_device=12,                   # Audio output device
#             # tts_voice='Elli',                   # Replace with a valid voice from ElevenLabs
#             # tts_model="eleven_multilingual_v2"  

#             # Edge TTS

#             tts_service='edge',
#             output_device=12,
#             tts_voice='jv-ID-SitiNeural'
#         )

#         # Start the conversation loop
#         while True:
#             asyncio.run(waifu.conversation_cycle())  # Use asyncio.run for async conversation_cycle

#     except Exception as e:
#         print(f"An error occurred: {e}")

# if __name__ == "__main__":
#     main()
