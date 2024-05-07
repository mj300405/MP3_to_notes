import sys
import fitz  # PyMuPDF
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget, QFileDialog, QProgressBar, QHBoxLayout, QGroupBox, QLabel, QScrollArea, QSizePolicy
from PySide6.QtCore import QThread, Qt, QEvent, QTimer
from PySide6.QtGui import QIcon, QPixmap, QImage
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtPdf import QPdfDocument
from transcription_worker import TranscriptionWorker
import os
import shutil
import tempfile
import threading
import vlc

class SoundToNotesApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Sound to Notes Transcription')
        self.setGeometry(100, 100, 1300, 800)
        self.setWindowIcon(QIcon('adds/favicon.ico'))  # Ensure this path is correct
        self.temp_files = []  # List to manage temporary files
        self.current_pdf_path = None  # Store the current PDF path
        self.mp3_player = None
        self.midi_player = None
        self.pdf_pixmaps = []
        self.initUI()


    def initUI(self):
        # Set up the central widget and main layout
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        mainLayout = QHBoxLayout(centralWidget)  # Main layout now horizontal

        # Container for controls and uploading
        controlsContainer = QVBoxLayout()

        # Set up the progress bar
        self.progressBar = QProgressBar()
        controlsContainer.addWidget(self.progressBar)

        # Set up the upload group box
        uploadGroupBox = QGroupBox("Upload Audio")
        uploadLayout = QVBoxLayout()
        self.uploadButton = QPushButton('Upload')
        self.uploadButton.clicked.connect(self.uploadFile)
        uploadLayout.addWidget(self.uploadButton)
        self.uploadedFileLabel = QLabel("No file uploaded")
        uploadLayout.addWidget(self.uploadedFileLabel)
        uploadGroupBox.setLayout(uploadLayout)
        controlsContainer.addWidget(uploadGroupBox)

        # Transcription group box
        transcriptionGroupBox = QGroupBox("Transcription Controls")
        transcriptionLayout = QVBoxLayout()
        transcriptionLayout.setContentsMargins(10, 10, 10, 10)  # Adjust margins
        transcriptionLayout.setSpacing(10)  # Adjust spacing
        self.transcriptionDisplay = QTextEdit()
        self.transcriptionDisplay.setMaximumHeight(50)
        controlsContainer.addWidget(self.transcriptionDisplay)
        self.transcribeButton = QPushButton('Transcribe')
        self.transcribeButton.clicked.connect(self.startTranscription)
        self.transcribeButton.setEnabled(False)
        transcriptionLayout.addWidget(self.transcribeButton)
        self.saveMidiButton = QPushButton('Save MIDI')
        self.saveMidiButton.clicked.connect(self.saveMidi)
        self.saveMidiButton.setEnabled(False)
        transcriptionLayout.addWidget(self.saveMidiButton)
        self.savePdfButton = QPushButton('Save PDF')
        self.savePdfButton.clicked.connect(self.savePdf)
        self.savePdfButton.setEnabled(False)
        transcriptionLayout.addWidget(self.savePdfButton)
        transcriptionGroupBox.setLayout(transcriptionLayout)
        controlsContainer.addWidget(transcriptionGroupBox)

        # MP3 player controls group
        MP3GroupBox = QGroupBox("MP3 Player Controls")
        MP3Layout = QVBoxLayout()
        MP3Layout.setContentsMargins(10, 10, 10, 10)  # Adjust margins
        MP3Layout.setSpacing(10)  # Adjust spacing
        self.playMP3Button = QPushButton('Play MP3')
        self.playMP3Button.clicked.connect(self.playMedia)
        self.playMP3Button.setEnabled(False)
        MP3Layout.addWidget(self.playMP3Button)
        self.pauseButton = QPushButton('Pause/Resume MP3')
        self.pauseButton.clicked.connect(self.togglePause)
        self.pauseButton.setEnabled(False)
        MP3Layout.addWidget(self.pauseButton)
        self.stopButton = QPushButton('Stop MP3')
        self.stopButton.clicked.connect(self.stopMedia)
        self.stopButton.setEnabled(False)
        MP3Layout.addWidget(self.stopButton)
        MP3GroupBox.setLayout(MP3Layout)
        controlsContainer.addWidget(MP3GroupBox)

        # MIDI player controls group
        MidiGroupBox = QGroupBox("MIDI Player Controls")
        MidiLayout = QVBoxLayout()
        MidiLayout.setContentsMargins(10, 10, 10, 10)  # Adjust margins
        MidiLayout.setSpacing(10)  # Adjust spacing
        self.playMidiButton = QPushButton('Play MIDI')
        self.playMidiButton.clicked.connect(self.playMediaMidi)
        self.playMidiButton.setEnabled(False)
        MidiLayout.addWidget(self.playMidiButton)
        self.pauseMidiButton = QPushButton('Pause/Resume MIDI')
        self.pauseMidiButton.clicked.connect(self.togglePauseMidi)
        self.pauseMidiButton.setEnabled(False)
        MidiLayout.addWidget(self.pauseMidiButton)
        self.stopMidiButton = QPushButton('Stop MIDI')
        self.stopMidiButton.clicked.connect(self.stopMediaMidi)
        self.stopMidiButton.setEnabled(False)
        MidiLayout.addWidget(self.stopMidiButton)
        MidiGroupBox.setLayout(MidiLayout)
        controlsContainer.addWidget(MidiGroupBox)

        # Add the left column layout to the main layout
        mainLayout.addLayout(controlsContainer, 1)

        # # PDF Display area
        # pdfGroupBox = QGroupBox("PDF Preview")
        # pdfLayout = QVBoxLayout()
        # self.scrollArea = QScrollArea()
        # self.scrollArea.setWidgetResizable(True)
        # self.scrollWidget = QWidget()
        # self.scrollLayout = QVBoxLayout(self.scrollWidget)
        # self.scrollArea.setWidget(self.scrollWidget)
        # pdfLayout.addWidget(self.scrollArea)
        # pdfGroupBox.setLayout(pdfLayout)
        # mainLayout.addWidget(pdfGroupBox, 2)  # Set stretch factor to 2 for a 1:2 ratio

        # PDF Display area using QPdfView
        pdfGroupBox = QGroupBox("PDF Preview")
        pdfLayout = QVBoxLayout()
        self.pdfView = QPdfView()
        self.pdfView.setZoomMode(QPdfView.FitToWidth)  # Automatically adjusts the PDF to fit the width of the view
        pdfLayout.addWidget(self.pdfView)
        pdfGroupBox.setLayout(pdfLayout)
        mainLayout.addWidget(pdfGroupBox, 2)  # Set stretch factor to 2 for a 1:2 ratio

        # Apply custom stylesheets
        self.applyStylesheet()


    def applyStylesheet(self):
        self.setStyleSheet("""
            QGroupBox {
                font: bold;
                border: 1px solid silver;
                border-radius: 6px;
                margin-top: 20px;
            }
            QGroupBox:title {
                subcontrol-origin: margin;
                left: 7px;
                padding: 5px 10px 5px 10px;
            }
            QPushButton {
                background-color: #A3C1DA;
                border-style: outset;
                border-width: 2px;
                border-radius: 10px;
                border-color: beige;
                font: bold 12px;
                min-width: 10em;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #6698FF;
                border-style: inset;
            }
            QTextEdit {
                font: 12px;
                border: 1px solid #A3C1DA;
            }
        """)


    def uploadFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Audio File", "", "Audio Files (*.mp3 *.wav)")
        if fileName:
            self.uploadedFileName = fileName
            self.uploadedFileLabel.setText(f"Uploaded file: {fileName.split('/')[-1]}")
            self.transcribeButton.setEnabled(True)
            self.saveMidiButton.setEnabled(False)
            self.savePdfButton.setEnabled(False)
            self.playMP3Button.setEnabled(True)
            self.pauseButton.setEnabled(False)
            self.stopButton.setEnabled(False)
        if self.mp3_player:
            self.mp3_player.stop()
            self.mp3_player.release()
        self.mp3_player = vlc.MediaPlayer(fileName)


    def startTranscription(self):
        # Modify this method to manage temporary files...
        if hasattr(self, 'uploadedFileName'):
            self.processFileInThread(self.uploadedFileName)

    def saveMidi(self):
        print("Attempting to save MIDI with path:", getattr(self.worker, 'temp_midi_path', 'No path attribute found'))  # Debug
        if hasattr(self.worker, 'temp_midi_path') and os.path.isfile(self.worker.temp_midi_path):
            midi_path, _ = QFileDialog.getSaveFileName(self, "Save MIDI File", "", "MIDI files (*.mid)")
            if midi_path:
                shutil.copy(self.worker.temp_midi_path, midi_path)
                self.transcriptionDisplay.setPlainText(f"MIDI file saved to: {midi_path}")
            else:
                print("MIDI save dialog canceled.")  # Debug
        else:
            self.transcriptionDisplay.setPlainText("No MIDI file to save.")



    def savePdf(self):
        if hasattr(self.worker, 'temp_pdf_path') and os.path.exists(self.worker.temp_pdf_path):
            pdf_path, _ = QFileDialog.getSaveFileName(self, "Save PDF File", "", "PDF files (*.pdf)")
            if pdf_path:
                shutil.copy(self.worker.temp_pdf_path, pdf_path)
                self.transcriptionDisplay.setPlainText(f"PDF file saved to: {pdf_path}")
                # Optionally remove from temp files list and delete the temporary file
                if self.worker.temp_pdf_path in self.temp_files:
                    self.temp_files.remove(self.worker.temp_pdf_path)
                    os.remove(self.worker.temp_pdf_path)
        else:
            self.transcriptionDisplay.setPlainText("No PDF file to save.")


    def processFileInThread(self, fileName):
        self.progressBar.setRange(0, 0)
        self.thread = QThread(self)  # Ensuring that the thread is parented to avoid premature deletion

        temp_midi_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mid").name
        temp_pdf_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
        print("Temporary MIDI path in processFileInThread:", temp_midi_path)  # Debug

        # Initialize the worker with a callback that is thread-safe
        self.worker = TranscriptionWorker(audio_path=fileName, device='cpu')
        
        # Connect signals and slots
        self.worker.transcription_result.connect(self.displayTranscriptionResult)
        self.worker.finished.connect(self.onWorkerFinished)
        self.worker.moveToThread(self.thread)

        # Start the thread
        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def onWorkerFinished(self):
        # This will be triggered when the worker's `finished` signal is emitted
        self.progressBar.setRange(0, 1)  # Reset progress bar or indicate completion
        self.thread.quit()  # Ensure the thread is properly cleaned up
        self.thread.wait()  # Optional: wait for the thread to finish


    def displayTranscriptionResult(self, midi_path, pdf_path):
        self.progressBar.setRange(0, 1)
        #self.transcriptionDisplay.setPlainText("Transcription completed.")
        self.saveMidiButton.setEnabled(True)
        self.savePdfButton.setEnabled(True)
        if pdf_path:
            self.current_pdf_path = pdf_path  # Store the current PDF path
            self.display_pdf_from_path(pdf_path)  # Display the PDF automatically  # Display the PDF automatically
            self.playMidiButton.setEnabled(True)
        if midi_path:
            self.temp_files.append(midi_path)
            self.loadAndPlayGeneratedMIDI(midi_path)
        

    def display_pdf_from_path(self, pdf_path):
        if not os.path.exists(pdf_path):
            print(f"PDF file not found at: {pdf_path}")
            return

        try:
            # Ensure the PDF document is reloaded each time the function is called
            if not hasattr(self, 'pdfDocument'):  # Check if pdfDocument is already defined
                self.pdfDocument = QPdfDocument()

            self.pdfDocument.load(pdf_path)  # Load the PDF file into QPdfDocument
            self.pdfView.setDocument(self.pdfDocument)  # Set the document in QPdfView
        except Exception as e:
            print(f"Error displaying PDF: {e}")

    def resizeEvent(self, event):
        super(SoundToNotesApp, self).resizeEvent(event)
        if hasattr(self, 'current_pdf_path') and self.current_pdf_path:
            self.display_pdf_from_path(self.current_pdf_path)



    def loadAndPlayGeneratedMIDI(self, midi_path):
        if self.midi_player:
            self.midi_player.stop()
            self.midi_player.release()

        self.midi_player = vlc.MediaPlayer(midi_path)
        self.playMidiButton.setEnabled(True)
        self.pauseMidiButton.setEnabled(False)
        self.stopMidiButton.setEnabled(False)
        self.uploadedFileLabel.setText(f"Ready to play generated MIDI: {os.path.basename(midi_path)}")


    def playMedia(self):
        if self.mp3_player:
            self.mp3_player.play()
            self.pauseButton.setEnabled(True)
            self.stopButton.setEnabled(True)

    def togglePause(self):
        if self.mp3_player:
            if self.mp3_player.is_playing():
                self.mp3_player.pause()
            else:
                self.mp3_player.play()

    def stopMedia(self):
        if self.mp3_player:
            self.mp3_player.stop()
            self.pauseButton.setEnabled(False)
            self.stopButton.setEnabled(False)

    def playMediaMidi(self):
        if self.midi_player:
            self.midi_player.play()
            self.pauseMidiButton.setEnabled(True)
            self.stopMidiButton.setEnabled(True)

    def togglePauseMidi(self):
        if self.midi_player and self.midi_player.is_playing():
            self.midi_player.pause()
        elif self.midi_player:
            self.midi_player.play()

    def stopMediaMidi(self):
        if self.midi_player:
            self.midi_player.stop()
            self.pauseMidiButton.setEnabled(False)
            self.stopMidiButton.setEnabled(False)

    def closeEvent(self, event):
        if self.mp3_player:
            self.mp3_player.stop()
            self.mp3_player.release()
        if self.midi_player:
            self.midi_player.stop()
            self.midi_player.release()
        super().closeEvent(event)
        # Cleanup temporary files on application close
        for file_path in self.temp_files:
            if os.path.exists(file_path):
                os.remove(file_path)
        event.accept()