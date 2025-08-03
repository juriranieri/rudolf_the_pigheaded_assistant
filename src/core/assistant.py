# src/core/assistant.py

import os
import threading
import google.generativeai as genai
import whisper
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import tempfile
from pynput import keyboard
import sys
import select
import datetime
import time

class Assistant:
    """Personal assistant class."""

    def __init__(self, mic_index=None):
        """Initializes the assistant."""
        api_key = os.getenv("PERSONAL_ASSISTANT_GEMINI_API_KEY")
        if not api_key:
            raise ValueError("PERSONAL_ASSISTANT_GEMINI_API_KEY not found in environment variables.")
        
        self.debug = os.getenv("PERSONAL_ASSISTANT_DEBUG", "false").lower() == "true"
        if self.debug:
            print("--- DEBUG MODE ENABLED ---")
            self.recordings_dir = "recordings"
            if not os.path.exists(self.recordings_dir):
                os.makedirs(self.recordings_dir)
            print(f"Recordings will be saved to: {self.recordings_dir}")

        print(f"Using Gemini API Key from .env file: {api_key[:4]}...{api_key[-4:]}")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        self.mic_index = mic_index
        self.whisper_model = whisper.load_model("base")
        self.recording = False
        self.listener = None
        self.stream = None
        self.frames = []
        self.sample_rate = 16000

    def transcribe_audio(self, file_path):
        """Transcribes audio using Whisper."""
        print(f"Transcribing audio file: {file_path}")
        result = self.whisper_model.transcribe(file_path)
        return result["text"]

    def _process_audio(self):
        """
        Processes the recorded audio frames, transcribes them,
        sends the text to the generative model, and prints the response.
        This method is designed to run in a separate thread to avoid blocking.
        """
        print("--- Entered _process_audio ---")
        try:
            if not self.frames:
                print("No audio recorded.")
                return

            captured_frames = self.frames
            self.frames = []
            
            print(f"Processing {len(captured_frames)} frames of audio.")
            recording = np.concatenate(captured_frames, axis=0)
            print(f"Final recording shape: {recording.shape}")

            audio_filepath = ""
            try:
                if self.debug:
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    audio_filepath = os.path.join(self.recordings_dir, f"recording_{timestamp}.wav")
                    print(f"Writing audio to permanent file: {audio_filepath}")
                    wav.write(audio_filepath, self.sample_rate, recording)
                else:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio_file:
                        audio_filepath = tmp_audio_file.name
                    print(f"Writing audio to temporary file: {audio_filepath}")
                    wav.write(audio_filepath, self.sample_rate, recording)

                print("--- Starting transcription ---")
                user_input = self.transcribe_audio(audio_filepath)
                print(f"--- Transcription result: '{user_input}' ---")
                
                sys.stdout.flush()
                print(f"> {user_input}")
                sys.stdout.flush()
                
                if user_input and user_input.strip():
                    print("--- Generating response from model ---")
                    response = self.model.generate_content(user_input)
                    print("--- Response received ---")
                    print(response.text)
                else:
                    print("--- Transcription is empty, skipping model generation ---")
            
            finally:
                if not self.debug and audio_filepath and os.path.exists(audio_filepath):
                    print(f"--- Deleting temporary file: {audio_filepath} ---")
                    os.remove(audio_filepath)

        except Exception as e:
            print(f"An error occurred in the audio processing thread: {e}")
            import traceback
            traceback.print_exc()

    def start_recording(self):
        if self.recording:
            return
        
        self.recording = True
        self.frames = []
        print("Recording started... Press 'r' again to stop.")

        def audio_callback(indata, frame_count, time_info, status):
            if status:
                print(status, file=sys.stderr)
            self.frames.append(indata.copy())

        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            callback=audio_callback,
            device=self.mic_index
        )
        self.stream.start()

    def stop_recording(self):
        if not self.recording:
            return

        print("Recording stopped. Processing...")
        self.stream.stop()
        self.stream.close()
        self.recording = False
        
        # Give the stream a moment to close and flush all buffers.
        time.sleep(0.1)

        threading.Thread(target=self._process_audio).start()

    def on_press(self, key):
        try:
            if key.char == 'r':
                if not self.recording:
                    self.start_recording()
                else:
                    self.stop_recording()
        except AttributeError:
            pass

    def start(self):
        """Starts the assistant."""
        print("Assistant started. Press 'r' to start/stop recording, type 'exit' to quit.")

        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

        try:
            while True:
                if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                    typed_input = sys.stdin.readline().strip()
                    if typed_input.lower() == "exit":
                        break
                    if typed_input:
                        response = self.model.generate_content(typed_input)
                        print(response.text)
        except (KeyboardInterrupt, EOFError):
            pass
        finally:
            if self.listener:
                self.listener.stop()
            print("\nAssistant stopped.")

    def stop(self):
        if self.listener:
            self.listener.stop()
