"""
UI Engineer module.
Builds the frontend using PyQt6. Handles the main window, 
camera feed display, recording controls, and feedback views.
Multithreading via QThread should be used here to maintain responsiveness.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
    QLabel, QPushButton, QTabWidget, QTextEdit, QListWidget, QListWidgetItem,
    QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QImage
from controllers.media_handler import CameraThread, AudioRecorder
from controllers.ai_agent import TranscriptionThread, FeedbackThread, generate_html_diff
from controllers import topic_engine
from models import database
import re

class FluencyCoachMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("English Fluency Coach")
        self.resize(1000, 600)
        
        # Apply minimalist, clean stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f7;
            }
            QLabel {
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #333333;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: white;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #e1e1e1;
                padding: 8px 15px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QTabBar::tab:selected {
                background-color: white;
                border: 1px solid #cccccc;
                border-bottom-color: white;
            }
            QTextEdit, QListWidget {
                border: none;
                background-color: white;
                color: #333333;
                font-size: 14px;
                padding: 10px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)

        self._setup_ui()
        
        # Initialize Database
        database.init_db()
        self._load_history()

        # Initialize Media Handlers
        self.camera_thread = CameraThread()
        self.camera_thread.change_pixmap_signal.connect(self.update_image)
        self.camera_thread.error_signal.connect(lambda msg: self.show_error_message("Camera Error", msg))
        self.camera_thread.start()
        
        self.audio_recorder = AudioRecorder(error_callback=lambda msg: self.show_error_message("Microphone Error", msg))
        self.is_recording = False

    def _setup_ui(self):
        """Initializes the central widget and main layout structure."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)

        left_panel = self._build_left_panel()
        right_panel = self._build_right_panel()

        # Add panels to main layout
        main_layout.addLayout(left_panel, stretch=1)
        main_layout.addLayout(right_panel, stretch=1)

    def _build_left_panel(self):
        """Constructs the left panel containing the camera feed and challenge mode controls."""
        left_panel = QVBoxLayout()
        left_panel.setSpacing(20)

        # Status Label
        self.status_label = QLabel("⚫ Standby")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #888888;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFixedHeight(20)
        left_panel.addWidget(self.status_label)

        # Blink timer for recording
        self.blink_timer = QTimer(self)
        self.blink_timer.timeout.connect(self._toggle_blink)
        self.is_blink_visible = True

        # Camera Placeholder
        self.camera_label = QLabel("Camera Feed Placeholder")
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_label.setStyleSheet("""
            QLabel {
                background-color: #e0e0e0;
                border: 2px dashed #aaaaaa;
                border-radius: 8px;
                font-size: 16px;
                color: #666666;
            }
        """)
        self.camera_label.setMinimumSize(480, 360)  # Standard 4:3 placeholder
        left_panel.addWidget(self.camera_label)

        # --- NEW CHALLENGE MODE SECTION ---
        self.current_topic = None
        
        challenge_layout = QVBoxLayout()
        challenge_layout.setSpacing(5)
        
        challenge_header = QLabel("Challenge Mode")
        challenge_header.setStyleSheet("font-weight: bold; font-size: 16px; color: #333333;")
        challenge_layout.addWidget(challenge_header, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.level_combo = QComboBox()
        self.level_combo.addItems(["Casual", "Professional", "Technical"])
        self.level_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 5px;
                font-size: 13px;
                color: #333333;
            }
        """)
        challenge_layout.addWidget(self.level_combo)
        
        self.topic_label = QLabel("Active Topic: [Click Generate to Start]")
        self.topic_label.setWordWrap(True)
        self.topic_label.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 15px;
                font-size: 14px;
                color: #555555;
            }
        """)
        self.topic_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        challenge_layout.addWidget(self.topic_label)
        
        self.generate_topic_btn = QPushButton("Generate Random Topic")
        self.generate_topic_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.generate_topic_btn.setToolTip("Generate a new random presentation topic to practice impromptu speaking.")
        self.generate_topic_btn.clicked.connect(self.generate_topic)
        challenge_layout.addWidget(self.generate_topic_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        left_panel.addLayout(challenge_layout)
        # ----------------------------------

        # Record Button
        self.record_btn = QPushButton("Start Recording")
        self.record_btn.setToolTip("Click to start or stop your audio and video recording.")
        self.record_btn.clicked.connect(self.toggle_recording)
        left_panel.addWidget(self.record_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        left_panel.addStretch()
        return left_panel

    def _build_right_panel(self):
        """Constructs the right panel containing tabs for current feedback and history."""
        right_panel = QVBoxLayout()
        
        self.tabs = QTabWidget()
        
        # Tab 1: Current Feedback
        self.feedback_tab = QWidget()
        feedback_layout = QVBoxLayout(self.feedback_tab)
        feedback_layout.setContentsMargins(0, 0, 0, 0)
        
        self.analytics_label = QLabel("Pace: -- WPM | Filler Words Detected: --")
        self.analytics_label.setStyleSheet("font-weight: bold; color: #0078d4; padding: 10px;")
        feedback_layout.addWidget(self.analytics_label)
        
        self.feedback_text = QTextEdit()
        self.feedback_text.setReadOnly(True)
        self.feedback_text.setPlaceholderText("Your AI feedback will appear here after recording...")
        feedback_layout.addWidget(self.feedback_text)
        
        # Tab 2: Past History
        self.history_tab = QWidget()
        history_layout = QHBoxLayout(self.history_tab)
        history_layout.setContentsMargins(0, 0, 0, 0)
        
        self.history_list = QListWidget()
        self.history_list.setMinimumWidth(150)
        self.history_list.setMaximumWidth(200)
        self.history_list.itemSelectionChanged.connect(self.on_history_item_selected)
        history_layout.addWidget(self.history_list)
        
        self.history_detail_text = QTextEdit()
        self.history_detail_text.setReadOnly(True)
        self.history_detail_text.setPlaceholderText("Select a history item to view details...")
        history_layout.addWidget(self.history_detail_text)
        
        self.tabs.addTab(self.feedback_tab, "Current Feedback")
        self.tabs.addTab(self.history_tab, "Past History")

        right_panel.addWidget(self.tabs)
        return right_panel

    def update_image(self, qt_img):
        """Updates the camera_label with a new QImage"""
        self.camera_label.setPixmap(QPixmap.fromImage(qt_img).scaled(
            self.camera_label.width(), self.camera_label.height(),
            Qt.AspectRatioMode.KeepAspectRatio
        ))

    def show_error_message(self, title, message):
        """Displays a critical error message box safely from any thread."""
        QTimer.singleShot(0, lambda: QMessageBox.critical(self, title, message))

    def generate_topic(self):
        level = self.level_combo.currentText().lower()
        self.topic_label.setText("Active Topic: Generating topic...")
        self.generate_topic_btn.setEnabled(False)
        
        # Instantiate as an instance variable and parent it to self to prevent garbage collection
        self.topic_thread = topic_engine.TopicGeneratorThread(level)
        self.topic_thread.setParent(self)
        self.topic_thread.finished_signal.connect(self.update_topic_label)
        self.topic_thread.start()

    def update_topic_label(self, topic):
        self.current_topic = topic
        self.topic_label.setText(f"Active Topic: {topic}")
        self.generate_topic_btn.setEnabled(True)

    def _toggle_blink(self):
        self.is_blink_visible = not self.is_blink_visible
        if self.is_blink_visible:
            self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #d83b01;")
        else:
            self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: transparent;")

    def toggle_recording(self):
        if not self.is_recording:
            # Start recording
            self.is_recording = True
            self.status_label.setText("🔴 Recording...")
            self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #d83b01;")
            self.blink_timer.start(800)
            
            self.record_btn.setText("Stop Recording")
            self.record_btn.setStyleSheet("""
                QPushButton {
                    background-color: #d83b01;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 10px 20px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #a82e00;
                }
            """)
            self.camera_thread.start_recording()
            self.audio_recorder.start_recording()
        else:
            try:
                # Stop recording
                self.is_recording = False
                self.blink_timer.stop()
                self.status_label.setText("⚫ Standby")
                self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #888888;")
                
                self.record_btn.setText("Start Recording")
                self.record_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #0078d4;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 10px 20px;
                        font-size: 14px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #005a9e;
                    }
                """)
                self.camera_thread.stop_recording()
                duration = self.audio_recorder.stop_recording()
                self.feedback_text.setPlainText("Processing transcription...")

                # Start transcription
                self.transcription_thread = TranscriptionThread(self.audio_recorder.audio_filename, duration_seconds=duration)
                self.transcription_thread.finished_signal.connect(self.on_transcription_finished)
                self.transcription_thread.error_signal.connect(lambda msg: self.show_error_message("Runtime Error", msg))
                self.transcription_thread.start()
            except Exception as e:
                QMessageBox.critical(self, "Stop Recording Crash", str(e))

    def on_transcription_finished(self, result_dict):
        """Displays the transcribed text and starts the LLM feedback process."""
        text = result_dict["text"]
        
        if text.startswith("[Error"):
            self.show_error_message("Transcription Error", text)
            self.feedback_text.setPlainText("Transcription failed. Please check your microphone or audio files.")
            return
            
        self.current_wpm = result_dict.get("wpm", 0.0)
        self.current_filler_count = result_dict.get("filler_count", 0)
        
        self.analytics_label.setText(f"Pace: {self.current_wpm} WPM | Filler Words Detected: {self.current_filler_count}")
        
        self.current_transcription = text
        self.feedback_text.setPlainText(f"Transcription:\n{text}\n\nAnalyzing grammar...")
        
        self.feedback_thread = FeedbackThread(text)
        self.feedback_thread.finished_signal.connect(self.on_feedback_finished)
        self.feedback_thread.start()

    def on_feedback_finished(self, result_dict):
        """Displays the LLM feedback."""
        feedback_text = result_dict.get("raw_feedback", "")
        html_diff = result_dict.get("html_diff", "")
        
        if feedback_text.startswith("[Error"):
            self.show_error_message("AI Feedback Error", feedback_text)
            self.feedback_text.setHtml("<b>Feedback failed. Please ensure your local LLM (Ollama) is running.</b>")
            return
            
        text = getattr(self, 'current_transcription', '')
        
        html_content = f"<b>Transcription:</b><br>{text}<br><br>"
        html_content += f"<b>--- AI Feedback ---</b><br>"
        
        formatted_feedback = feedback_text.replace('\n', '<br>')
        html_content += formatted_feedback
        
        if html_diff:
            html_content += f"<br><br><b>#### Visual Comparison:</b><br>{html_diff}"
            
        self.feedback_text.setHtml(html_content)
        
        # Save to database
        if hasattr(self, 'current_transcription'):
            new_id, timestamp = database.insert_history(
                self.current_transcription, 
                feedback_text,
                wpm=getattr(self, 'current_wpm', 0.0),
                filler_count=getattr(self, 'current_filler_count', 0),
                topic=getattr(self, 'current_topic', None)
            )
            self._add_history_item(new_id, timestamp)
            
            self.current_topic = None
            self.topic_label.setText("Active Topic: [Click Generate to Start]")

    def _load_history(self):
        records = database.get_all_history()
        # Reverse to add the oldest first if we are inserting at bottom, 
        # but since we want newest at top, let's just insert them in order.
        # Actually get_all_history returns newest first, so we use addItem which puts newest at top... 
        # Wait, addItem puts at bottom. 
        for record in records:
            self._add_history_item(record["id"], record["timestamp"], at_top=False)
            
    def _add_history_item(self, record_id, timestamp, at_top=True):
        item = QListWidgetItem(timestamp)
        item.setData(Qt.ItemDataRole.UserRole, record_id)
        if at_top:
            self.history_list.insertItem(0, item)
        else:
            self.history_list.addItem(item)
            
    def on_history_item_selected(self):
        selected_items = self.history_list.selectedItems()
        if not selected_items:
            self.history_detail_text.clear()
            return
        
        item = selected_items[0]
        record_id = item.data(Qt.ItemDataRole.UserRole)
        record = database.get_history_by_id(record_id)
        
        if record:
            transcription = record['transcription']
            feedback = record['feedback']
            
            html_diff = ""
            match = re.search(r'### Corrected Version:\s*(.*)', feedback, re.DOTALL | re.IGNORECASE)
            if match:
                corrected = match.group(1).strip()
                html_diff = generate_html_diff(transcription, corrected)
            
            html_content = ""
            if record.get('topic'):
                html_content += f"<b>--- Challenge Topic ---</b><br>{record['topic']}<br><br>"
            
            html_content += f"<b>--- Analytics ---</b><br>"
            html_content += f"Pace: {record.get('wpm', 0)} WPM | Filler Words: {record.get('filler_count', 0)}<br><br>"
            html_content += f"<b>--- Transcription ---</b><br>{transcription}<br><br>"
            html_content += f"<b>--- AI Feedback ---</b><br>{feedback.replace('\n', '<br>')}"
            
            if html_diff:
                html_content += f"<br><br><b>#### Visual Comparison:</b><br>{html_diff}"
                
            self.history_detail_text.setHtml(html_content)

    def closeEvent(self, event):
        """Stop the camera thread when closing the application."""
        if hasattr(self, 'camera_thread'):
            self.camera_thread.stop()
        if hasattr(self, 'audio_recorder') and self.is_recording:
            self.audio_recorder.stop_recording()
        event.accept()
