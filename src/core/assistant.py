# src/core/assistant.py

import os
import threading
import google.generativeai as genai
import whisper

import numpy as np
import scipy.io.wavfile as wav
import tempfile
import sys
import select
import datetime
import time
import pvporcupine
import pyaudio
import struct
from core.os_utils import get_selected_text, take_screenshot

class Assistant:
    """Personal assistant class."""

    def __init__(self, mic_index=None):
        """Initializes the assistant."""
        self.access_key = os.getenv("PICOVOICE_ACCESS_KEY")
        if not self.access_key:
            raise ValueError("PICOVOICE_ACCESS_KEY not found in environment variables.")

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
        self.model = genai.GenerativeModel("gemini-1.5-pro")
        self.mic_index = mic_index
        self.whisper_model = whisper.load_model("base")
        self.recording = False
        self.stream = None
        self.frames = []
        self.sample_rate = 16000
        self.channels = 1 # Mono audio
        self.silence_threshold = 0.01  # Silence threshold
        self.silence_duration = 2  # Seconds of silence to stop recording
        self.pa = pyaudio.PyAudio()
        self.porcupine = None
        self.audio_stream = None # This will be the single, main audio stream
        self.selected_text = None
        self.screenshot = None

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
                    if self.selected_text:
                        user_input = f"{user_input}\n\nSelected text:\n{self.selected_text}"

                    content = [user_input]
                    if self.screenshot:
                        content.append(self.screenshot)

                    print("--- Generating response from model ---")
                    response = self.model.generate_content(content)
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

    


    

    def start(self):
        """Starts the assistant."""
        print("Assistant started. Say 'Terminator' to start recording.")
        try:
            self.porcupine = pvporcupine.create(
                access_key=self.access_key,
                keywords=['terminator']
            )

            def audio_callback(in_data, frame_count, time_info, status):
                if status:
                    print(status, file=sys.stderr)

                pcm = struct.unpack_from("h" * frame_count, in_data)
                keyword_index = self.porcupine.process(pcm)

                if keyword_index >= 0:
                    print("Wake word detected!")
                    self.recording = True
                    self.frames = [] # Clear frames for new recording
                    self.silence_frames = 0 # Reset silence counter
                    self.recording_start_time = time.time() # Start recording timer

                    # Get selected text
                    self.selected_text = get_selected_text()
                    if self.selected_text:
                        print(f"Follow-up instruction for the selected text: '{self.selected_text}'")

                    # Take screenshot
                    self.screenshot = take_screenshot()
                    if self.screenshot:
                        print("Screenshot taken.")

                if self.recording:
                    audio_data = np.frombuffer(in_data, dtype=np.int16)
                    self.frames.append(audio_data)

                    # Check for 3-second limit
                    if time.time() - self.recording_start_time > 3:
                        print("3 seconds recorded. Stopping recording.")
                        self.recording = False
                        threading.Thread(target=self._process_audio).start()
                    else:
                        # Silence detection
                        if np.abs(audio_data).mean() < self.silence_threshold:
                            self.silence_frames += 1
                        else:
                            self.silence_frames = 0

                        if self.silence_frames > self.sample_rate / frame_count * self.silence_duration:
                            print("Silence detected. Stopping recording.")
                            self.recording = False
                            threading.Thread(target=self._process_audio).start()

                return (in_data, pyaudio.paContinue)

            self.audio_stream = self.pa.open(
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.porcupine.frame_length,
                stream_callback=audio_callback
            )

            self.audio_stream.start_stream()
            print("Listening for wake word...")

            # Keep the main thread alive
            while self.audio_stream.is_active():
                time.sleep(0.1)

        except (KeyboardInterrupt, EOFError):
            pass
        finally:
            self.stop()

    def stop(self):
        print("\nAssistant stopped.")
        if self.porcupine is not None:
            self.porcupine.delete()
        if self.audio_stream is not None:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
        if self.pa is not None:
            self.pa.terminate()
        


if __name__ == "__main__":
    assistant = Assistant()
    assistant.start()