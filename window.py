# window.py
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget, QFileDialog, QProgressBar, QHBoxLayout, QGroupBox
from PySide6.QtCore import QThread
from PySide6.QtGui import QIcon
from transcription_worker import TranscriptionWorker

class SoundToNotesApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Sound to Notes Transcription')
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon('path/to/your/icon.png'))  # Update this path to your application's icon
        self.initUI()

    def initUI(self):
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        mainLayout = QVBoxLayout(centralWidget)

        self.progressBar = QProgressBar()
        mainLayout.addWidget(self.progressBar)

        uploadGroupBox = QGroupBox("Upload Audio")
        uploadLayout = QHBoxLayout()
        self.uploadButton = QPushButton('Upload')
        self.uploadButton.clicked.connect(self.uploadFile)
        uploadLayout.addWidget(self.uploadButton)
        uploadGroupBox.setLayout(uploadLayout)
        mainLayout.addWidget(uploadGroupBox)

        transcriptionGroupBox = QGroupBox("Transcription")
        transcriptionLayout = QVBoxLayout()
        self.transcriptionDisplay = QTextEdit()
        self.transcriptionDisplay.setPlaceholderText('Transcribed notes will be displayed here...')
        transcriptionLayout.addWidget(self.transcriptionDisplay)
        transcriptionGroupBox.setLayout(transcriptionLayout)
        mainLayout.addWidget(transcriptionGroupBox)

        controlsGroupBox = QGroupBox("Controls")
        controlsLayout = QHBoxLayout()
        self.playButton = QPushButton('Play')
        # Placeholder - Implement actual audio playback functionality
        self.playButton.clicked.connect(lambda: print("Play button clicked"))
        controlsLayout.addWidget(self.playButton)

        self.saveButton = QPushButton('Save')
        # Placeholder - Implement actual functionality to save transcription results
        self.saveButton.clicked.connect(lambda: print("Save button clicked"))
        controlsLayout.addWidget(self.saveButton)
        controlsGroupBox.setLayout(controlsLayout)
        mainLayout.addWidget(controlsGroupBox)

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
            self.processFileInThread(fileName)


    def processFileInThread(self, fileName):
        self.progressBar.setRange(0, 0)  # Indeterminate progress
        self.thread = QThread()
        # Specify the model_type here, adjust according to your model
        model_type = "Note_pedal"
        checkpoint_path = "checkpoints/best_model_2.pth"
        self.worker = TranscriptionWorker(fileName, model_type, checkpoint_path)
        self.worker.moveToThread(self.thread)
        self.worker.finished.connect(self.thread.quit)
        self.worker.transcription_result.connect(self.displayTranscriptionResult)
        self.thread.started.connect(self.worker.run)
        self.thread.start()


    def displayTranscriptionResult(self, midi_path):
        self.progressBar.setRange(0, 1)  # Reset progress bar to default
        self.transcriptionDisplay.setPlainText(f"Transcription completed. MIDI file saved to: {midi_path}")