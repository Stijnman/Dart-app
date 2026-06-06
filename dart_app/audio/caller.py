import queue
import threading
import pyttsx3

class DartCaller:
    """
    Thread-safe, non-blocking Audio Caller using pyttsx3.
    Enables offline speech synthesis on Windows, macOS, and Linux.
    """
    def __init__(self, rate: int = 150, volume: float = 1.0):
        self.speech_queue = queue.Queue()
        self.rate = rate
        self.volume = volume
        self.worker_thread = threading.Thread(target=self._speech_loop, daemon=True)
        self.worker_thread.start()

    def _speech_loop(self):
        engine = pyttsx3.init()
        engine.setProperty('rate', self.rate)
        engine.setProperty('volume', self.volume)
        
        while True:
            text = self.speech_queue.get()
            if text is None:
                break
            try:
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                print(f"[Audio Error]: {e} | Fallback console logging: {text}")
            finally:
                self.speech_queue.task_done()

    def call_score(self, score: int):
        if score == 180:
            self.speech_queue.put("One hundred and eighty!")
        elif score == 0:
            self.speech_queue.put("No score!")
        else:
            self.speech_queue.put(str(score))

    def call_checkout(self, player_name: str):
        self.speech_queue.put(f"Game shot, and the match, to {player_name}!")

    def shutdown(self):
        self.speech_queue.put(None)
        self.worker_thread.join()
