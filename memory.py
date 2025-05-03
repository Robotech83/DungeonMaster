# memory.py
import json
import os

CHARACTER_FILE = "characters.json"

def save_character(character):
    characters = []
    if os.path.exists(CHARACTER_FILE):
        with open(CHARACTER_FILE, 'r') as f:
            characters = json.load(f)
    characters.append(character)
    with open(CHARACTER_FILE, 'w') as f:
        json.dump(characters, f, indent=4)

def list_characters():
    if not os.path.exists(CHARACTER_FILE):
        return "No characters saved yet."
    with open(CHARACTER_FILE, 'r') as f:
        characters = json.load(f)
    return "\n".join([f"{c['name']}, a {c['trait']} {c['role']}" for c in characters])
