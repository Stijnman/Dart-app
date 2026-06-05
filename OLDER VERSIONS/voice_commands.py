"""
core/voice_commands.py
Voice Commands System for Dart Game Pro

Supports voice input for game control and scoring.
Works alongside the existing voice_scorer.py
"""

from typing import Optional, Dict
import re

class VoiceCommandParser:
    """Parses voice commands for game control and scoring."""

    # Common scoring patterns
    SCORE_PATTERNS = [
        r'^(?P<multiplier>[STD])?(?P<number>\d{1,2})$',           # T20, D16, 15
        r'^(?P<number>\d{1,3})$',                                # 60, 180
        r'^(?P<multiplier>double|triple)\s+(?P<number>\d{1,2})$', # double 20
        r'^bull(?:seye)?$',                                       # Bull / Bullseye
        r'^miss$',                                                # Miss
    ]

    # Game control commands
    CONTROL_COMMANDS = {
        "undo": ["undo", "undo last", "back"],
        "redo": ["redo", "forward"],
        "next": ["next player", "next", "switch"],
        "skip": ["skip turn", "pass"],
        "save": ["save game", "save"],
        "stats": ["show stats", "stats"],
        "exit": ["exit", "quit", "end game"],
    }

    def parse(self, text: str) -> Dict:
        """Parse voice input into structured command or score."""
        text = text.lower().strip()

        # Check for control commands first
        for command, phrases in self.CONTROL_COMMANDS.items():
            if any(phrase in text for phrase in phrases):
                return {"type": "control", "command": command, "raw": text}

        # Try to parse as a score
        for pattern in self.SCORE_PATTERNS:
            match = re.match(pattern, text)
            if match:
                return self._parse_score_match(match, text)

        return {"type": "unknown", "raw": text}

    def _parse_score_match(self, match, original_text: str) -> Dict:
        groups = match.groupdict()

        if 'multiplier' in groups and groups['multiplier']:
            multiplier = groups['multiplier'].upper()
            if multiplier in ['D', 'DOUBLE']:
                multiplier = 'D'
            elif multiplier in ['T', 'TRIPLE']:
                multiplier = 'T'
            else:
                multiplier = 'S'
        else:
            multiplier = 'S'

        if groups.get('number'):
            number = int(groups['number'])
        elif 'bull' in original_text:
            number = 50 if 'eye' in original_text else 25
            multiplier = 'S'
        else:
            number = 0

        # Convert to actual score
        if multiplier == 'D':
            score = number * 2
        elif multiplier == 'T':
            score = number * 3
        else:
            score = number

        return {
            "type": "score",
            "score": score,
            "multiplier": multiplier,
            "number": number,
            "raw": original_text
        }


def get_voice_command_help() -> str:
    """Returns help text for voice commands."""
    return """
Voice Commands:
- Scoring: 'T20', 'D16', '180', 'bull', 'miss'
- Control: 'undo', 'next player', 'skip turn', 'show stats', 'save game'
""".strip()
