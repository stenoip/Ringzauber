import sys
import os
import json
import subprocess
from PyQt6.QtCore import QUrl, QSize, QObject, pyqtSlot, QRunnable, QThreadPool, pyqtSignal, QTimer
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QLineEdit, QStatusBar,
    QWidget, QTabWidget, QLabel, QMenu, QFileDialog, QPushButton,
    QVBoxLayout, QHBoxLayout, QListWidget, QFrame, QDialog, QTextEdit,
    QListWidgetItem, QStyle, QMessageBox
)
from PyQt6.QtGui import QAction, QIcon, QContextMenuEvent, QFontDatabase, QFont, QKeySequence
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineDownloadRequest
from PyQt6.QtWebChannel import QWebChannel
from praterich_ai import get_praterich_response_text
from ringzauber_ui import (
    PraterichSidePanel, CustomWebEngineView, NotesDialog, PraterichRequestWorker, WebChannelHandler
)
# Import speech recognition library
import speech_recognition as sr

class PraterichBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QHBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs, 1)
        self.tabs.setTabsClosable(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        
        self.praterich_panel = PraterichSidePanel()
        self.main_layout.addWidget(self.praterich_panel)
        self.praterich_panel.setVisible(False)
        
        self.download_list_dialog = None
        self.notes_dialog = NotesDialog(self)
        self.closed_tabs = []

        QWebEngineProfile.defaultProfile().downloadRequested.connect(self.on_download_requested)

        self.setup_ui()
        self.setup_keyboard_shortcuts()
        self.load_custom_font()
        
        # Load the user's default search engine from a configuration file.
        self.load_default_search_engine()

        self.home_url = QUrl.fromLocalFile(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'new_tab.html'))
        self.add_new_tab(self.home_url)

    def load_default_search_engine(self):
        """Loads the default search engine URL from a configuration file."""
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ringzauber_config.json')
        self.default_search_url = "https://www.google.com/search?q="  # Fallback to Google

        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    search_engine = config.get("default_search_engine", "google").lower()
                    if search_engine == "duckduckgo":
                        self.default_search_url = "https://duckduckgo.com/?q="
                    elif search_engine == "yahoo":
                        self.default_search_url = "https://search.yahoo.com/search?p="
                    elif search_engine == "ecosia":
                        self.default_search_url = "https://www.ecosia.org/search?q="
                    # Google is the default if no match is found
            except Exception as e:
                print(f"Error reading configuration file: {e}")
                QMessageBox.warning(self, "Configuration Error", "Could not load default search engine. Using Google.")
        else:
            QMessageBox.information(self, "Setup Incomplete", "Please run ringzauber_intro.py to set your preferences.")

    def setup_ui(self):
        navtb = QToolBar("Navigation")
        navtb.setIconSize(QSize(24, 24))
        self.addToolBar(navtb)

        forward_btn = QAction(QIcon("forward.png"), 'Forward', self)
        forward_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        navtb.addAction(forward_btn) 

        back_btn = QAction(QIcon("back.png"), 'Back', self)
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())
        navtb.addAction(back_btn)

        reload_btn = QAction(QIcon("reload.png"), 'Reload', self)
        reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        navtb.addAction(reload_btn)

        home_btn = QAction(QIcon("home.png"), 'Home', self)
        home_btn.triggered.connect(self.navigate_home)
        navtb.addAction(home_btn)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navtb.addWidget(self.url_bar)
        
        self.tabs.currentChanged.connect(self.update_url)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        downloads_btn = QPushButton("Downloads")
        downloads_btn.setIcon(QIcon("download.png"))
        downloads_btn.clicked.connect(self.show_downloads_list)
        self.status_bar.addPermanentWidget(downloads_btn)

        praterich_btn = QPushButton("Praterich")
        praterich_btn.setIcon(QIcon("praterich_icon.png"))
        praterich_btn.clicked.connect(self.toggle_praterich_panel)
        self.status_bar.addPermanentWidget(praterich_btn)
        
        notes_btn = QPushButton("Notes")
        notes_btn.setIcon(QIcon("notes.png"))
        notes_btn.clicked.connect(self.notes_dialog.show)
        self.status_bar.addPermanentWidget(notes_btn)

        terminal_btn = QPushButton("Terminal")
        terminal_btn.setIcon(QIcon("terminal.png"))
        terminal_btn.clicked.connect(self.open_terminal)
        self.status_bar.addPermanentWidget(terminal_btn)
        
        self.praterich_panel.command_bar.returnPressed.connect(self.on_praterich_command)
        self.praterich_panel.upload_btn.clicked.connect(self.upload_file)
        self.praterich_panel.new_chat_btn.clicked.connect(self.praterich_panel.clear_chat)
        
    def setup_keyboard_shortcuts(self):
        self.new_tab_action = QAction("New Tab", self, shortcut=QKeySequence("Ctrl+T"), triggered=lambda: self.add_new_tab())
        self.addAction(self.new_tab_action)

        self.close_tab_action = QAction("Close Tab", self, shortcut=QKeySequence("Ctrl+W"), triggered=lambda: self.close_current_tab(self.tabs.currentIndex()))
        self.addAction(self.close_tab_action)
        
        self.reopen_tab_action = QAction("Reopen Tab", self, shortcut=QKeySequence("Ctrl+Shift+T"), triggered=self.reopen_last_closed_tab)
        self.addAction(self.reopen_tab_action)
        
        self.next_tab_action = QAction("Next Tab", self, shortcut=QKeySequence("Ctrl+Tab"), triggered=lambda: self.tabs.setCurrentIndex((self.tabs.currentIndex() + 1) % self.tabs.count()))
        self.addAction(self.next_tab_action)

        self.previous_tab_action = QAction("Previous Tab", self, shortcut=QKeySequence("Ctrl+Shift+Tab"), triggered=lambda: self.tabs.setCurrentIndex((self.tabs.currentIndex() - 1 + self.tabs.count()) % self.tabs.count()))
        self.addAction(self.previous_tab_action)
        
        for i in range(1, 10):
            action = QAction(f"Go to Tab {i}", self, shortcut=QKeySequence(f"Ctrl+{i}"), triggered=lambda i=i: self.tabs.setCurrentIndex(i-1))
            self.addAction(action)
        
        self.new_window_action = QAction("New Window", self, shortcut=QKeySequence("Ctrl+N"), triggered=self.new_window)
        self.addAction(self.new_window_action)
        
        self.close_window_action = QAction("Close Window", self, shortcut=QKeySequence("Ctrl+Shift+W"), triggered=self.close)
        self.addAction(self.close_window_action)

    def reopen_last_closed_tab(self):
        if self.closed_tabs:
            last_tab_data = self.closed_tabs.pop()
            url = last_tab_data.get('url')
            self.add_new_tab(QUrl(url))
        else:
            self.praterich_panel.start_typing_effect("There are no recently closed tabs to reopen.")
    
    def new_window(self):
        new_browser = PraterichBrowser()
        new_browser.show()

    def show_downloads_list(self):
        if not hasattr(self, 'download_list_widget') or not self.download_list_widget:
            self.download_list_widget = QListWidget()
            self.download_list_dialog = QDialog(self)
            self.download_list_dialog.setWindowTitle("Downloads")
            self.download_list_dialog.setFixedSize(400, 300)
            
            layout = QVBoxLayout(self.download_list_dialog)
            layout.addWidget(self.download_list_widget)
            
        self.download_list_dialog.exec()

    def on_download_requested(self, download: QWebEngineDownloadRequest):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", download.path())
        if file_path:
            download.setPath(file_path)
            download.accept()
            download.stateChanged.connect(lambda: self.update_download_status(download))
            self.download_list_widget.addItem(f"Downloading: {os.path.basename(file_path)}")
        else:
            download.cancel()

    def update_download_status(self, download):
        for i in range(self.download_list_widget.count()):
            item = self.download_list_widget.item(i)
            if download.path() in item.text():
                if download.state() == QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
                    item.setText(f"Completed: {os.path.basename(download.path())}")
                elif download.state() == QWebEngineDownloadRequest.DownloadState.DownloadCancelled:
                    item.setText(f"Cancelled: {os.path.basename(download.path())}")
                elif download.state() == QWebEngineDownloadRequest.DownloadState.DownloadInterrupted:
                    item.setText(f"Interrupted: {os.path.basename(download.path())}")
                return

    def toggle_praterich_panel(self):
        self.praterich_panel.setVisible(not self.praterich_panel.isVisible())

    def add_new_tab(self, qurl=None):
        if qurl is None:
            qurl = self.home_url

        browser = CustomWebEngineView(self, browser=self)
        browser.setUrl(qurl)
        
        i = self.tabs.addTab(browser, "New Tab")
        self.tabs.setCurrentIndex(i)
        
        browser.urlChanged.connect(lambda qurl, browser=browser: self.update_url(qurl))
        browser.loadFinished.connect(lambda ok: self.update_title(browser))

    def update_title(self, browser):
        if browser != self.tabs.currentWidget():
            return
        
        title = browser.title()
        index = self.tabs.indexOf(browser)
        self.tabs.setTabText(index, title)

    def update_url(self, qurl):
        if self.tabs.currentWidget() and self.tabs.currentWidget().url() == qurl:
            self.url_bar.setText(qurl.toString())
    
    def navigate_to_url(self):
        url_text = self.url_bar.text()
        if not url_text:
            return
        
        if "." not in url_text or " " in url_text:
            url = f"{self.default_search_url}{url_text}"
        elif not url_text.startswith(("http://", "https://")):
            url = f"https://{url_text}"
        else:
            url = url_text

        self.tabs.currentWidget().setUrl(QUrl(url))
        self.url_bar.setText(url)
        
    def close_current_tab(self, index):
        if self.tabs.count() < 2:
            self.close()
            return
            
        browser = self.tabs.widget(index)
        
        tab_data = {'url': browser.url().toString()}
        self.closed_tabs.append(tab_data)
        
        browser.deleteLater()
        self.tabs.removeTab(index)
        
    def tab_open_doubleclick(self, index):
        if index == -1:
            self.add_new_tab()

    def navigate_home(self):
        self.tabs.currentWidget().setUrl(self.home_url)

    def on_praterich_command(self, user_query=None):
        if not user_query:
            user_query = self.praterich_panel.command_bar.text()
            self.praterich_panel.command_bar.clear()
        
        self.praterich_panel.show_thinking_message("Thinking...")
        
        worker = PraterichRequestWorker(user_query)
        worker.signals.result.connect(self.perform_praterich_action)
        worker.signals.error.connect(self.handle_ai_error_on_command)
        self.praterich_panel.thread_pool.start(worker)

    def handle_ai_error_on_command(self, error_message):
        self.praterich_panel.start_typing_effect(f"Error: {error_message}")
        self.praterich_panel.hide_thinking_message()

    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Upload File")
        if file_path:
            self.praterich_panel.start_typing_effect(f"Understood. I will process the file located at: {file_path}")

    def perform_praterich_action(self, response):
        command = response.get("command")
        query = response.get("query")
        message = response.get("message")
        
        self.praterich_panel.start_typing_effect(message)
        self.praterich_panel.hide_thinking_message()

        if command == "NAVIGATE":
            self.add_new_tab(QUrl(query))
        elif command == "SEARCH":
            # Use the default search engine URL
            search_url = f"{self.default_search_url}{query}"
            self.add_new_tab(QUrl(search_url))
        elif command == "NEW_TAB":
            num_tabs = int(query) if query else 1
            for _ in range(num_tabs):
                self.add_new_tab(self.home_url)
        elif command == "CLOSE_TAB":
            self.close_current_tab(self.tabs.currentIndex())
        elif command == "RELOAD":
            self.tabs.currentWidget().reload()
        elif command == "GO_BACK":
            self.tabs.currentWidget().back()
        elif command == "GO_FORWARD":
            self.tabs.currentWidget().forward()
        elif command == "SET_COLOR":
            self.setStyleSheet(f"QMainWindow {{ background-color: {query}; }}")
        elif command == "EDIT_PAGE":
            self.tabs.currentWidget().page().runJavaScript(query)
        elif command == "EDIT_CODE":
            self.status_bar.showMessage("Editing code is not enabled in this version.")
        elif command == "SET_FONT":
            QApplication.instance().setStyleSheet(f"QApplication {{ {query} }}")
        elif command == "UPLOAD_FILE":
            file_path, _ = QFileDialog.getOpenFileName(self, "Select a File to Upload")
            if file_path:
                response_message = f"File selected: {file_path}. Processing with Praterich..."
                self.praterich_panel.start_typing_effect(response_message)
        elif command == "TOGGLE_SIDEBAR":
            self.praterich_panel.setVisible(not self.praterich_panel.isVisible())
        elif command == "MANAGE_EXTENSIONS":
            self.praterich_panel.start_typing_effect("I am afraid I cannot manage extensions at this moment, as this feature is still under development.")
        elif command == "SYNC_DATA":
            self.praterich_panel.start_typing_effect("Data synchronization is not yet implemented. Please check for a future update.")
        elif command == "TRANSLATE_PAGE":
            translate_js = f"window.open('https://translate.google.com/?sl=auto&tl={query}&text=' + encodeURIComponent(document.body.innerText), '_blank');"
            self.tabs.currentWidget().page().runJavaScript(translate_js)
        elif command == "CHANGE_SETTINGS":
            self.praterich_panel.start_typing_effect("Current settings cannot be changed via command. A settings menu will be implemented in a future update.")
        elif command == "DEVELOPER_TOOLS":
            self.tabs.currentWidget().page().action(QWebEnginePage.WebAction.InspectElement).trigger()
        elif command == "ZOOM_IN":
            current_zoom = self.tabs.currentWidget().zoomFactor()
            self.tabs.currentWidget().setZoomFactor(current_zoom + 0.1)
        elif command == "ZOOM_OUT":
            current_zoom = self.tabs.currentWidget().zoomFactor()
            self.tabs.currentWidget().setZoomFactor(current_zoom - 0.1)
        elif command == "FIND_ON_PAGE":
            self.tabs.currentWidget().findText(query)
        elif command == "PRINT_TO_PDF":
            file_path, _ = QFileDialog.getSaveFileName(self, "Save as PDF", "", "PDF Files (*.pdf)")
            if file_path:
                self.tabs.currentWidget().page().printToPdf(file_path)
        elif command == "BOOKMARK_PAGE":
            self.praterich_panel.start_typing_effect("The bookmarking feature is not yet available, my apologies. I will remember this for a future update.")
        elif command == "SWITCH_TAB":
            try:
                tab_index = int(query) - 1
                if 0 <= tab_index < self.tabs.count():
                    self.tabs.setCurrentIndex(tab_index)
                else:
                    self.praterich_panel.start_typing_effect("I'm afraid that tab number is out of range.")
            except (ValueError, IndexError):
                self.praterich_panel.start_typing_effect("Please provide a valid tab number or name.")
        elif command == "RESIZE_WINDOW":
            self.praterich_panel.start_typing_effect("I can't resize the window automatically just yet. You may do so by dragging the edges.")
        elif command == "NEW_CHAT":
            self.praterich_panel.clear_chat()
        elif command == "CRAWL_SITE":
            def handle_html(html_content):
                prompt = f"Oodles has crawled the following HTML from {query}. Please summarize what you see, and describe the website's purpose. The HTML is:\n\n{html_content[:5000]}..."
                response = get_praterich_response_text(prompt)
                self.praterich_panel.start_typing_effect(response)
            
            self.tabs.currentWidget().page().toHtml(handle_html)
        elif command == "TAB_FORMAT_VERTICAL":
            self.tabs.setTabPosition(QTabWidget.TabPosition.West)
            self.tabs.setDocumentMode(True)
            self.tabs.setMovable(True)
        elif command == "TAB_FORMAT_HORIZONTAL_MULTIROWE":
            self.tabs.setTabPosition(QTabWidget.TabPosition.North)
            self.tabs.setDocumentMode(False)
            self.tabs.setMovable(True)
        elif command == "OPEN_NOTES":
            self.notes_dialog.show()
        elif command == "PROMPT_DISPLAY":
            self.praterich_panel.start_typing_effect(query)

    def open_terminal(self):
        try:
            if sys.platform == "win32":
                subprocess.Popen(["start", "cmd"], shell=True)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", "-a", "Terminal"])
            else:
                subprocess.Popen(["x-terminal-emulator"])
        except FileNotFoundError:
            self.status_bar.showMessage("Error: Terminal application not found.")
            
    def load_custom_font(self):
        font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Roboto.ttf")
        
        if not os.path.exists(font_path):
            print(f"Error: Font file not found at path: {font_path}")
            return
            
        font_id = QFontDatabase.addApplicationFont(font_path)
        
        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            print(f"Font '{font_family}' loaded successfully.")
            self.setStyleSheet(f"""
                * {{
                    font-family: '{font_family}';
                }}
            """)
        else:
            print(f"Error: Failed to load font from path: {font_path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    QApplication.setApplicationName("Ringzauber")
    window = PraterichBrowser()
    window.show()
    sys.exit(app.exec())