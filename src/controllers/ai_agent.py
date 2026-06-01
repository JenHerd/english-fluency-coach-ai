"""
AI Integration module.
Manages transcription of audio files and communicates with the LLM API 
to retrieve grammar/vocabulary feedback.
"""

from faster_whisper import WhisperModel
from PyQt6.QtCore import QThread, pyqtSignal

import re

class TranscriptionThread(QThread):
    finished_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)

    def __init__(self, audio_filepath, duration_seconds=0.0):
        super().__init__()
        self.audio_filepath = audio_filepath
        self.duration_seconds = duration_seconds

    def run(self):
        try:
            # Initialize WhisperModel (using 'small' model on CPU)
            # compute_type='int8' runs faster on CPU and uses less memory
            model = WhisperModel("small", device="cpu", compute_type="int8")
            
            # Transcribe the audio file directly with an initial prompt for vocabulary priming
            segments, info = model.transcribe(self.audio_filepath, beam_size=5, language='en', initial_prompt='Amirul Husni, Antigravity, Google.')
            
            # Concatenate all transcribed segments
            text = "".join([segment.text for segment in segments])
            
            if text.strip():
                clean_text = text.strip()
                words = clean_text.split()
                wpm = (len(words) / self.duration_seconds) * 60 if self.duration_seconds > 0 else 0
                
                text_lower = clean_text.lower()
                filler_count = 0
                for f in [r'\bum\b', r'\buh\b', r'\blike\b', r'\byou guys\b']:
                    filler_count += len(re.findall(f, text_lower))
                
                self.finished_signal.emit({
                    "text": clean_text,
                    "wpm": round(wpm, 1),
                    "filler_count": filler_count
                })
            else:
                self.finished_signal.emit({
                    "text": "[Error: No speech detected in audio]",
                    "wpm": 0.0,
                    "filler_count": 0
                })
                
        except Exception as e:
            self.error_signal.emit(str(e))

import os
import time
import ollama
import difflib

def generate_html_diff(original, corrected):
    orig_words = re.findall(r"[\w']+|[.,!?;]", original)
    corr_words = re.findall(r"[\w']+|[.,!?;]", corrected)
    
    diff = list(difflib.ndiff(orig_words, corr_words))
    
    html = []
    for token in diff:
        code = token[0]
        word = token[2:]
        if code == ' ':
            html.append(word)
        elif code == '-':
            html.append(f'<del style="color: red;">{word}</del>')
        elif code == '+':
            html.append(f'<span style="color: green; font-weight: bold;">{word}</span>')
            
    res = " ".join(html)
    res = re.sub(r' \s*([.,!?;])', r'\1', res)
    return res

class FeedbackThread(QThread):
    finished_signal = pyqtSignal(dict)

    def __init__(self, transcribed_text):
        super().__init__()
        self.transcribed_text = transcribed_text

    def run(self):
        if not self.transcribed_text or self.transcribed_text.startswith("[Error"):
            self.finished_signal.emit({"raw_feedback": "No valid transcription provided. Skipping feedback.", "html_diff": ""})
            return

        try:
            system_instruction = (
                "Role & Perspective: You are an interactive English Fluency Coach talking directly to Amirul Husni, a Computer Science student. Always use 'You/Your' instead of 'The speaker' or 'They'.\n"
                "Technical Context: Expect technical software engineering vocabulary. The user is discussing building applications and using a development platform called 'Antigravity' by Google. Do not flag these terms as vague or incorrect.\n"
                "Strict Formatting: You must format your response strictly using Markdown. Include exactly these three headings:\n"
                "### What you did well:\n"
                "(Use bullet points)\n"
                "### Suggestions for Improvement:\n"
                "(Use bullet points)\n"
                "### Corrected Version:\n"
                "(Provide the fully improved, natural sentence)"
            )
            prompt = f"Transcription: \"{self.transcribed_text}\""
            
            response = ollama.chat(model='llama3.2', messages=[
                {
                    'role': 'system',
                    'content': system_instruction
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ])
            
            content = response['message']['content']
            
            corrected_version = ""
            match = re.search(r'### Corrected Version:\s*(.*)', content, re.DOTALL | re.IGNORECASE)
            if match:
                corrected_version = match.group(1).strip()
            
            html_diff = ""
            if corrected_version:
                html_diff = generate_html_diff(self.transcribed_text, corrected_version)
                
            self.finished_signal.emit({
                "raw_feedback": content,
                "html_diff": html_diff
            })
        except ollama.ResponseError as e:
            self.finished_signal.emit({"raw_feedback": f"[Error: Local Ollama error (is it running?): {e}]", "html_diff": ""})
        except Exception as e:
            self.finished_signal.emit({"raw_feedback": f"[Error: Could not retrieve feedback: {e}]", "html_diff": ""})
