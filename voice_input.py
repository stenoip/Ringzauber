import speech_recognition as sr
from PyQt6.QtCore import QThread, pyqtSignal

class VoiceRecognitionThread(QThread):
    # This signal will carry the transcribed text or an error message.
    finished = pyqtSignal(str) 

    def __init__(self, parent=None):
        super().__init__(parent)
        self.recognizer = sr.Recognizer()

    def run(self):
        """
        Listens to the microphone and transcribes the speech.
        """
        try:
            with sr.Microphone() as source:
                print("Listening...")
                # Adjust for ambient noise before listening.
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=5)
                text = self.recognizer.recognize_google(audio)
                self.finished.emit(text)
        except sr.UnknownValueError:
            self.finished.emit("Could not understand audio")
        except sr.RequestError as e:
            self.finished.emit(f"Speech recognition error: {e}")
        except Exception as e:
            self.finished.emit(f"An unexpected error occurred: {e}")