# src/core/assistant.py

import os
import google.generativeai as genai


class Assistant:
    """Personal assistant class."""

    def __init__(self):
        """Initializes the assistant."""
        api_key = os.getenv("PERSONAL_ASSISTANT_GEMINI_API_KEY")
        if not api_key:
            raise ValueError("PERSONAL_ASSISTANT_GEMINI_API_KEY not found in environment variables.")
        
        print(f"Using Gemini API Key from .env file: {api_key[:4]}...{api_key[-4:]}")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def start(self):
        """Starts the assistant."""
        print("Assistant started.")
        while True:
            user_input = input("> ")
            if user_input.lower() == "exit":
                break
            response = self.model.generate_content(user_input)
            print(response.text)
