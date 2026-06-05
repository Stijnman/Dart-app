"""
dart_app/audio/caller.py
Non-blocking, multi-threaded offline audio caller for real-time dart score callouts.
Uses pyttsx3 (TTS) in a dedicated worker thread + queue.
Safe to call from Streamlit main thread, game loops, etc. without blocking UI or throw recording.

Usage:
    from dart_app.audio.caller import AudioCaller
    caller = AudioCaller(rate=180, volume=0.9)
    caller.announce_score("Alice", 60, 180)   # non-blocking
    caller.announce_checkout("Alice", 120)
    # ... later
    caller.shutdown()
"""

import queue
import threading
import time
from typing import Optional

try:
    import pyttsx3
    HAS_PYTTSX3 = True
except ImportError:
    HAS_PYTTSX3 = False

class AudioCaller:
    """Background TTS queue for non-blocking speech callouts."""

    def __init__(self, rate: int = 175, volume: float = 0.85, voice_id: Optional[str] = None):
        self.rate = rate
        self.volume = max(0.0, min(1.0, volume))
        self.voice_id = voice_id
        self._q: "queue.Queue[str]" = queue.Queue(maxsize=32)
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self._engine = None
        self._init_engine()
        self._start_worker()

    def _init_engine(self):
        if not HAS_PYTTSX3:
            return
        try:
            self._engine = pyttsx3.init()
            self._engine.setProperty('rate', self.rate)
            self._engine.setProperty('volume', self.volume)
            if self.voice_id:
                self._engine.setProperty('voice', self.voice_id)
            # Best-effort: pick a decent English voice if none specified
            if not self.voice_id:
                voices = self._engine.getProperty('voices') or []
                for v in voices:
                    if 'en' in (v.id or '').lower() or 'english' in (v.name or '').lower():
                        self._engine.setProperty('voice', v.id)
                        break
        except Exception:
            self._engine = None  # will fallback to print

    def _start_worker(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._worker_loop, name="AudioCallerWorker", daemon=True)
        self._thread.start()

    def _worker_loop(self):
        while not self._stop.is_set():
            try:
                text = self._q.get(timeout=0.5)
                if text is None:
                    self._q.task_done()
                    break
                self._speak_blocking(text)
                self._q.task_done()
            except queue.Empty:
                continue
            except Exception:
                # Never let worker die on one bad utterance
                time.sleep(0.1)

    def _speak_blocking(self, text: str):
        if not text or not text.strip():
            return
        if self._engine is not None:
            try:
                self._engine.say(text.strip())
                self._engine.runAndWait()
                return
            except Exception:
                pass  # fall through to fallback
        # Fallback (visible in logs / for headless)
        print(f"[AUDIO CALLER] {text}")

    # Public non-blocking API
    def call(self, text: str):
        """Queue text for speech. Never blocks caller."""
        if not text:
            return
        try:
            self._q.put_nowait(text.strip())
        except queue.Full:
            # Drop oldest if saturated (prefer latest callouts)
            try:
                self._q.get_nowait()
            except queue.Empty:
                pass
            try:
                self._q.put_nowait(text.strip())
            except queue.Full:
                pass

    def announce_score(self, player: str, score: int, total: Optional[int] = None):
        if total is not None:
            self.call(f"{player} scores {score}. Total {total}.")
        else:
            self.call(f"{player} scores {score}.")

    def announce_checkout(self, player: str, checkout: int):
        self.call(f"{player} checks out on {checkout}!")

    def announce_winner(self, player: str):
        self.call(f"{player} wins the leg!")

    def announce_target(self, target: str):
        self.call(f"Target: {target}")

    def shutdown(self, timeout: float = 2.0):
        """Stop worker cleanly."""
        self._stop.set()
        try:
            self._q.put_nowait(None)  # sentinel
        except Exception:
            pass
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=timeout)
        if self._engine is not None:
            try:
                self._engine.stop()
            except Exception:
                pass
        self._engine = None

    def __del__(self):
        try:
            self.shutdown()
        except Exception:
            pass

# Convenience singleton for simple use
_default_caller: Optional[AudioCaller] = None

def get_default_caller() -> AudioCaller:
    global _default_caller
    if _default_caller is None:
        _default_caller = AudioCaller()
    return _default_caller

if __name__ == "__main__":
    caller = AudioCaller()
    caller.announce_score("Alice", 81, 180)
    caller.announce_checkout("Bob", 32)
    time.sleep(3)
    caller.shutdown()
