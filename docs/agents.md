# Agent Instructions & Architecture (agents.md)
## Context for Google Antigravity

This document defines how the agentic system should approach building the application. 

### 1. Overall Agent Strategy
The project will be built in phases. Do not attempt to write the entire application in one single script. Use a modular architecture, breaking the code into separate files (e.g., `main.py`, `ui.py`, `media_handler.py`, `ai_agent.py`, `database.py`).

### 2. System Prompts & Roles
When assigning tasks within the Antigravity workspace, utilize the following specialized roles for the agents:

#### A. The UI Engineer Agent
* **Responsibility:** Build the frontend using CustomTkinter or PyQt6. 
* **Guidelines:** Ensure the design is clean, minimalist, and responsive. Implement multithreading (using QThread or standard threading) so the UI remains responsive while the camera is active or API requests are processing.

#### B. The Media Specialist Agent
* **Responsibility:** Handle OpenCV and PyAudio integrations.
* **Guidelines:** Ensure audio and video are perfectly synced if saved to disk. Handle Windows-specific driver access permissions securely.

#### C. The AI Integration Agent
* **Responsibility:** Manage transcription and LLM API calls.
* **Guidelines:** Construct strict system prompts for the LLM to output feedback in a predictable format (e.g., JSON) so it can be parsed and displayed neatly in the UI.

### 3. Execution Order for the Agent
1. Initialize project structure and setup `requirements.txt`.
2. Draft the basic UI window with a placeholder camera feed.
3. Implement actual webcam and microphone capture.
4. Integrate the transcription model.
5. Integrate the LLM API for grammar checking.
6. Connect the local SQLite database for history tracking.
7. Final polish and bug fixing.
