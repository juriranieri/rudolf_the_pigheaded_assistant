# src/main.py

import os
import sys

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from dotenv import load_dotenv

from core.assistant import Assistant


def main():
    """Main function."""
    load_dotenv()
    print("Hello, I am your personal assistant.")
    assistant = Assistant()
    assistant.start()


if __name__ == "__main__":
    main()
