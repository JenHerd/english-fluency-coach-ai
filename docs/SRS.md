# Software Requirements Specification (SRS)
## Project Name: English Fluency Coach (Desktop App)

### 1. Technology Stack
* **Language:** Python 3.10+
* **GUI Framework:** PyQt6 or CustomTkinter (for a modern, clean look).
* **Media Handling:** OpenCV (for video capture) and PyAudio/SoundDevice (for microphone capture).
* **Transcription:** `SpeechRecognition` library or local `Whisper` model (if hardware permits).
* **AI Integration:** Integration with an LLM API (e.g., Google Gemini API, OpenAI, or a local model via Ollama).
* **Storage:** SQLite3 for storing historical feedback and transcripts.

### 2. Functional Requirements
* **FR1:** The system shall access the default Windows camera and microphone.
* **FR2:** The system shall save the temporary audio/video files locally in a designated `temp` folder.
* **FR3:** The system shall handle API timeouts gracefully, alerting the user without crashing.
* **FR4:** The system shall allow users to delete their past history from the local database.

### 3. Non-Functional Requirements
* **Performance:** The UI thread must not freeze during media processing or API calls (requires multithreading/async operations).
* **Privacy:** All video and audio files must remain locally on the user's Windows machine. Only the text transcript is sent to the LLM API.
* **Compatibility:** Must run natively on Windows 10/11.

### 4. Data Models (Database Schema)
* **Table: `sessions`**
  * `id` (Primary Key, Integer)
  * `timestamp` (DateTime)
  * `original_transcript` (Text)
  * `ai_feedback` (Text)
  * `duration_seconds` (Integer)
