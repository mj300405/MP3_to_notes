#transcription_worker.py
from PySide6.QtCore import QObject, Signal
import torch
import librosa
from inference import PianoTranscription
from generate_pdf import convert_midi_to_pdf
import tempfile
import subprocess
import os

# class TranscriptionWorker(QObject):
#     finished = Signal()
#     transcription_result = Signal(str, str)

#     def __init__(self, audio_path, model_type, checkpoint_path, midi_path=None, pdf_path=None, display_callback=None):
#         super().__init__()
#         self.audio_path = audio_path
#         self.model_type = model_type
#         self.checkpoint_path = checkpoint_path
#         self.midi_path = midi_path
#         self.pdf_path = pdf_path
#         self.display_callback = display_callback

#     def run(self):
#         audio, sr = librosa.load(self.audio_path, sr=None, mono=True)
#         transcriptor = PianoTranscription(model_type=self.model_type, checkpoint_path=self.checkpoint_path)
#         if self.midi_path:
#             # Transcribe and optionally save the MIDI
#             transcribed_dict = transcriptor.transcribe(audio=audio, midi_path=self.midi_path)
#         if self.pdf_path and self.midi_path:
#             convert_midi_to_pdf(self.midi_path, self.pdf_path)
#         if self.display_callback and self.pdf_path:
#             self.display_callback(self.pdf_path)
#         self.finished.emit()
class TranscriptionWorker(QObject):
    finished = Signal()
    transcription_result = Signal(str, str)

    def __init__(self, audio_path, model_type, checkpoint_path, temp_midi_path, temp_pdf_path, display_callback):
        super().__init__()
        self.audio_path = audio_path
        self.model_type = model_type
        self.checkpoint_path = checkpoint_path
        self.temp_midi_path = temp_midi_path  # Confirm this is correctly set
        self.temp_pdf_path = temp_pdf_path
        self.display_callback = display_callback
        print(f"Initialized with MIDI path: {self.temp_midi_path}")  # Debug statement

    def run(self):
        audio, sr = librosa.load(self.audio_path, sr=None, mono=True)
        transcriptor = PianoTranscription(model_type=self.model_type, checkpoint_path=self.checkpoint_path)
        
        # Generate MIDI if path provided
        if self.temp_midi_path:
            transcribed_dict = transcriptor.transcribe(audio=audio, midi_path=self.temp_midi_path)

        # Generate temporary PDF from MIDI
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            self.temp_pdf_path = tmp_pdf.name

        if self.temp_midi_path:
            convert_midi_to_pdf(open(self.temp_midi_path, 'rb').read(), self.temp_pdf_path)
            if self.display_callback:
                self.display_callback(self.temp_pdf_path)  # Display the PDF from temporary path

        self.transcription_result.emit(self.temp_midi_path, self.temp_pdf_path)
        self.finished.emit()