import subprocess
import tempfile
import shutil
import os
import time


def convert_midi_to_pdf(midi_data, pdf_file_path):
    #musescore_executable = "C:\\Program Files\\MuseScore 4\\bin\\MuseScore4.exe"
    musescore_executable = "/usr/bin/musescore"

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mid") as tmp_midi:
        midi_file_path = tmp_midi.name
        tmp_midi.write(midi_data)
        tmp_midi.flush()

    command = [musescore_executable, midi_file_path, '-o', pdf_file_path]
    try:
        process = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("MuseScore output:", process.stdout.decode())
        print("MuseScore errors:", process.stderr.decode())
        print(f"PDF successfully generated at: {pdf_file_path}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to convert MIDI to PDF: {e.stdout.decode()} {e.stderr.decode()}")
    finally:
        os.unlink(midi_file_path)




def convert_midi_to_pdf_preview(musescore_executable, midi_data, pdf_file_path):
    # Create a temporary MIDI file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mid") as tmp_midi:
        midi_file_path = tmp_midi.name
        tmp_midi.write(midi_data)
        tmp_midi.close()

        # Ensure the executable path and arguments are correctly specified
        command = [musescore_executable, midi_file_path, '-o', pdf_file_path]

        try:
            subprocess.run(command, check=True)
            print(f"PDF successfully generated at: {pdf_file_path}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to convert MIDI to PDF: {e}")
        finally:
            # Remove the temporary MIDI file
            if os.path.exists(midi_file_path):
                os.remove(midi_file_path)


def safe_file_delete(file_path, max_attempts=5, delay=1):
    """ Attempt to delete a file with retries and delays. """
    for attempt in range(max_attempts):
        try:
            os.remove(file_path)
            print("File deleted successfully.")
            break
        except PermissionError as e:
            if attempt < max_attempts - 1:
                print(f"Retrying to delete file. Attempt {attempt + 1}")
                time.sleep(delay)
            else:
                print(f"Failed to delete the file after {max_attempts} attempts.")
                raise e
