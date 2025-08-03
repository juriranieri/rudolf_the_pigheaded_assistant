# test_recording.py

import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import os

# --- Parameters ---
duration = 3  # seconds
sample_rate = 16000  # Hertz
channels = 1
output_filename = "test_recording.wav"

print("This script will test your audio setup.")
print(f"It will record for {duration} seconds, save it to '{output_filename}', and then attempt to play it back.")
print("-" * 20)

try:
    # 1. Record audio
    print(f"Starting {duration}-second recording...")
    myrecording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=channels, dtype='float32')
    sd.wait()  # Wait until recording is finished
    print("Recording finished.")
    print("%s" %myrecording)

    # 2. Save the recording to a file
    print(f"Saving recording to '{output_filename}'...")
    wav.write(output_filename, sample_rate, myrecording)
    print(f"File saved successfully to: {os.path.abspath(output_filename)}")

    # 3. Playback audio
    print("-" * 20)
    print("Now attempting to play back the recording...")
    sd.play(myrecording, sample_rate)
    sd.wait()  # Wait until playback is finished
    print("Playback finished.")
    print("-" * 20)
    print("Test complete. Please check the generated .wav file to see if audio was captured.")

except Exception as e:
    print(f"\nAn error occurred: {e}")
    print("Please ensure you have a working microphone and speakers.")
    print("On macOS, you might need to grant accessibility/microphone permissions to your terminal.")

