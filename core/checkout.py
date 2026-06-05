"""
Comprehensive checkout system with full PDC tournament tables.
Refactored: Fixed Bull mapping (50 in checkout context), cleaned invalid entries.
"""

from typing import List, Optional, Tuple
from .constants import CHECKOUT_TABLE, MAX_CHECKOUT_SCORE


def get_checkout(remaining: int) -> List[str]:
    """Get checkout suggestion(s) for a given remaining score."""
    if remaining <= 0 or remaining > MAX_CHECKOUT_SCORE:
        return []
    return CHECKOUT_TABLE.get(remaining, [])


def get_best_checkout(remaining: int) -> Optional[str]:
    """Get the primary (best) checkout path for a score."""
    checkouts = get_checkout(remaining)
    return checkouts[0] if checkouts else None


def parse_checkout_path(path: str) -> List[Tuple[str, int]]:
    """
    Parse a checkout path string into segments.

    In checkout context:
    - "Bull" = inner bull (50 points)
    - "Bullseye" = also inner bull (50 points)
    - "25" = outer bull (25 points)

    Examples:
        'T20 T20 D20' -> [('T', 20), ('T', 20), ('D', 20)]
        'T20 T20 Bull' -> [('T', 20), ('T', 20), ('B', 25)]  # Bull = 50 pts
    """
    segments = []
    for part in path.split():
        part = part.strip()
        if not part:
            continue
        lower = part.lower()
        if lower == "bull":
            segments.append(("B", 25))  # Inner bull = 50 pts (25 * 2)
        elif lower == "bullseye":
            segments.append(("B", 25))  # Same as Bull
        elif part.startswith("T"):
            try:
                val = int(part[1:])
                if 1 <= val <= 20:
                    segments.append(("T", val))
            except ValueError:
                continue
        elif part.startswith("D"):
            try:
                val = int(part[1:])
                if 1 <= val <= 20 or val == 25:
                    segments.append(("D", val))
            except ValueError:
                continue
        else:
            try:
                val = int(part)
                if 1 <= val <= 20 or val == 25:
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
            remaining_score += 50  # Bull = 50 in checkout context
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


def filter_checkouts_by_out_rule(remaining: int, out_rule: str) -> List[str]:
    """
    Filter checkout suggestions based on the out rule.

    Args:
        remaining: Score remaining
        out_rule: 'straight', 'double', or 'master'

    Returns:
        Filtered list of checkout paths
    """
    checkouts = get_checkout(remaining)
    if not checkouts:
        return []

    if out_rule == "straight":
        return checkouts

    filtered = []
    for path in checkouts:
        segments = parse_checkout_path(path)
        if not segments:
            continue
        last_mult, last_val = segments[-1]

        if out_rule == "double":
            # Must finish on double (D) or bull (B)
            if last_mult in ("D", "B"):
                filtered.append(path)
        elif out_rule == "master":
            # Must finish on double (D), triple (T), or bull (B)
            if last_mult in ("D", "T", "B"):
                filtered.append(path)

    return filtered if filtered else checkouts


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
