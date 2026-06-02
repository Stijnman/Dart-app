"""
Comprehensive checkout system with full PDC tournament tables.
"""

from typing import List, Optional, Tuple
from .constants import CHECKOUT_TABLE


def get_checkout(remaining: int) -> List[str]:
    """Get checkout suggestion(s) for a given remaining score."""
    if remaining <= 0 or remaining > 170:
        return []
    return CHECKOUT_TABLE.get(remaining, [])


def get_best_checkout(remaining: int) -> Optional[str]:
    """Get the primary (best) checkout path for a score."""
    checkouts = get_checkout(remaining)
    return checkouts[0] if checkouts else None


def parse_checkout_path(path: str) -> List[Tuple[str, int]]:
    """
    Parse a checkout path string into segments.
    e.g., 'T20 T20 D20' -> [('T', 20), ('T', 20), ('D', 20)]
    e.g., 'Bull' -> [('B', 25)]
    """
    segments = []
    for part in path.split():
        part = part.strip()
        if not part:
            continue
        if part.lower() == "bull":
            segments.append(("B", 25))
        elif part.lower() == "bullseye":
            segments.append(("B", 50))
        elif part.startswith("T"):
            try:
                val = int(part[1:])
                segments.append(("T", val))
            except ValueError:
                continue
        elif part.startswith("D"):
            try:
                val = int(part[1:])
                segments.append(("D", val))
            except ValueError:
                continue
        else:
            try:
                val = int(part)
                segments.append(("S", val))
            except ValueError:
                continue
    return segments


def get_checkout_score_for_dart(segments: List[Tuple[str, int]], dart_idx: int) -> int:
    """Get the score needed after N darts in a checkout path."""
    if dart_idx >= len(segments):
        return 0
    remaining_score = 0
    for i in range(dart_idx, len(segments)):
        mult, val = segments[i]
        if mult == "T":
            remaining_score += val * 3
        elif mult == "D":
            remaining_score += val * 2
        elif mult == "B":
            remaining_score += val
        else:
            remaining_score += val
    return remaining_score


def is_checkable_score(remaining: int) -> bool:
    """Check if a score can be checked out in 3 darts or fewer."""
    return remaining in CHECKOUT_TABLE


def get_first_dart_suggestion(remaining: int) -> Optional[str]:
    """Get the suggested first dart for a checkout."""
    checkout = get_best_checkout(remaining)
    if not checkout:
        return None
    segments = parse_checkout_path(checkout)
    if not segments:
        return None
    mult, val = segments[0]
    if mult == "T":
        return f"T{val}"
    elif mult == "D":
        return f"D{val}"
    elif mult == "B":
        return "Bull"
    else:
        return str(val)


def get_two_dart_checkouts() -> dict:
    """Get all two-dart checkout options (for practicing doubles)."""
    two_dart = {}
    for score, paths in CHECKOUT_TABLE.items():
        for path in paths:
            segments = parse_checkout_path(path)
            if len(segments) == 2:
                two_dart[score] = path
                break
    return two_dart


def get_three_dart_checkouts() -> dict:
    """Get all three-dart checkout options."""
    three_dart = {}
    for score, paths in CHECKOUT_TABLE.items():
        for path in paths:
            segments = parse_checkout_path(path)
            if len(segments) == 3:
                three_dart[score] = path
                break
    return three_dart


# Common checkout milestones for UI highlighting
CHECKOUT_MILESTONES = {
    170: "Maximum checkout",
    167: "",
    164: "",
    161: "",
    160: "",
    136: "",
    121: "",
    100: "Ton checkout",
    50: "Bull checkout",
    40: "D20",
    32: "D16",
    24: "D12",
    16: "D8",
    8: "D4",
}
