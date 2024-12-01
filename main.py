import asyncio
import customtkinter as ctk
from Controller.waifu import Waifu
from Controller.waifuGUI import WaifuGUI

def main():
    """Main function to initialize and run the Waifu Chat application."""
    try:
        # Initialize Waifu chatbot
        waifu = Waifu()
        waifu.initialize(
            user_input_service='whisper',
            stt_duration=0.5,
            mic_index=None,
            chatbot_service='openai',
            chatbot_model='gpt-3.5-turbo',
            chatbot_temperature=0.7,
            personality_file='./Assets/personality.txt',
            tts_service='edge',
            output_device=12,
            tts_voice='id-ID-GadisNeural'
        )
        print("Waifu successfully initialized!")

        # Initialize and start the CustomTkinter GUI
        root = ctk.CTk()
        gui = WaifuGUI(root, waifu)

        # Run the asyncio event loop with the GUI
        asyncio.get_event_loop().run_until_complete(root.mainloop())

    except Exception as e:
        print(f"Error during initialization or runtime: {e}")

if __name__ == "__main__":
    main()
