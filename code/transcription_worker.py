from PySide6.QtCore import QObject, Signal
import librosa
from piano_transcription_inference import PianoTranscription, sample_rate, load_audio
from generate_pdf import convert_midi_to_pdf
import tempfile
import os

class TranscriptionWorker(QObject):
    finished = Signal()
    transcription_result = Signal(str, str)

    def __init__(self, audio_path, device='cpu', display_callback=None):
        super().__init__()
        self.audio_path = audio_path
        self.device = device
        self.display_callback = display_callback
        self.temp_midi_path = None
        self.temp_pdf_path = None
        print("TranscriptionWorker initialized")

    def run(self):
        try:
            # Load audio
            (audio, _) = load_audio(self.audio_path, sr=sample_rate, mono=True)
            print(f"Audio loaded from {self.audio_path}")

            # Initialize the transcriptor
            transcriptor = PianoTranscription(device=self.device)
            print("Transcriptor initialized")

            # Use a temporary file to save the MIDI
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mid") as tmp_midi:
                self.temp_midi_path = tmp_midi.name
                transcriptor.transcribe(audio=audio, midi_path=self.temp_midi_path)
                print(f"MIDI file generated at {self.temp_midi_path}")
            
            # Use another temporary file for the PDF output
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                self.temp_pdf_path = tmp_pdf.name

            # Convert MIDI to PDF
            convert_midi_to_pdf(open(self.temp_midi_path, 'rb').read(), self.temp_pdf_path)
            print(f"PDF generated at {self.temp_pdf_path}")
            
            # Callback to display the PDF
            if self.display_callback:
                self.display_callback(self.temp_pdf_path)

            # Emit the result paths
            self.transcription_result.emit(self.temp_midi_path, self.temp_pdf_path)

        except Exception as e:
            print(f"An error occurred: {str(e)}")

        finally:
            self.finished.emit()