# English Fluency Coach AI

A local, privacy-first desktop application designed to help you master impromptu speaking and perfect your English fluency. By leveraging on-device machine learning models, your audio, video, and transcripts never leave your machine.

![Fluency Coach AI](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![PyQt6](https://img.shields.io/badge/PyQt6-UI-green)

---

## 🌟 Features

* **Privacy-First Processing**: All audio transcription and AI analysis runs entirely on your local machine. No cloud APIs, no data mining.
* **Dynamic Impromptu Challenge Mode**: Generate endless, highly creative speaking prompts powered by Llama 3.2. Tailor your practice with *Casual*, *Professional*, or *Technical* difficulty levels.
* **Visual Word Diffing**: Instantly compare your spoken transcription against the AI's "Corrected Version" with rich-text, word-by-word visual highlighting. Red strikethroughs for removed words and bold green for AI additions.
* **Speaking Analytics**: Automatically calculates your Words Per Minute (WPM) and detects common filler words (um, uh, like, etc.) to help you track your speaking confidence.
* **SQLite Session History**: Every practice session, transcript, and AI feedback report is saved to a local SQLite database (`history.db`) for easy review in the "Past History" tab.
* **MVC Architecture**: A cleanly structured Model-View-Controller codebase ensures UI responsiveness by offloading heavy ML inference to background `QThread` workers.

## 🛠️ Technologies Used

* **[Python](https://www.python.org/)**: Core application logic.
* **[PyQt6](https://riverbankcomputing.com/software/pyqt/)**: Responsive, threaded desktop user interface.
* **[Faster-Whisper](https://github.com/SYSTRAN/faster-whisper)**: High-performance, local speech-to-text transcription.
* **[Ollama](https://ollama.com/) (Llama 3.2)**: Local Large Language Model for advanced grammar correction and dynamic topic generation.
* **[SQLite](https://www.sqlite.org/)**: Lightweight, serverless database for persistent history.

## 🚀 Getting Started

### Prerequisites

1. **Python 3.10+**: Ensure Python is installed on your system.
2. **Ollama**: Download and install [Ollama](https://ollama.com/).
3. **Llama 3.2 Model**: Once Ollama is installed, open your terminal and pull the required model:
   ```bash
   ollama run llama3.2
   ```

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/JenHerd/english-fluency-coach-ai.git
   cd english-fluency-coach-ai
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the App

Start the Ollama server in the background (if it isn't already running), then launch the application:

```bash
python src/main.py
```

## 🏗️ Architecture

The codebase strictly follows the **Model-View-Controller (MVC)** design pattern:
- **`models/`**: Manages the SQLite database operations (`database.py`).
- **`views/`**: Contains the PyQt6 frontend (`ui.py`).
- **`controllers/`**: Houses the heavy lifting—camera threads, audio recorders, whisper transcription, and Ollama integration (`ai_agent.py`, `media_handler.py`, `topic_engine.py`).

## 📄 License

This project is open-source and available under the MIT License.
