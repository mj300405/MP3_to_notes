import sys
import fitz  # PyMuPDF
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget, QFileDialog, QProgressBar, QHBoxLayout, QGroupBox, QLabel, QScrollArea, QSizePolicy
from PySide6.QtCore import QThread, Qt
from PySide6.QtGui import QIcon, QPixmap, QImage
from transcription_worker import TranscriptionWorker
import os
import shutil
import tempfile

class SoundToNotesApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Sound to Notes Transcription')
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon('adds/favicon.ico'))  # Ensure this path is correct
        self.initUI()
        self.temp_files = []  # List to manage temporary files
        self.current_pdf_path = None  # Store the current PDF path

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
        self.uploadedFileLabel = QLabel("No file uploaded")
        uploadLayout.addWidget(self.uploadedFileLabel)
        uploadGroupBox.setLayout(uploadLayout)
        mainLayout.addWidget(uploadGroupBox)

        transcriptionGroupBox = QGroupBox("Transcription")
        transcriptionLayout = QVBoxLayout()
        self.transcriptionDisplay = QTextEdit()
        self.transcriptionDisplay.setPlaceholderText('Saved file path will be displayed here...')
        self.transcriptionDisplay.setMaximumHeight(50)
        transcriptionLayout.addWidget(self.transcriptionDisplay)
        
        # PDF Display Section with Scroll Area
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)  # Allows the contained widget to resize freely
        self.scrollArea.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # May need to import QSizePolicy
        self.pdfDisplayLabel = QLabel("PDF preview will appear here")
        self.pdfDisplayLabel.setAlignment(Qt.AlignCenter)
        self.pdfDisplayLabel.setScaledContents(False)
        self.scrollArea.setWidget(self.pdfDisplayLabel)  # Adding the label to the scroll area
        transcriptionLayout.addWidget(self.scrollArea)  # Adding the scroll area to the layout
        
        transcriptionGroupBox.setLayout(transcriptionLayout)
        mainLayout.addWidget(transcriptionGroupBox)

        controlsGroupBox = QGroupBox("Controls")
        controlsLayout = QHBoxLayout()
        self.transcribeButton = QPushButton('Transcribe')
        self.transcribeButton.clicked.connect(self.startTranscription)
        self.transcribeButton.setEnabled(False)
        controlsLayout.addWidget(self.transcribeButton)
        
        self.playButton = QPushButton('Play')
        self.playButton.clicked.connect(lambda: print("Play button clicked"))
        controlsLayout.addWidget(self.playButton)

        self.saveMidiButton = QPushButton('Save MIDI')
        self.saveMidiButton.clicked.connect(self.saveMidi)
        self.saveMidiButton.setEnabled(False)
        controlsLayout.addWidget(self.saveMidiButton)

        self.savePdfButton = QPushButton('Save PDF')
        self.savePdfButton.clicked.connect(self.savePdf)
        self.savePdfButton.setEnabled(False)
        controlsLayout.addWidget(self.savePdfButton)

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
            self.uploadedFileName = fileName
            self.uploadedFileLabel.setText(f"Uploaded file: {fileName.split('/')[-1]}")
            self.transcribeButton.setEnabled(True)
            self.saveMidiButton.setEnabled(False)
            self.savePdfButton.setEnabled(False)


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
        self.thread = QThread()

        temp_midi_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mid").name
        temp_pdf_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
        print("Temporary MIDI path in processFileInThread:", temp_midi_path)  # Debug

        # Update TranscriptionWorker initialization to match the new constructor
        self.worker = TranscriptionWorker(audio_path=fileName,
                                        device='cpu',  # Assuming 'cpu' use, adjust as necessary
                                        display_callback=self.display_pdf_from_path)

        self.worker.moveToThread(self.thread)
        self.worker.finished.connect(self.thread.quit)
        self.worker.transcription_result.connect(self.displayTranscriptionResult)
        self.thread.started.connect(self.worker.run)
        self.thread.start()


    def displayTranscriptionResult(self, midi_path, pdf_path):
        self.progressBar.setRange(0, 1)
        self.transcriptionDisplay.setPlainText("Transcription completed.")
        self.saveMidiButton.setEnabled(True)
        self.savePdfButton.setEnabled(True)
        if pdf_path:
            self.current_pdf_path = pdf_path  # Store the current PDF path
            self.display_pdf_from_path(pdf_path)  # Display the PDF automatically  # Display the PDF automatically

    # def display_pdf_from_path(self, pdf_path):
    #     try:
    #         if not os.path.exists(pdf_path):
    #             raise FileNotFoundError(f"PDF file not found at {pdf_path}")

    #         doc = fitz.open(pdf_path)
    #         if doc.page_count == 0:
    #             raise ValueError("PDF document is empty or corrupted")

    #         page = doc[0]
    #         # Render the page to a higher resolution pixmap before scaling.
    #         pix = page.get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72))
    #         img = QImage(pix.samples, pix.width, pix.height, QImage.Format_RGB888)
    #         pixmap = QPixmap.fromImage(img)
    #         # Scale the pixmap to the QLabel size while preserving the aspect ratio.
    #         scaled_pixmap = pixmap.scaled(self.pdfDisplayLabel.width(), self.pdfDisplayLabel.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
    #         self.pdfDisplayLabel.setPixmap(scaled_pixmap)
    #         doc.close()
    #     except Exception as e:
    #         print(f"Error displaying PDF: {e}")
    def display_pdf_from_path(self, pdf_path):
        try:
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF file not found at {pdf_path}")
            
            doc = fitz.open(pdf_path)
            page = doc[0]
            pix = page.get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72))  # Adjust scale here as necessary
            img = QImage(pix.samples, pix.width, pix.height, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(img)
            
            # Use Qt.KeepAspectRatio to maintain aspect ratio
            scaled_pixmap = pixmap.scaled(self.pdfDisplayLabel.width(), self.pdfDisplayLabel.height(), 
                                        Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            self.pdfDisplayLabel.setPixmap(scaled_pixmap)
            doc.close()
        except Exception as e:
            print(f"Error displaying PDF: {e}")
            self.pdfDisplayLabel.clear()




    def resizeEvent(self, event):
        super(SoundToNotesApp, self).resizeEvent(event)  # Make sure to call the base class method
        if self.current_pdf_path:
            self.display_pdf_from_path(self.current_pdf_path)




    def closeEvent(self, event):
        # Cleanup temporary files on application close
        for file_path in self.temp_files:
            if os.path.exists(file_path):
                os.remove(file_path)
        event.accept()