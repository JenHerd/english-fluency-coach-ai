"""
Media Specialist module.
Handles OpenCV for webcam capture and SoundDevice/PyAudio for microphone capture.
Manages temporary saving of audio/video files locally.
"""

import cv2
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write as wav_write
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage
import threading
import os

TEMP_DIR = os.path.abspath(os.path.join(os.getcwd(), 'temp'))
os.makedirs(TEMP_DIR, exist_ok=True)

class CameraThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)
    error_signal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self._run_flag = True
        self.recording = False
        self.out = None
        self.video_filename = os.path.join(TEMP_DIR, "temp_video.avi")

    def run(self):
        # Open the default camera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.error_signal.emit("Could not open webcam.")
            return
        
        while self._run_flag:
            ret, cv_img = cap.read()
            if ret:
                # If we are recording, write the frame to the video file
                if self.recording:
                    if self.out is None:
                        # Initialize VideoWriter
                        fourcc = cv2.VideoWriter_fourcc(*'XVID')
                        # Use the same frame size as the capture
                        frame_size = (int(cap.get(3)), int(cap.get(4)))
                        self.out = cv2.VideoWriter(self.video_filename, fourcc, 20.0, frame_size)
                    self.out.write(cv_img)
                
                # Convert the image to QImage for the UI
                rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                self.change_pixmap_signal.emit(convert_to_Qt_format)
            else:
                self.error_signal.emit("Webcam disconnected or failed to read frame.")
                break
                
        # Release the camera and writer when the thread stops
        cap.release()
        if self.out is not None:
            self.out.release()
            self.out = None

    def start_recording(self):
        self.recording = True

    def stop_recording(self):
        try:
            self.recording = False
            if self.out is not None:
                self.out.release()
                self.out = None
        except Exception as e:
            raise RuntimeError(f"Video saving failed: {e}")

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()


class AudioRecorder:
    def __init__(self, fs=44100, error_callback=None):
        self.fs = fs
        self.error_callback = error_callback
        self.recording = False
        self.audio_data = []
        self.audio_filename = os.path.join(TEMP_DIR, "temp_audio.wav")
        self._stream = None
        self._thread = None

    def _callback(self, indata, frames, time, status):
        if status:
            print(status)
        if self.recording:
            self.audio_data.append(indata.copy())

    def _record(self):
        try:
            with sd.InputStream(samplerate=self.fs, channels=1, dtype='int16', callback=self._callback):
                while self.recording:
                    sd.sleep(100)
        except Exception as e:
            if self.error_callback:
                self.error_callback(f"Microphone access error: {e}")
            self.recording = False

    def start_recording(self):
        self.audio_data = []
        self.recording = True
        self._thread = threading.Thread(target=self._record)
        self._thread.start()

    def stop_recording(self):
        try:
            self.recording = False
            if self._thread is not None:
                self._thread.join()
            
            duration = 0.0
            if self.audio_data:
                # Concatenate chunks and save to file
                audio_np = np.concatenate(self.audio_data, axis=0)
                wav_write(self.audio_filename, self.fs, audio_np)
                duration = len(audio_np) / self.fs
                
            return duration
        except Exception as e:
            raise RuntimeError(f"Audio saving failed: {e}")
