import sys
import os
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QComboBox, QTextEdit, QTabWidget, QMessageBox
)
from PyQt6.QtCore import Qt

# Set the base path for PyInstaller
if getattr(sys, 'frozen', False):
    BASE_PATH = sys._MEIPASS
else:
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(BASE_PATH, "ringzauber_config.json")
ENV_FILE = os.path.join(BASE_PATH, "protect.env")

class SettingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ringzauber Settings & Manual")
        self.setFixedSize(700, 600)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Initialize UI Tabs
        self.init_preferences_tab()
        self.init_how_to_use_tab()
        self.init_commands_tab()
        self.init_about_tab()
        self.init_terms_tab()

        # Bottom Buttons
        self.button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save & Apply")
        self.save_btn.setStyleSheet("background-color: #2ecc71; color: white; padding: 10px; font-weight: bold;")
        self.save_btn.clicked.connect(self.save_settings)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.setStyleSheet("padding: 10px;")
        self.close_btn.clicked.connect(self.close)
        
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.close_btn)
        self.button_layout.addWidget(self.save_btn)
        self.layout.addLayout(self.button_layout)

        self.load_current_settings()

    def init_preferences_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("<h3>Browser Preferences</h3>"))
        layout.addWidget(QLabel("Default Search Engine:"))
        self.search_combo = QComboBox()
        self.search_combo.addItems(["Ecosia", "DuckDuckGo", "Yahoo", "Oodles"])
        layout.addWidget(self.search_combo)
        layout.addSpacing(20)
        layout.addWidget(QLabel("Praterich AI Personality:"))
        self.personality_combo = QComboBox()
        self.personality_combo.addItems(["Classic", "Friendly", "Professional", "Sarcastic"])
        layout.addWidget(self.personality_combo)
        layout.addStretch()
        self.tabs.addTab(tab, "General")

    def init_how_to_use_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setHtml("""
            <h2>How to Use Ringzauber</h2>
            <p><b>1. Browsing:</b> Use the address bar at the top to enter URLs or search terms. Ringzauber supports multi-tab browsing.</p>
            <p><b>2. Praterich Plus:</b> The side panel on the right is your AI assistant. You can type requests in plain English, and it will either answer your question or perform an action.</p>
            <p><b>3. Vision:</b> Praterich can "see." If you upload an image or take a screenshot within the browser, you can ask Praterich to analyze the UI, read text from the image, or explain visual content.</p>
            <p><b>4. Notes:</b> Use the built-in Notes tool to save snippets of information while you browse. You can ask Praterich to 'add this to my notes'.</p>
            <p><b>5. Customization:</b> Change your AI's personality in the 'General' tab to change how Praterich interacts with you.</p>
        """)
        layout.addWidget(help_text)
        self.tabs.addTab(tab, "How to Use")

    def init_commands_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        cmd_text = QTextEdit()
        cmd_text.setReadOnly(True)
        cmd_text.setHtml("""
            <h2>AI Command Reference</h2>
            <p>Praterich Plus understands natural language, but here are the specific system commands it can trigger:</p>
            <ul>
                <li><b>NAVIGATE / SEARCH:</b> "Go to google.com" or "Search for news about space."</li>
                <li><b>TAB MANAGEMENT:</b> "Open a new tab," "Close this tab," or "Switch to the first tab."</li>
                <li><b>PAGE CONTROL:</b> "Reload the page," "Go back," or "Zoom in."</li>
                <li><b>UTILITIES:</b> "Open notes," "Edit page," "Set font size," or "Print to PDF."</li>
                <li><b>LAYOUT:</b> "Toggle sidebar," "Horizontal tabs," or "Vertical tabs."</li>
                <li><b>ADVANCED:</b> "Crawl this site" (using Oodles), "Developer tools," or "Translate page."</li>
            </ul>
            <p><i>Note: You don't need to type the command name. Just say "Hey Praterich, can you zoom in for me?"</i></p>
        """)
        layout.addWidget(cmd_text)
        self.tabs.addTab(tab, "Commands")

    def init_about_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        about_text = QLabel(
            "<center><h1>Ringzauber</h1>"
            "<b>Version 1.6 (Plus Edition)</b><br><br>"
            "Developed by <b>Stenoip Company</b><br>"
            "<a href='https://stenoip.github.io'>stenoip.github.io</a><br><br>"
            "Ringzauber is an A.I browser built with PyQt6 and LLM technology.<br>"
            "All rights reserved © 2025-2026.</center>"
        )
        about_text.setOpenExternalLinks(True)
        layout.addWidget(about_text)
        layout.addStretch()
        self.tabs.addTab(tab, "About")

    def init_terms_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        terms_display = QTextEdit()
        terms_display.setReadOnly(True)
        terms_display.setText("NOTICE: Ringzauber is a Work in Progress.\n\nCopyright (c) 2025 Stenoip Company. All rights reserved...")
        layout.addWidget(terms_display)
        self.tabs.addTab(tab, "Terms")

    def load_current_settings(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    self.search_combo.setCurrentText(data.get("default_search_engine", "Ecosia"))
                    self.personality_combo.setCurrentText(data.get("praterich_personality", "Classic"))
            except: pass

    def save_settings(self):
        selected_engine = self.search_combo.currentText()
        selected_personality = self.personality_combo.currentText()
        config_data = {"default_search_engine": selected_engine, "praterich_personality": selected_personality}
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config_data, f, indent=4)

        env_lines = []
        if os.path.exists(ENV_FILE):
            with open(ENV_FILE, 'r') as f: env_lines = f.readlines()

        updated_lines = [l for l in env_lines if not l.startswith(("SEARCH_ENGINE=", "PERSONALITY="))]
        updated_lines.append(f"SEARCH_ENGINE={selected_engine}\n")
        updated_lines.append(f"PERSONALITY={selected_personality}\n")

        with open(ENV_FILE, 'w') as f: f.writelines(updated_lines)
        QMessageBox.information(self, "Success", "Settings saved successfully!")
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SettingsWindow()
    window.show()
    sys.exit(app.exec())
