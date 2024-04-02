# transcription_worker.py
from PySide6.QtCore import QObject, Signal
import torch
# Ensure these imports point to the correct locations in your project
from inference import PianoTranscription
import librosa
from generate_pdf import convert_midi_to_pdf

class TranscriptionWorker(QObject):
    finished = Signal()
    transcription_result = Signal(str)

    def __init__(self, audio_path, model_type, checkpoint_path):
        super().__init__()
        self.audio_path = audio_path
        self.model_type = model_type
        self.checkpoint_path = checkpoint_path
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

    def run(self):
        # Load audio from the file path
        audio, sr = librosa.load(self.audio_path, sr=None, mono=True)
        
        # Initialize the transcription object with the correct parameters
        transcriptor = PianoTranscription(model_type=self.model_type,
                                          checkpoint_path=self.checkpoint_path,
                                          device=self.device)
        
        # Generate a MIDI path based on the audio path or as per your logic
        midi_path = self.audio_path.replace('.wav', '.mid').replace('.mp3', '.mid')

        # Call the transcribe method with the loaded audio and MIDI path
        transcribed_dict = transcriptor.transcribe(audio=audio, midi_path=midi_path)

        # generate PDF directly from transcribed data
        pdf_path = self.audio_path.replace('.wav', '.pdf').replace('.mp3', '.pdf')
        convert_midi_to_pdf(midi_path, pdf_path)

        # Emit the transcription result with the path to the generated MIDI file
        self.transcription_result.emit(pdf_path)
        self.finished.emit()
