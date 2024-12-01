import asyncio
import customtkinter as ctk
from Controller.waifu import Waifu


class WaifuGUI:
    def __init__(self, root, waifu):
        self.root = root
        self.waifu = waifu
        self.root.title("Waifu Chat")
        self.root.geometry("700x600")
        ctk.set_appearance_mode("Dark")  # Set dark mode
        ctk.set_default_color_theme("blue")  # Use a blue color theme

        # Chat display box
        self.chat_display = ctk.CTkTextbox(self.root, wrap="word", state="disabled")
        self.chat_display.grid(row=0, column=0, padx=20, pady=10, columnspan=3, sticky="nsew")

        # Input frame
        self.input_frame = ctk.CTkFrame(self.root)
        self.input_frame.grid(row=1, column=0, padx=20, pady=10, columnspan=3, sticky="ew")

        # User input box
        self.user_input = ctk.CTkEntry(self.input_frame, placeholder_text="Type your message...")
        self.user_input.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="ew")
        self.user_input.bind("<Return>", lambda event: self.send_message())

        # Buttons frame for alignment
        self.buttons_frame = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        self.buttons_frame.grid(row=0, column=1, padx=(10, 0), pady=5, sticky="ew")

        # Buttons
        self.send_button = ctk.CTkButton(self.buttons_frame, text="Send", command=self.send_message)
        self.send_button.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        self.voice_button = ctk.CTkButton(self.buttons_frame, text="🎤 Voice", command=self.handle_voice_input)
        self.voice_button.grid(row=0, column=1, padx=(5, 5), sticky="ew")

        self.talking_button = ctk.CTkButton(self.buttons_frame, text="🗣️ Talking Mode", command=self.toggle_talking_mode)
        self.talking_button.grid(row=0, column=2, padx=(5, 0), sticky="ew")

        # Logs display
        self.logs_display = ctk.CTkTextbox(self.root, height=100, wrap="word", state="disabled")
        self.logs_display.grid(row=2, column=0, padx=20, pady=10, columnspan=3, sticky="nsew")

        # Configure grid weight for responsiveness
        self.root.grid_rowconfigure(0, weight=1)  # Chat area expands
        self.root.grid_rowconfigure(1, weight=0, minsize=40)  # Fixed height for buttons and input field row
        self.root.grid_rowconfigure(2, weight=0)  # Logs area stays at a fixed height

        # Ensure columns expand/shrink proportionally
        self.root.grid_columnconfigure(0, weight=1)  # Chat and logs expand proportionally
        self.root.grid_columnconfigure(1, weight=0)  # Control buttons remain fixed width
        self.root.grid_columnconfigure(2, weight=0)  # Control buttons remain fixed width

    def handle_voice_input(self):
        """Handles capturing and processing voice input."""
        try:
            user_input = self.waifu.get_user_input()
            if user_input:
                self.log_message(f"Voice input detected: {user_input}")
                asyncio.create_task(self.handle_waifu_response(user_input))
        except Exception as e:
            self.log_message(f"Error during voice input: {e}")

    def toggle_talking_mode(self):
        """Toggles the talking mode on or off."""
        self.talking_mode = not self.talking_mode
        if self.talking_mode:
            self.log_message("Talking mode activated.")
            asyncio.create_task(self.start_talking_mode())
            self.talking_button.configure(text="🛑 Stop Talking")
        else:
            self.log_message("Talking mode deactivated.")
            self.talking_button.configure(text="🗣️ Talking Mode")

    async def start_talking_mode(self):
        """Continuously listens and processes voice input in talking mode."""
        while self.talking_mode:
            try:
                user_input = self.waifu.get_user_input()
                if user_input:
                    self.log_message(f"Voice input in talking mode: {user_input}")
                    await self.handle_waifu_response(user_input)
            except Exception as e:
                self.log_message(f"Error in talking mode: {e}")
            await asyncio.sleep(0.5)

    def send_message(self):
        """Handles sending a message to Waifu."""
        user_input = self.user_input.get().strip()
        if user_input:
            self.user_input.delete(0, ctk.END)
            asyncio.create_task(self.handle_waifu_response(user_input))

    async def handle_waifu_response(self, user_input):
        """Handles Waifu's response asynchronously."""
        try:
            self.display_chat("You", user_input)
            self.log_message(f"User input: {user_input}")

            response = self.waifu.get_chatbot_response(user_input)
            await self.waifu.tts_say(response)

            self.display_chat("Waifu", response)
            self.log_message(f"Waifu response: {response}")
        except Exception as e:
            self.log_message(f"Error in handling response: {e}")

    def display_chat(self, sender, message):
        """Displays a message in the chatbox."""
        self.chat_display.configure(state="normal")
        self.chat_display.insert(ctk.END, f"{sender}: {message}\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see(ctk.END)

    def log_message(self, message):
        """Logs a message in the logs display."""
        self.logs_display.configure(state="normal")
        self.logs_display.insert(ctk.END, f"{message}\n")
        self.logs_display.configure(state="disabled")
        self.logs_display.see(ctk.END)
