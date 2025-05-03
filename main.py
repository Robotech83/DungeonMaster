import openai
import speech_recognition as sr
import pyttsx3
import json
from abc import ABC, abstractmethod

# Configuration
GPT_MODEL = "gpt-3.5-turbo"
WAKE_WORD = "hey dm"

class GPTClient:
    def __init__(self, api_key):
        openai.api_key = api_key
        
    def generate_content(self, prompt, max_tokens=500):
        try:
            response = openai.ChatCompletion.create(
                model=GPT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            return f"Error generating content: {str(e)}"

class VoiceAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.engine = pyttsx3.init()
        
    def listen(self):
        with self.microphone as source:
            print("Listening...")
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)
            
        try:
            return self.recognizer.recognize_google(audio).lower()
        except sr.UnknownValueError:
            return ""
        except Exception as e:
            print(f"Error in speech recognition: {e}")
            return ""

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

class ContentGenerator(ABC):
    def __init__(self, gpt_client):
        self.gpt = gpt_client
    
    @abstractmethod
    def generate_prompt(self, parameters):
        pass
    
    @abstractmethod
    def parse_response(self, response):
        pass

class CharacterGenerator(ContentGenerator):
    def generate_prompt(self, parameters):
        return f"""
        Generate a detailed D&D 5e character with:
        - Race: {parameters.get('race', 'random')}
        - Class: {parameters.get('class', 'random')}
        - Background: {parameters.get('background', 'random')}
        Include ability scores (using standard array), equipment, personality traits, and bonds.
        Format as JSON with keys: name, race, class, level, stats, equipment, background, personality, bonds.
        """
    
    def parse_response(self, response):
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return response

class NPCGenerator(ContentGenerator):
    def generate_prompt(self, parameters):
        return f"""
        Create a D&D NPC with:
        - Role: {parameters.get('role', 'random')}
        - Alignment: {parameters.get('alignment', 'random')}
        - Secret: {parameters.get('secret', 'random')}
        Include physical description, personality quirks, motivations, and plot hooks.
        Format as JSON with keys: name, race, occupation, alignment, description, personality, motivations, plot_hooks.
        """
    
    def parse_response(self, response):
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return response

class MapGenerator(ContentGenerator):
    def generate_prompt(self, parameters):
        return f"""
        Design a {parameters.get('location', 'dungeon')} map with:
        - Size: {parameters.get('size', 'medium')}
        - Key landmarks
        - Environmental hazards
        - Hidden secrets
        Include possible encounters and loot locations.
        Format as JSON with keys: location_type, map_description, landmarks, hazards, secrets, encounters, loot.
        """
    
    def parse_response(self, response):
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return response

class QuestGenerator(ContentGenerator):
    def generate_prompt(self, parameters):
        return f"""
        Create a {parameters.get('quest_type', 'side')} quest:
        - Difficulty: {parameters.get('difficulty', 'medium')}
        - Length: {parameters.get('length', '3 encounters')}
        Include NPC involvement, moral dilemmas, and multiple resolution paths.
        Format as JSON with keys: quest_name, quest_type, objectives, npcs_involved, rewards, complications, resolution_options.
        """
    
    def parse_response(self, response):
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return response

class DnDAssistant:
    def __init__(self, api_key):
        self.gpt_client = GPTClient(api_key)
        self.voice = VoiceAssistant()
        self.generators = {
            "character": CharacterGenerator(self.gpt_client),
            "npc": NPCGenerator(self.gpt_client),
            "map": MapGenerator(self.gpt_client),
            "quest": QuestGenerator(self.gpt_client)
        }
        
    def process_command(self, command):
        command = command.lower()
        if "character" in command:
            return self.generate_content("character")
        elif "npc" in command:
            return self.generate_content("npc")
        elif "map" in command:
            return self.generate_content("map")
        elif "quest" in command:
            return self.generate_content("quest")
        return "I didn't understand that command. Try asking for a character, NPC, map, or quest."
    
    def generate_content(self, content_type):
        generator = self.generators[content_type]
        prompt = generator.generate_prompt({})  # Can pass parameters here
        response = self.gpt_client.generate_content(prompt)
        result = generator.parse_response(response)
        
        if isinstance(result, dict):
            return self.format_response(result)
        return response
    
    def format_response(self, data):
        formatted = []
        for key, value in data.items():
            if isinstance(value, list):
                value = "\n- " + "\n- ".join(value)
            formatted.append(f"{key.title()}: {value}")
        return "\n".join(formatted)
    
    def run(self):
        print("Dungeon Master Assistant activated. Say 'hey dm' to start.")
        while True:
            text = self.voice.listen()
            if WAKE_WORD in text:
                self.voice.speak("How can I assist you, Dungeon Master?")
                command = self.voice.listen()
                print(f"Command received: {command}")
                response = self.process_command(command)
                print("Generated response:", response)
                self.voice.speak(response)

if __name__ == "__main__":
    API_KEY = "your-api-key-here"  # Replace with your OpenAI API key
    assistant = DnDAssistant(API_KEY)
    assistant.run()