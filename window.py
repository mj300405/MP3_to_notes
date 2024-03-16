import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget,
                               QFileDialog, QProgressBar, QHBoxLayout, QGroupBox)
from PySide6.QtCore import QThread, QObject, Signal
from PySide6.QtGui import QIcon
import numpy as np
from audio_processor import PianoAudioProcessor

class AudioProcessingWorker(QObject):
    finished = Signal()
    progress = Signal(int)
    features_extracted = Signal(dict)

    def __init__(self, fileName, pianoAudioProcessor):
        super().__init__()
        self.fileName = fileName
        self.pianoAudioProcessor = pianoAudioProcessor

    def run(self):
        signal, sr = self.pianoAudioProcessor.load_audio(self.fileName)
        self.progress.emit(20)  # Emulate progress update
        features = self.pianoAudioProcessor.extract_features(signal, sr)
        self.progress.emit(100)  # Signal completion
        self.features_extracted.emit(features)
        self.finished.emit()

class SoundToNotesApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Sound to Notes Transcription')
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon('icon_path_here.png'))  # Update with the correct path to your icon
        self.pianoAudioProcessor = PianoAudioProcessor()
        self.initUI()

    def initUI(self):
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        mainLayout = QVBoxLayout(centralWidget)

        # Progress Bar
        self.progressBar = QProgressBar()
        mainLayout.addWidget(self.progressBar)

        # Upload Audio Group
        uploadGroupBox = QGroupBox("Upload Audio")
        uploadLayout = QHBoxLayout()
        self.uploadButton = QPushButton('Upload')
        self.uploadButton.clicked.connect(self.uploadFile)
        uploadLayout.addWidget(self.uploadButton)
        uploadGroupBox.setLayout(uploadLayout)
        mainLayout.addWidget(uploadGroupBox)

        # Transcription Display Group
        transcriptionGroupBox = QGroupBox("Transcription")
        transcriptionLayout = QVBoxLayout()
        self.transcriptionDisplay = QTextEdit()
        self.transcriptionDisplay.setPlaceholderText('Transcribed notes will be displayed here...')
        transcriptionLayout.addWidget(self.transcriptionDisplay)
        transcriptionGroupBox.setLayout(transcriptionLayout)
        mainLayout.addWidget(transcriptionGroupBox)

        # Controls Group
        controlsGroupBox = QGroupBox("Controls")
        controlsLayout = QHBoxLayout()
        self.playButton = QPushButton('Play')
        self.playButton.clicked.connect(self.playAudio)  # Implement this method
        controlsLayout.addWidget(self.playButton)

        self.saveButton = QPushButton('Save')
        self.saveButton.clicked.connect(self.saveTranscription)  # Implement this method
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
        self.thread = QThread()
        self.worker = AudioProcessingWorker(fileName, self.pianoAudioProcessor)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.progressBar.setValue)
        self.worker.features_extracted.connect(self.display_feature_summary)
        self.thread.start()

    def display_feature_summary(self, features):
        feature_summary = "Extracted Features Summary:\n"
        for name, feature in features.items():
            feature_summary += f"{name}: shape {str(feature.shape)}\n"
        self.transcriptionDisplay.setPlainText(feature_summary)
        self.progressBar.setValue(0)  # Reset progress bar
    
    def prepare_features_for_model(features):
        # Flatten the features that have more than one dimension
        flattened_features = [features[key].flatten() for key in features if len(features[key].shape) > 1]
        feature_vector = np.concatenate(flattened_features)
        feature_vector = (feature_vector - feature_vector.mean()) / feature_vector.std()
        return feature_vector


    # Implement the playAudio method
    def playAudio(self):
        print("Playing audio...")  # Placeholder for actual audio playback functionality

    # Implement the saveTranscription method
    def saveTranscription(self):
        print("Saving transcription...")  # Placeholder for actual save functionality

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = SoundToNotesApp()
    mainWindow.show()
    sys.exit(app.exec())
