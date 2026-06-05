"""
Shared utilities for dart game logic.
"""

from typing import Tuple, List, Optional
from .constants import VALID_DART_SCORES, ADJACENT_MAP


def parse_dart_value(dart: int) -> Tuple[int, int]:
    """
    Parse a dart score into (base_number, multiplier).

    Returns:
        (base, mult) where:
        - base is the segment number (1-20, 25)
        - mult is 1 (single), 2 (double), or 3 (triple)

    Examples:
        20 -> (20, 1)   # single 20
        40 -> (20, 2)   # double 20
        60 -> (20, 3)   # triple 20
        25 -> (25, 1)   # outer bull
        50 -> (25, 2)   # inner bull (double 25)
    """
    if dart <= 0:
        return (0, 0)
    if dart <= 20:
        return (dart, 1)
    if dart == 25:
        return (25, 1)
    if dart == 50:
        return (25, 2)
    if dart <= 40 and dart % 2 == 0:
        return (dart // 2, 2)
    if dart <= 60 and dart % 3 == 0:
        return (dart // 3, 3)
    return (0, 0)


def is_valid_dart_score(dart: int) -> bool:
    """Check if a dart score is valid."""
    return dart in VALID_DART_SCORES


def validate_dart_throw(darts: List[int]) -> Tuple[bool, Optional[str]]:
    """
    Validate a dart throw (list of 3 dart scores).

    Returns:
        (is_valid, error_message)
    """
    if len(darts) > 3:
        return (False, f"Too many darts: {len(darts)} (max 3)")

    for i, dart in enumerate(darts):
        if not is_valid_dart_score(dart):
            return (False, f"Invalid dart score at position {i+1}: {dart}")

    return (True, None)


def is_double(segment_score: int) -> bool:
    """Check if a dart score represents a double segment hit."""
    if segment_score == 50:
        return True  # Bullseye counts as double
    if segment_score <= 40 and segment_score > 0 and segment_score % 2 == 0:
        base = segment_score // 2
        if 1 <= base <= 20:
            return True
    return False


def is_triple(segment_score: int) -> bool:
    """Check if a dart score represents a triple segment hit."""
    if segment_score <= 60 and segment_score > 0 and segment_score % 3 == 0:
        base = segment_score // 3
        if 1 <= base <= 20:
            return True
    return False


def is_bull(segment_score: int) -> bool:
    """Check if a dart score is a bull hit (25 or 50)."""
    return segment_score in (25, 50)


def is_valid_finish(dart_score: int) -> bool:
    """
    Check if a dart score is a valid finishing dart (double or bull).

    In standard darts, you must finish on a double (including bull).
    """
    if dart_score == 50:
        return True  # Inner bull (double 25)
    if dart_score == 25:
        return False  # Outer bull is NOT a double
    if dart_score % 2 == 0 and 2 <= dart_score <= 40:
        return True  # Double 1-20
    return False


def get_adjacent_number(num: int) -> int:
    """Get a random adjacent number on the dartboard."""
    import random
    adj = ADJACENT_MAP.get(num, [num])
    return random.choice(adj)


def format_score_message(player_name: str, total: int, new_score: int) -> str:
    """Format a standard scoring message."""
    msg = f"{player_name}: {total} -> {new_score}"
    if total == 180:
        msg += " | ONE HUNDRED AND EIGHTY!"
    elif total >= 140:
        msg += " | TON PLUS!"
    elif total >= 100:
        msg += " | TON!"
    return msg
