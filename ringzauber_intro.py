import sys
import subprocess
import os
import json

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QStackedWidget,
                             QTextEdit, QComboBox)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import QUrl, QDir, Qt, QSize

class RingzauberSetup(QMainWindow):
    """The main application window for the Ringzauber setup wizard."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ringzauber Setup v1.5")
        self.setGeometry(100, 100, 800, 600)
        
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Initialize and add all pages to the stacked widget
        self.init_ui()

    def init_ui(self):
        """Initializes and sets up all the pages of the wizard."""
        # Page 1: Welcome Screen
        welcome_page = QWidget()
        welcome_layout = QVBoxLayout()
        welcome_label = QLabel("<h1>Welcome to Ringzauber</h1><p>Version 1.5</p>")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        next_button1 = QPushButton("Next")
        next_button1.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        welcome_layout.addWidget(welcome_label)
        welcome_layout.addWidget(next_button1)
        welcome_page.setLayout(welcome_layout)
        self.stacked_widget.addWidget(welcome_page)
        
        # Page 2: Terms and Conditions
        terms_page = QWidget()
        terms_layout = QVBoxLayout()
        terms_label = QLabel("<h2>Ringzauber Terms of Service</h2>")
        terms_text = QTextEdit()
        terms_text.setReadOnly(True)
        terms_text.setText(
            """
            NOTICE: Ringzauber is a Work in Progress.

            Copyright (c) 2025 Stenoip Company. All rights reserved.
            
            This document outlines the Terms of Service for the Ringzauber application ("Ringzauber"). 
            By installing, accessing, or using Ringzauber, you agree to be bound by these terms. 
            If you do not agree, you may not use the application.

            1. Acceptance of Terms
            Your use of Ringzauber constitutes your full acceptance of this agreement. 
            These terms may be updated at any time, and continued use after any such changes 
            constitutes your consent to the new terms.

            2. Description of Service
            Ringzauber is a web browser application designed to facilitate web browsing and other related 
            functions. Its features include, but are not limited to, tab management, search functionality, 
            and a conversational AI assistant.

            3. User Conduct
            You agree to use Ringzauber only for lawful purposes. You shall not use Ringzauber to:
            a. Engage in any illegal activity or promote illegal acts.
            b. Transmit any malicious code, viruses, or other harmful data.
            c. Infringe upon the intellectual property rights of others.
            d. Interfere with or disrupt the application's functionality.

            4. Privacy Policy
            Ringzauber is designed to respect your privacy. The application does not collect 
            personally identifiable information from you without your explicit consent. 
            Please refer to our full Privacy Policy for detailed information on how we handle data.

            5. Intellectual Property
            The Ringzauber application, its design, code, and any intellectual property 
            contained within, are the exclusive property of stenoip company. You are granted a 
            limited, non-exclusive, non-transferable license to use the application for your 
            personal use. You may not modify, distribute, or create derivative works from Ringzauber.

            6. Disclaimer of Warranties
            RINGZAUBER IS PROVIDED "AS IS" AND WITHOUT ANY WARRANTY OF ANY KIND, EITHER 
            EXPRESS OR IMPLIED. WE DO NOT WARRANT THAT THE APPLICATION WILL BE UNINTERRUPTED, 
            ERROR-FREE, OR SECURE. YOUR USE OF RINGZAUBER IS AT YOUR SOLE RISK.

            7. Limitation of Liability
            IN NO EVENT SHALL STENOIP COMPANY BE LIABLE FOR ANY DAMAGES (INCLUDING, BUT NOT 
            LIMITED TO, INCIDENTAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES) ARISING FROM YOUR USE 
            OF RINGZAUBER, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.

            8. Modifications to Terms
            We reserve the right to modify these Terms of Service at any time. Your continued 
            use of the application after any such changes will signify your acceptance of the 
            new terms.

            9. Contact Information
            If you have any questions about these Terms of Service, please contact us at 
            customerservivecustomerserviceforstenoip@gmail.com

            This is a fictional terms of service document for demonstration purposes. 
            Consult with a legal professional for real-world applications.
            """
        )
        next_button2 = QPushButton("Next")
        next_button2.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        terms_layout.addWidget(terms_label)
        terms_layout.addWidget(terms_text)
        terms_layout.addWidget(next_button2)
        terms_page.setLayout(terms_layout)
        self.stacked_widget.addWidget(terms_page)
        
        # Page 3: Video
        video_page = QWidget()
        video_layout = QVBoxLayout()
        
        video_title = QLabel("<h2>Watch a quick intro to Ringzauber</h2>")
        video_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Setup video player
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        
        self.video_widget = QVideoWidget()
        self.media_player.setVideoOutput(self.video_widget)
        
        video_path = QDir.currentPath() + "/ringzauber_video.mp4"
        if os.path.exists(video_path):
            self.media_player.setSource(QUrl.fromLocalFile(video_path))
            self.media_player.play()
        else:
            video_status_label = QLabel("Video not found. Please place 'ringzauber_video.mp4' in the script directory.")
            video_layout.addWidget(video_status_label)
        
        next_button3 = QPushButton("Next")
        next_button3.clicked.connect(self.stop_video)
        next_button3.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))
        
        video_layout.addWidget(video_title)
        video_layout.addWidget(self.video_widget)
        video_layout.addWidget(next_button3)
        video_page.setLayout(video_layout)
        self.stacked_widget.addWidget(video_page)

        # Page 4: Search Engine Selection
        search_engine_page = QWidget()
        search_engine_layout = QVBoxLayout()
        search_engine_label = QLabel("<h2>Choose your default search engine</h2>")
        
        self.search_combo_box = QComboBox()
        self.search_combo_box.addItem("Ecosia")
        self.search_combo_box.addItem("DuckDuckGo")
        self.search_combo_box.addItem("Yahoo")
        
        next_button4 = QPushButton("Done")
        next_button4.clicked.connect(self.complete_setup)

        search_engine_layout.addWidget(search_engine_label)
        search_engine_layout.addWidget(self.search_combo_box)
        search_engine_layout.addWidget(next_button4)
        search_engine_page.setLayout(search_engine_layout)
        self.stacked_widget.addWidget(search_engine_page)

    def stop_video(self):
        """Stops the video playback."""
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.stop()

    def complete_setup(self):
        """Finalizes the setup, saves the configuration, and launches the main browser."""
        selected_engine = self.search_combo_box.currentText()
        config_data = {"default_search_engine": selected_engine}
        
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ringzauber_config.json')
        with open(config_path, 'w') as f:
            json.dump(config_data, f)
        
        print(f"Setup complete. Default search engine set to: {selected_engine}")
        
        try:
            subprocess.Popen([sys.executable, 'ringzauber.py'])
        except FileNotFoundError:
            print("Error: ringzauber.py not found. Make sure it's in the same directory.")
        
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RingzauberSetup()
    window.show()
    sys.exit(app.exec())
