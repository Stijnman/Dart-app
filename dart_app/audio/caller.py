import queue
import threading
import logging

try:
    import pyttsx3
except Exception:
    pyttsx3 = None

logger = logging.getLogger("dart_app.audio.caller")

class DartCaller:
    """
    Thread-safe, non-blocking Audio Caller using pyttsx3.
    Enables offline speech synthesis on Windows, macOS, and Linux.
    """
    def __init__(self, rate: int = 150, volume: float = 1.0):
        self.speech_queue = queue.Queue()
        self.rate = rate
        self.volume = volume
        self._stop_event = threading.Event()
        self.worker_thread = threading.Thread(target=self._speech_loop, daemon=True)
        self.worker_thread.start()

    def _speech_loop(self):
        engine = None
        if pyttsx3 is not None:
            try:
                engine = pyttsx3.init()
                engine.setProperty('rate', self.rate)
                engine.setProperty('volume', self.volume)
            except Exception as e:
                logger.exception("pyttsx3 init failed, falling back to console output: %s", e)
                engine = None
        else:
            logger.warning("pyttsx3 not available; using console fallback for audio output")

        while not self._stop_event.is_set():
            text = self.speech_queue.get()
            if text is None:
                break
            try:
                if engine is not None:
                    engine.say(text)
                    engine.runAndWait()
                else:
                    logger.info("[Audio Fallback] %s", text)
            except Exception as e:
                logger.exception("[Audio Error]: %s | Fallback console logging: %s", e, text)
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

    def shutdown(self, timeout: float = 5.0):
        self._stop_event.set()
        self.speech_queue.put(None)
        self.worker_thread.join(timeout=timeout)
        if self.worker_thread.is_alive():
            logger.warning("Audio worker thread did not exit within timeout")
