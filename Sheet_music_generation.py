from music21 import stream, note, tempo, meter

def create_sheet_music(note_events, output_path='transcription.pdf'):
    # Create a Music21 stream to hold the music data
    s = stream.Stream()
    
    # Optional: Add tempo and time signature to the stream
    s.append(tempo.MetronomeMark(number=120))  # Example tempo
    s.append(meter.TimeSignature('4/4'))  # Example time signature
    
    for event in note_events:
        start_time, end_time, pitch = event
        duration = end_time - start_time  # Calculate duration based on your model's time step resolution
        new_note = note.Note()
        new_note.pitch.midi = pitch
        new_note.duration.quarterLength = duration  # Set duration in terms of quarter notes
        s.append(new_note)
    
    # Export the stream to a MIDI file first
    midi_path = output_path.replace('.pdf', '.mid')
    s.write('midi', fp=midi_path)