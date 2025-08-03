I want to build an app that I run locally on my mac book, that helps me manage my work.

1. Voice/Text controls/input
- The app is controlled via speech (or as lifeline with text). There will be a keyword “Rudolf”. The app will silently listen to the audio input (using something like Picovoice Porcupine) and wakeup when that word is heard. After that word is heard, it will record the whole audio for the instructions, for at least 5 seconds. For improved performance, especially in noisy environments, we will integrate OpenAI Whisper. This is a powerful model that can be run locally, ensuring privacy and offline capabilities.
- The app has access to the desktop screen and can read what is "selected/underlined" with the cursor or what is in the main screen.
- It gives priority to what it is selected via the cursor, not the overall desktop. 


2. Given the provided context (commands, screen and selected content), it takes one of the following actions:
Create a TODO on Google Tasks, with the necessary context, including a link to the website/document that was used (when possible)

(We will add more)

## TODO

- [ ] Pre-train a custom hotword model for "Rudolf" using Picovoice Porcupine.
