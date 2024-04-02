import subprocess

def convert_midi_to_pdf(midi_file_path, pdf_file_path):
    # Adjust the path to the MuseScore executable as per your MuseScore installation
    musescore_executable = "C:\\Program Files\\MuseScore 4\\bin\\MuseScore4.exe"
    
    # Ensure the executable path and arguments are correctly specified
    command = [musescore_executable, midi_file_path, '-o', pdf_file_path]
    
    try:
        subprocess.run(command, check=True)
        print(f"PDF successfully generated at: {pdf_file_path}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to convert MIDI to PDF: {e}")

# Example usage
convert_midi_to_pdf('path/to/your/midi_file.mid', 'path/to/output/pdf_file.pdf')
