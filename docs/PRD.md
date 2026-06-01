# Product Requirements Document (PRD)
## Project Name: English Fluency Coach (Desktop App)

### 1. Product Vision
To create a lightweight, responsive Windows application that acts as a personal English tutor using local hardware and AI APIs.

### 2. Core Features
* **Media Capture:** A UI interface featuring a live webcam feed and a prominent "Record/Stop" button.
* **Transcription Engine:** Processes the recorded audio into text immediately after stopping the recording.
* **AI Analysis:** Sends the transcript to an LLM to identify errors (grammar, syntax, vocabulary) and returns a side-by-side comparison (Original vs. Improved).
* **[Added Feature] Pronunciation/Pacing Metrics:** Measures Words Per Minute (WPM) and pauses to give feedback on speaking confidence and flow.
* **[Added Feature] History Dashboard:** A simple local database (SQLite or JSON) that saves past transcripts and AI feedback so the user can review past mistakes.

### 3. User Interface (UI) Requirements
* **Style:** Minimalist and clean (avoid bright, distracting colors). Use soft, neutral tones.
* **Layout:**
  * Left Panel: Live camera feed and recording controls.
  * Right Panel: Tabbed view for "Current Feedback" and "Past History".

### 4. User Flow
1. User opens the application.
2. User clicks "Start Recording" and speaks into the camera.
3. User clicks "Stop Recording".
4. A loading indicator appears while the app processes audio and fetches AI feedback.
5. The feedback is displayed on the screen.
