from piano_transcription_inference import PianoTranscription, sample_rate, load_audio # type: ignore

# Load audio
(audio, _) = load_audio('adds/Schubert/original/movement1.mp3', sr=sample_rate, mono=True)

# Transcriptor
transcriptor = PianoTranscription(device='cpu')    # 'cuda' | 'cpu'

# Transcribe and write out to MIDI file
transcribed_dict = transcriptor.transcribe(audio, 'cut_liszt.mid')