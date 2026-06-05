"""
Voice-Activated Scoring System
Converts speech input directly to dart scores with high accuracy.
Supports multiple languages and dart terminology.
"""

import re
from typing import Optional, List, Dict, Tuple
from enum import Enum
from dataclasses import dataclass


class DartTerminology(Enum):
    """Dart terminology in different languages."""
    ENGLISH = "en"
    DUTCH = "nl"
    GERMAN = "de"
    FRENCH = "fr"


@dataclass
class VoiceScore:
    """Represents a parsed voice score."""
    segment: int  # 1-20 or 25 (bull)
    multiplier: int  # 1 (single), 2 (double), 3 (triple)
    score: int  # Final score value
    confidence: float  # 0.0-1.0
    raw_input: str  # Original voice input


class VoiceScorer:
    """
    Converts voice input to dart scores.
    Handles various dart terminology and natural language patterns.
    """
    
    # Terminology patterns for each language
    PATTERNS = {
        DartTerminology.ENGLISH: {
            "single": [r"\bsingle\b", r"\bone\b(?!\s*hundred)"],
            "double": [r"\bdouble\b", r"\bd\b(?!\s*\w)", r"\btwo\b"],
            "triple": [r"\btriple\b", r"\bt\b(?!\s*\w)", r"\bthree\b"],
            "bull": [r"\bbull(?:seye)?\b", r"\bouter\s+bull\b", r"\broos\b"],
            "outer_bull": [r"\bouter\s+bull\b", r"\bouter\b"],
            "bullseye": [r"\bbullseye\b", r"\binner\s+bull\b"],
            "numbers": {
                r"\bone\b": 1, r"\btwo\b": 2, r"\bthree\b": 3, r"\bfour\b": 4,
                r"\bfive\b": 5, r"\bsix\b": 6, r"\bseven\b": 7, r"\beight\b": 8,
                r"\bnine\b": 9, r"\bten\b": 10, r"\beleven\b": 11, r"\btwelve\b": 12,
                r"\bthirteen\b": 13, r"\bfourteen\b": 14, r"\bfifteen\b": 15,
                r"\bsixteen\b": 16, r"\bseventeen\b": 17, r"\beighteen\b": 18,
                r"\bnineteen\b": 19, r"\btwenty\b": 20,
            }
        },
        DartTerminology.DUTCH: {
            "single": [r"\benkel\b", r"\been\b"],
            "double": [r"\bdubbel\b", r"\bd\b", r"\btwee\b"],
            "triple": [r"\btriple\b", r"\bt\b", r"\bdrie\b"],
            "bull": [r"\bbull\b", r"\broos\b"],
            "outer_bull": [r"\buiter\s+bull\b", r"\buiter\s+roos\b"],
            "bullseye": [r"\bbullseye\b", r"\binner\s+roos\b"],
            "numbers": {
                r"\been\b": 1, r"\btwee\b": 2, r"\bdrie\b": 3, r"\bvier\b": 4,
                r"\bvijf\b": 5, r"\bzes\b": 6, r"\bzeven\b": 7, r"\bacht\b": 8,
                r"\bnegen\b": 9, r"\btien\b": 10, r"\belf\b": 11, r"\btwaalf\b": 12,
                r"\bdertien\b": 13, r"\bveertien\b": 14, r"\bvijftien\b": 15,
                r"\bzestien\b": 16, r"\bzeventien\b": 17, r"\bachttien\b": 18,
                r"\bnegentien\b": 19, r"\btwintig\b": 20,
            }
        },
        DartTerminology.GERMAN: {
            "single": [r"\beinfach\b", r"\beins\b"],
            "double": [r"\bdoppel\b", r"\bd\b", r"\bzwei\b"],
            "triple": [r"\btriple\b", r"\bt\b", r"\bdrei\b"],
            "bull": [r"\bbull\b", r"\brose\b"],
            "outer_bull": [r"\bäußer\s+bull\b"],
            "bullseye": [r"\bbullseye\b", r"\binner\s+bull\b"],
            "numbers": {
                r"\beins\b": 1, r"\bzwei\b": 2, r"\bdrei\b": 3, r"\bvier\b": 4,
                r"\bfünf\b": 5, r"\bsechs\b": 6, r"\bsieben\b": 7, r"\bacht\b": 8,
                r"\bneun\b": 9, r"\bzehn\b": 10, r"\belf\b": 11, r"\bzwölf\b": 12,
                r"\bdreizehn\b": 13, r"\bvierzehn\b": 14, r"\bfünfzehn\b": 15,
                r"\bsechzehn\b": 16, r"\bsiebzehn\b": 17, r"\bachtzehn\b": 18,
                r"\bneunzehn\b": 19, r"\bzwanzig\b": 20,
            }
        },
    }
    
    def __init__(self, language: DartTerminology = DartTerminology.ENGLISH):
        self.language = language
        self.patterns = self.PATTERNS.get(language, self.PATTERNS[DartTerminology.ENGLISH])
    
    def parse(self, voice_input: str) -> Optional[VoiceScore]:
        """
        Parse voice input into a dart score.
        
        Examples:
            "Triple twenty" -> VoiceScore(segment=20, multiplier=3, score=60)
            "Double ten" -> VoiceScore(segment=10, multiplier=2, score=20)
            "Bullseye" -> VoiceScore(segment=25, multiplier=2, score=50)
            "Single five" -> VoiceScore(segment=5, multiplier=1, score=5)
        """
        if not voice_input or not isinstance(voice_input, str):
            return None
        
        text = voice_input.lower().strip()
        
        # Check for bullseye
        if self._match_pattern(text, self.patterns.get("bullseye", [])):
            return VoiceScore(
                segment=25,
                multiplier=2,
                score=50,
                confidence=0.95,
                raw_input=voice_input
            )
        
        # Check for outer bull
        if self._match_pattern(text, self.patterns.get("outer_bull", [])):
            return VoiceScore(
                segment=25,
                multiplier=1,
                score=25,
                confidence=0.95,
                raw_input=voice_input
            )
        
        # Check for generic bull (assume bullseye)
        if self._match_pattern(text, self.patterns.get("bull", [])):
            return VoiceScore(
                segment=25,
                multiplier=2,
                score=50,
                confidence=0.85,
                raw_input=voice_input
            )
        
        # Extract multiplier
        multiplier = 1
        confidence = 0.9
        
        if self._match_pattern(text, self.patterns.get("triple", [])):
            multiplier = 3
        elif self._match_pattern(text, self.patterns.get("double", [])):
            multiplier = 2
        elif self._match_pattern(text, self.patterns.get("single", [])):
            multiplier = 1
        else:
            confidence = 0.7  # Lower confidence if multiplier not explicitly stated
        
        # Extract number
        segment = self._extract_number(text)
        
        if segment is None or segment < 1 or segment > 20:
            return None
        
        score = segment * multiplier
        
        return VoiceScore(
            segment=segment,
            multiplier=multiplier,
            score=score,
            confidence=confidence,
            raw_input=voice_input
        )
    
    def parse_multiple(self, voice_inputs: List[str]) -> List[Optional[VoiceScore]]:
        """Parse multiple voice inputs (e.g., three darts in one sentence)."""
        return [self.parse(inp) for inp in voice_inputs]
    
    def _match_pattern(self, text: str, patterns: List[str]) -> bool:
        """Check if any pattern matches the text."""
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _extract_number(self, text: str) -> Optional[int]:
        """Extract a number from the text."""
        numbers = self.patterns.get("numbers", {})
        
        for pattern, value in numbers.items():
            if re.search(pattern, text, re.IGNORECASE):
                return value
        
        return None


class VoiceScoreValidator:
    """Validates and corrects voice scores."""
    
    @staticmethod
    def validate(score: VoiceScore) -> Tuple[bool, str]:
        """
        Validate a voice score.
        
        Returns:
            (is_valid, message)
        """
        if score.score < 0 or score.score > 180:
            return False, f"Invalid score: {score.score}"
        
        if score.segment < 1 or (score.segment > 20 and score.segment != 25):
            return False, f"Invalid segment: {score.segment}"
        
        if score.multiplier not in [1, 2, 3]:
            return False, f"Invalid multiplier: {score.multiplier}"
        
        # Check if score matches segment * multiplier
        expected_score = score.segment * score.multiplier if score.segment != 25 else (25 if score.multiplier == 1 else 50)
        if score.score != expected_score:
            return False, f"Score mismatch: {score.score} != {expected_score}"
        
        return True, "Valid"
    
    @staticmethod
    def correct_common_mistakes(voice_input: str) -> str:
        """Correct common speech recognition mistakes."""
        corrections = {
            r"\bfifty\b": "bullseye",
            r"\btwenty five\b": "outer bull",
            r"\bto\b": "two",
            r"\bfor\b": "four",
            r"\bsee\b": "three",
            r"\bate\b": "eight",
            r"\bno\b": "no",  # Keep as is
        }
        
        corrected = voice_input.lower()
        for pattern, replacement in corrections.items():
            corrected = re.sub(pattern, replacement, corrected, flags=re.IGNORECASE)
        
        return corrected


class VoiceScoreHistory:
    """Maintains a history of voice scores for analysis and correction."""
    
    def __init__(self, max_history: int = 100):
        self.history: List[VoiceScore] = []
        self.max_history = max_history
    
    def add(self, score: VoiceScore) -> None:
        """Add a score to history."""
        self.history.append(score)
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    def get_recent(self, count: int = 10) -> List[VoiceScore]:
        """Get the most recent scores."""
        return self.history[-count:]
    
    def get_average_confidence(self) -> float:
        """Get average confidence of recent scores."""
        if not self.history:
            return 0.0
        return sum(s.confidence for s in self.history) / len(self.history)
    
    def get_most_common_segment(self) -> Optional[int]:
        """Get the most frequently scored segment."""
        if not self.history:
            return None
        segments = [s.segment for s in self.history]
        return max(set(segments), key=segments.count)
    
    def export_json(self) -> str:
        """Export history as JSON."""
        import json
        return json.dumps([
            {
                "segment": s.segment,
                "multiplier": s.multiplier,
                "score": s.score,
                "confidence": s.confidence,
                "raw_input": s.raw_input,
            }
            for s in self.history
        ], indent=2)
