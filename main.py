
import pyttsx3
import json
import random
from vosk import Model, KaldiRecognizer
import pyaudio
import os
from memory import save_character, list_characters
from llm_npc import generate_npc_llm

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 180)

# Load Vosk voice recognition model
model_path = "vosk-model-small-en-us-0.15"
if not os.path.exists(model_path):
    print("Please download the Vosk model from https://alphacephei.com/vosk/models and extract it here.")
    exit()

model = Model(model_path)
recognizer = KaldiRecognizer(model, 16000)

# Setup microphone stream
mic = pyaudio.PyAudio()
stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
stream.start_stream()

# Text-to-speech helper
def speak(text):
    print("DM:", text)
    engine.say(text)
    engine.runAndWait()

# Dice roller
def roll_dice(command):
    try:
        parts = command.lower().split("d")
        num = int(parts[0]) if parts[0] else 1
        sides = int(parts[1])
        rolls = [random.randint(1, sides) for _ in range(num)]
        result = f"You rolled: {rolls} = {sum(rolls)}"
        return result
    except:
        return "Sorry, I couldn't understand the dice roll."

# Basic NPC generator
def generate_npc():
    names = ["Thargok", "Elandra", "Milo", "Seraphine"]
    traits = ["mysterious", "grumpy", "friendly", "deceptive"]
    roles = ["blacksmith", "barkeep", "ranger", "wizard"]
    npc = {
        "name": random.choice(names),
        "trait": random.choice(traits),
        "role": random.choice(roles)
    }
    save_character(npc)
    return f"{npc['name']} is a {npc['trait']} {npc['role']}."

# Command handler
def handle_command(text):
    text = text.lower()
    if "character" in text and "smart" in text:
        npc = generate_npc_llm()
        speak("Here's a detailed character.")
        return npc
    elif "character" in text or "npc" in text:
        return generate_npc()
    elif "roll" in text and "d" in text:
        return roll_dice(text.replace("roll ", ""))
    elif "list characters" in text or "recall characters" in text:
        return list_characters()
    elif "hello" in text:
        return "Hello adventurer! What would you like me to do?"
    elif "quit" in text or "exit" in text:
        speak("Goodbye!")
        exit()
    else:
        return "I'm not sure how to help with that yet."

# Start voice assistant
speak("Dungeon Master Assistant is ready.")

while True:
    print("Listening...")
    data = stream.read(4096, exception_on_overflow=False)

    if recognizer.AcceptWaveform(data):
        result = json.loads(recognizer.Result())
        text = result.get("text", "")
        if text:
            print(f"You said: {text}")
            response = handle_command(text)
            speak(response)