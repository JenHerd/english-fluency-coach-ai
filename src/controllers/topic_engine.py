"""
Topic Engine Module
Provides a list of random presentation topics to challenge the user's
impromptu speaking skills, focusing on multi-level categories.
"""

import random
import ollama
from PyQt6.QtCore import QThread, pyqtSignal

# Reorganized into mapped levels for accurate fallback support
CHALLENGE_TOPICS = {
    "casual": [
        "Talk about your favorite comfort food and explain step-by-step how to prepare it.",
        "Describe a travel destination you want to visit and what draws you to it.",
        "How do you maintain focus and manage your time during an intense week?",
        "Describe your ideal morning routine and how it sets up your day for success.",
        "If you could master any musical instrument or creative hobby instantly, what would it be?"
    ],
    "professional": [
        "How do you approach resolving a technical disagreement inside a project team?",
        "Describe a major setback or mistake you made in a past project and what it taught you.",
        "How do you explain an unexpected system delay to an anxious supervisor or user?",
        "What are the most important communication qualities that separate a great leader from a boss?",
        "How do you structure your personal routine to learn new software tools outside of your core workload?"
    ],
    "technical": [
        "Explain how a Naive Bayes algorithm classifies data to a non-technical person.",
        "What is the difference between an autonomous AI Agent and a traditional sequential workflow?",
        "Explain the core concept of Market Basket Analysis and why e-commerce systems use it.",
        "Why is the Separation of Concerns important when structuring a software repository?",
        "Describe your favorite personal coding project and the biggest technical challenge you overcame while building it.",
        "How would you pitch a new software product idea to a group of investors in under two minutes?",
        "Explain the concept of containerization (like Docker) and why it's useful in modern deployment.",
        "What are the trade-offs between using a SQL versus a NoSQL database?",
        "Describe a time you had a technical disagreement with a team member and how you resolved it.",
        "How would you explain the concept of an API (Application Programming Interface) to a child?"
    ]
}

def get_random_topic(level='technical'):
    """Fallback function: Returns a randomly selected challenge topic matching the requested level."""
    cleaned_level = level.lower().strip()
    if cleaned_level in CHALLENGE_TOPICS:
        return random.choice(CHALLENGE_TOPICS[cleaned_level])
    return random.choice(CHALLENGE_TOPICS['technical'])

def is_ollama_online():
    """Health check to explicitly test if the local server is running."""
    try:
        ollama.list() # A lightning-fast ping to the server
        return True
    except Exception:
        return False

class TopicGeneratorThread(QThread):
    finished_signal = pyqtSignal(str)
    
    def __init__(self, level='technical'):
        super().__init__()
        self.level = level.lower().strip()
        
    def run(self):
        # YOUR EXPLICIT IF/ELSE RULE
        if is_ollama_online():
            print(f"\n[Topic Engine] Ollama is ONLINE. Generating fully random {self.level} topic...")
            try:
                prompt_instruction = (
                    f"You are a highly creative English training app. Generate ONE single, highly unique, "
                    f"and unexpected impromptu speaking prompt. The difficulty level is: {self.level}. "
                    f"Avoid repetitive starters like 'Describe' or 'Explain'. Give me a bizarre, creative, or challenging scenario. "
                    f"Output ONLY the prompt sentence."
                )
                
                response = ollama.chat(
                    model='llama3.2', 
                    messages=[{'role': 'user', 'content': prompt_instruction}],
                    options={'temperature': 1.0, 'top_p': 0.95}
                )
                
                # Safe extraction for both dictionary and object formats
                if hasattr(response, 'message'):
                    topic = response.message.content.strip()
                else:
                    topic = response['message']['content'].strip()
                
                if topic:
                    self.finished_signal.emit(topic)
                else:
                    print("[Topic Engine] WARNING: AI returned a blank string. Using fallback.")
                    self.finished_signal.emit(get_random_topic(self.level))
                
            except Exception as e:
                print(f"[Topic Engine] WARNING: Ollama failed during generation. Error: {e}")
                self.finished_signal.emit(get_random_topic(self.level))
        
        else:
            print(f"\n[Topic Engine] Ollama is OFFLINE. Pulling from Challenge Topics box...")
            self.finished_signal.emit(get_random_topic(self.level))