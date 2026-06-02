"""
Dart Game Pro v2 — Constants, Checkout Tables & Game Configuration
Complete PDC-standard checkout tables and game mode definitions.
"""

from typing import Dict, List, Tuple

# =============================================================================
# PDC TOURNAMENT CHECKOUT TABLES (all finishes 2-170)
# =============================================================================

CHECKOUT_TABLE: Dict[int, List[str]] = {
    170: ["T20 T20 Bull"],
    167: ["T20 T19 Bull"],
    166: ["T20 T16 D16"],
    165: ["T20 T15 D16"],
    164: ["T20 T18 Bull"],
    163: ["T20 T17 D16"],
    162: ["T20 T16 Bull"],
    161: ["T20 T17 Bull"],
    160: ["T20 T20 D20"],
    159: ["T20 T19 D16"],
    158: ["T20 T20 D19"],
    157: ["T20 T19 D20"],
    156: ["T20 T20 D18"],
    155: ["T20 T19 D19"],
    154: ["T20 T18 D20"],
    153: ["T20 T19 D18"],
    152: ["T20 T20 D16"],
    151: ["T20 T17 D20"],
    150: ["T20 T18 D18", "Bull Bull Bull"],
    149: ["T20 T19 D16"],
    148: ["T20 T20 D14"],
    147: ["T20 T17 D18"],
    146: ["T20 T18 D16"],
    145: ["T20 T15 D20", "T20 T19 D14"],
    144: ["T20 T20 D12"],
    143: ["T20 T17 D16"],
    142: ["T20 T14 D20"],
    141: ["T20 T19 D12"],
    140: ["T20 T20 D10", "T20 T16 D16"],
    139: ["T20 T13 D20", "T19 T14 D20"],
    138: ["T20 T18 D12"],
    137: ["T20 T15 D16"],
    136: ["T20 T20 D8"],
    135: ["T20 T17 D12", "Bull T20 D20"],
    134: ["T20 T14 D16"],
    133: ["T20 T19 D8"],
    132: ["T20 T16 D12", "Bull T14 D20"],
    131: ["T20 T13 D16"],
    130: ["T20 T20 D5", "T20 T18 D8"],
    129: ["T19 T16 D12", "T20 T19 D6"],
    128: ["T20 T20 D4", "T18 T14 D16"],
    127: ["T20 T17 D8"],
    126: ["T19 T19 D6", "T20 T16 D9"],
    125: ["T20 T19 D4", "25 T20 D20"],
    124: ["T20 T16 D8"],
    123: ["T20 T13 D12", "T19 T16 D9"],
    122: ["T20 T18 D4"],
    121: ["T20 T15 D8", "T19 T16 D8"],
    120: ["T20 20 D20", "T19 T13 D12"],
    119: ["T19 T16 D7", "T20 19 Bull"],
    118: ["T20 18 Bull", "T16 T16 D9"],
    117: ["T20 17 Bull"],
    116: ["T20 16 Bull", "T20 20 D18"],
    115: ["T20 15 Bull", "T19 20 D18"],
    114: ["T20 14 Bull", "T20 18 D18"],
    113: ["T20 13 Bull", "T20 17 D18"],
    112: ["T20 12 Bull", "T20 20 D16"],
    111: ["T20 19 D16", "T19 14 Bull"],
    110: ["T20 18 D16", "T20 10 Bull", "T19 T13 D10"],
    109: ["T20 17 D16", "T19 20 D16"],
    108: ["T20 16 D16", "T19 19 D16"],
    107: ["T20 15 D16", "T19 18 D16"],
    106: ["T20 14 D16", "T19 17 D16"],
    105: ["T20 13 D16", "T19 16 D16", "T20 5 Bull"],
    104: ["T20 12 D16", "T19 15 D16", "T18 18 D16"],
    103: ["T20 11 D16", "T19 14 D16", "T17 12 Bull"],
    102: ["T20 10 D16", "T19 13 D16", "T20 14 Bull"],
    101: ["T20 9 D16", "T19 12 D16", "T17 10 Bull"],
    100: ["T20 D20", "T16 12 D20"],
    99: ["T19 10 D16", "T20 7 D16", "T19 T10 D6"],
    98: ["T20 D19", "T18 12 D16"],
    97: ["T19 D20", "T15 12 D20", "T19 T10 D5"],
    96: ["T20 D18", "T16 16 D16", "T20 6 D18"],
    95: ["T19 D19", "T15 18 D16", "T19 T10 D4"],
    94: ["T18 D20", "T16 18 D16"],
    93: ["T19 D18", "T17 16 D16"],
    92: ["T20 D16", "T16 16 D18", "T20 4 D16"],
    91: ["T17 D20", "T15 16 D20", "T17 T10 D5"],
    90: ["T20 D15", "Bull D20", "T18 12 D18"],
    89: ["T19 D16", "T13 16 D20", "T19 T10 D1"],
    88: ["T16 D20", "T20 8 D16", "T16 T16 D4"],
    87: ["T17 D18", "T15 12 D18", "T17 10 D16"],
    86: ["T18 D16", "T14 12 D20", "T18 T10 D1"],
    85: ["T15 D20", "T19 8 D16"],
    84: ["T16 D18", "T20 4 D16", "T16 T16 D2"],
    83: ["T17 D16", "T15 10 D18", "T17 8 D16"],
    82: ["T14 D20", "Bull D16", "Bull T16 D1", "T14 T14 D5"],
    81: ["T19 D12", "T15 6 D18", "T13 12 D18"],
    80: ["T20 D10", "T16 8 D16", "T12 T16 D4"],
    79: ["T19 D11", "T13 10 D18", "T15 8 D18"],
    78: ["T18 D12", "T14 4 D20", "T18 T10 D0*"],
    77: ["T15 D16", "T19 6 D12", "T17 10 D12"],
    76: ["T20 D8", "T16 12 D12", "T20 T8 D0*"],
    75: ["T15 D15", "T17 6 D15", "T13 12 D15"],
    74: ["T14 D16", "T16 10 D12", "T14 T10 D4"],
    73: ["T19 D8", "T15 8 D14", "T11 12 D16"],
    72: ["T16 D12", "T20 4 D10", "T12 T12 D6"],
    71: ["T13 D16", "T17 6 D13", "T11 10 D16"],
    70: ["T10 D20", "T18 8 D12", "T10 T10 D10"],
    69: ["T19 D6", "T15 8 D13", "T13 10 D12"],
    68: ["T20 D4", "T16 8 D12", "T12 12 D14", "T16 T8 D0*"],
    67: ["T17 D8", "T15 4 D15", "T13 8 D14"],
    66: ["T10 D18", "T16 6 D12", "T14 4 D16", "T10 T10 D8"],
    65: ["T15 D10", "T19 4 D8", "T13 6 D14"],
    64: ["T16 D8", "T14 6 D14", "T8 16 D16", "T16 T8 D0*"],
    63: ["T13 D12", "T17 4 D9", "T11 6 D15"],
    62: ["T10 D16", "T14 4 D14", "T8 14 D16"],
    61: ["T15 D8", "T11 4 D16", "T9 12 D14"],
    60: ["20 D20", "T10 D15", "T12 8 D12"],
    59: ["19 D20", "T13 4 D10", "T9 10 D13"],
    58: ["18 D20", "T10 8 D15", "T8 10 D15"],
    57: ["17 D20", "T15 4 D8", "T9 8 D14"],
    56: ["16 D20", "T8 8 D16", "T12 4 D10"],
    55: ["15 D20", "T15 2 D8", "T9 6 D14"],
    54: ["14 D20", "T10 4 D15", "Bull 4 D15"],
    53: ["13 D20", "T11 4 D10", "T7 8 D14"],
    52: ["12 D20", "T8 4 D16", "T12 2 D10"],
    51: ["11 D20", "T9 2 D12", "T7 6 D14"],
    50: ["Bull", "10 D20", "T10 D10"],
    49: ["9 D20", "T11 D8", "T7 4 D14"],
    48: ["16 D16", "8 D20", "T8 D12", "T16 D0*"],
    47: ["15 D16", "7 D20", "T9 D10", "T11 4 D7"],
    46: ["10 D18", "6 D20", "T6 D14", "T14 D2"],
    45: ["13 D16", "5 D20", "T15 D0*", "T11 2 D7"],
    44: ["12 D16", "4 D20", "T4 D16"],
    43: ["11 D16", "3 D20", "T9 D8", "T11 D5"],
    42: ["10 D16", "2 D20", "T6 D12", "T10 D6"],
    41: ["9 D16", "1 D20", "T7 D10", "T5 D13"],
    40: ["D20", "8 D16", "T4 D14"],
    39: ["7 D16", "11 D14", "T9 D6"],
    38: ["D19", "6 D16", "T4 D13"],
    37: ["5 D16", "9 D14", "T7 D8"],
    36: ["D18", "4 D16", "T6 D9"],
    35: ["3 D16", "7 D14", "T5 D10"],
    34: ["D17", "2 D16", "T6 D8"],
    33: ["1 D16", "5 D14", "T11 D0*"],
    32: ["D16", "8 D12", "T4 D10"],
    31: ["15 D8", "3 D14", "T5 D8"],
    30: ["D15", "10 D10", "T6 D6"],
    29: ["13 D8", "5 D12", "T9 D1"],
    28: ["D14", "4 D12", "T4 D8"],
    27: ["11 D8", "3 D12", "T9 D0*"],
    26: ["D13", "2 D12", "T6 D4"],
    25: ["9 D8", "1 D12", "T5 D5"],
    24: ["D12", "8 D8", "T4 D6"],
    23: ["7 D8", "3 D10", "T7 D1"],
    22: ["D11", "6 D8", "T2 D8"],
    21: ["5 D8", "1 D10", "T7 D0*"],
    20: ["D10", "4 D8", "T4 D4"],
    19: ["3 D8", "7 D6", "T3 D5"],
    18: ["D9", "2 D8", "T6 D0*"],
    17: ["1 D8", "5 D6", "T3 D4"],
    16: ["D8", "4 D6", "T2 D5"],
    15: ["7 D4", "3 D6", "T5 D0*"],
    14: ["D7", "2 D6", "T2 D4"],
    13: ["5 D4", "1 D6", "T3 D2"],
    12: ["D6", "4 D4", "T4 D0*"],
    11: ["3 D4", "1 D5", "T1 D4"],
    10: ["D5", "2 D4"],
    9:  ["1 D4", "5 D2", "T3 D0*"],
    8:  ["D4", "4 D2", "T2 D1"],
    7:  ["3 D2", "1 D3", "T1 D2"],
    6:  ["D3", "2 D2"],
    5:  ["1 D2"],
    4:  ["D2"],
    3:  ["1 D1"],
    2:  ["D1"],
}

# No-checkout scores (requires setup shot)
NO_CHECKOUT_RANGE = set(range(159, 171))  # Only 160, 161, 164, 167, 170 are checkable

# =============================================================================
# GAME MODE DEFINITIONS
# =============================================================================

X01_STARTING_SCORES = [101, 170, 201, 210, 301, 501, 701, 901, 1001, 1501]

X01_MODES = {
    "101": {"start": 101, "description": "Quick finish game"},
    "170": {"start": 170, "description": "170 challenge"},
    "201": {"start": 201, "description": "Short format"},
    "210": {"start": 210, "description": "210 challenge"},
    "301": {"start": 301, "description": "Standard short form"},
    "501": {"start": 501, "description": "The classic"},
    "701": {"start": 701, "description": "Tournament format"},
    "901": {"start": 901, "description": "Extended format"},
    "1001": {"start": 1001, "description": "Marathon format"},
    "1501": {"start": 1501, "description": "Epic marathon"},
}

CRICKET_VARIANTS = {
    "standard": {
        "name": "Standard Cricket",
        "targets": [15, 16, 17, 18, 19, 20, 25],
        "scoring": "open",
        "cutthroat": False,
    },
    "cut_throat": {
        "name": "Cut-Throat Cricket",
        "targets": [15, 16, 17, 18, 19, 20, 25],
        "scoring": "open",
        "cutthroat": True,  # Points go to other players
    },
    "no_score": {
        "name": "No-Score Cricket",
        "targets": [15, 16, 17, 18, 19, 20, 25],
        "scoring": "marks_only",  # No points, first to close all wins
        "cutthroat": False,
    },
}

# =============================================================================
# PRACTICE GAME CONFIGS
# =============================================================================

BOBS_27_CONFIG = {
    "start_score": 27,
    "targets": list(range(1, 21)) + [25],  # D1 through D20 + D(Bull)
    "points_per_hit": {"single": 0, "double": 1, "triple": 0},  # Only doubles count
    "hit_value": "double_value",  # Score = number on board for double
    "lives_system": True,
    "easy_mode_max_lives": float('inf'),  # No elimination
    "hard_mode_max_lives": 0,  # One miss = out
}

AROUND_THE_CLOCK_CONFIG = {
    "classic_targets": list(range(1, 21)) + [25],  # 1-20 then Bull
    "double_variants": {
        "singles": {"name": "Singles", "required_hits": "single"},
        "doubles": {"name": "Doubles Only", "required_hits": "double"},
        "triples": {"name": "Triples Only", "required_hits": "triple"},
    },
    "description": "Hit each number in sequence 1-20, then Bull",
}

SHANGHAI_CONFIG = {
    "rounds": list(range(1, 8)),  # 7 rounds (numbers 1-7) or full 1-20
    "sh_bonus": True,  # S+H (single+double+triple of round number) = instant win
    "sh_score": "round_number",  # Score = round number for any hit
}

# =============================================================================
# PARTY GAME CONFIGS
# =============================================================================

KILLER_CONFIG = {
    "default_lives": 3,
    "lives_range": (1, 9),
    "kill_zone": "claim_number",  # Each player claims a number, hit it to kill others
}

HALF_IT_CONFIG = {
    "default_targets": ["15", "16", "D", "17", "18", "T", "19", "20", "Bull"],
    "halve_on_miss": True,
    "max_rounds": 9,
}

# =============================================================================
# DARTBOT DIFFICULTY LEVELS
# =============================================================================

DARTBOT_LEVELS = {
    1: {"name": "Beginner", "avg_throw": 18, "checkout_pct": 0.05, "triple_pct": 0.03, "double_pct": 0.15, "description": "Just started playing"},
    2: {"name": "Casual", "avg_throw": 26, "checkout_pct": 0.12, "triple_pct": 0.06, "double_pct": 0.25, "description": "Plays occasionally"},
    3: {"name": "Pub Player", "avg_throw": 32, "checkout_pct": 0.20, "triple_pct": 0.10, "double_pct": 0.35, "description": "Regular pub player"},
    4: {"name": "League Player", "avg_throw": 38, "checkout_pct": 0.30, "triple_pct": 0.15, "double_pct": 0.45, "description": "Local league standard"},
    5: {"name": "Good League", "avg_throw": 42, "checkout_pct": 0.38, "triple_pct": 0.18, "double_pct": 0.50, "description": "Top of local league"},
    6: {"name": "County Player", "avg_throw": 45, "checkout_pct": 0.45, "triple_pct": 0.22, "double_pct": 0.55, "description": "County/regional level"},
    7: {"name": "Advanced", "avg_throw": 48, "checkout_pct": 0.52, "triple_pct": 0.26, "double_pct": 0.60, "description": "Highly skilled amateur"},
    8: {"name": "Semi-Pro", "avg_throw": 52, "checkout_pct": 0.60, "triple_pct": 0.30, "double_pct": 0.65, "description": "Near professional"},
    9: {"name": "Tour Card", "avg_throw": 56, "checkout_pct": 0.68, "triple_pct": 0.35, "double_pct": 0.72, "description": "PDC Tour Card holder"},
    10: {"name": "World Class", "avg_throw": 60, "checkout_pct": 0.78, "triple_pct": 0.40, "double_pct": 0.78, "description": "Elite professional"},
    11: {"name": "GOAT", "avg_throw": 65, "checkout_pct": 0.88, "triple_pct": 0.48, "double_pct": 0.85, "description": "Best in the world"},
    12: {"name": "Lukeman", "avg_throw": 70, "checkout_pct": 0.95, "triple_pct": 0.55, "double_pct": 0.92, "description": "Machine-like precision"},
}

# =============================================================================
# BOARD SEGMENTS
# =============================================================================

BOARD_SEGMENTS = list(range(1, 21))  # 1-20
BOARD_DOUBLES = [f"D{s}" for s in BOARD_SEGMENTS] + ["D25"]
BOARD_TRIPLES = [f"T{s}" for s in BOARD_SEGMENTS]
BOARD_SINGLES = [str(s) for s in BOARD_SEGMENTS] + ["25", "Bull"]
BOARD_ALL = BOARD_SINGLES + BOARD_DOUBLES + BOARD_TRIPLES

SEGMENT_VALUES = {
    1: 1, 2: 2, 3: 3, 4: 4, 5: 5,
    6: 6, 7: 7, 8: 8, 9: 9, 10: 10,
    11: 11, 12: 12, 13: 13, 14: 14, 15: 15,
    16: 16, 17: 17, 18: 18, 19: 19, 20: 20,
    25: 25,
}

# =============================================================================
# QUICK SCORE BUTTONS (common scores for fast entry)
# =============================================================================

QUICK_SCORES = [0, 26, 41, 45, 60, 81, 85, 100, 125, 140, 180]
QUICK_CHECKOUTS = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 24, 28, 32, 36, 40, 50]

# =============================================================================
# STAT CATEGORIES
# =============================================================================

STAT_METRICS = [
    "games_played", "games_won", "games_lost",
    "legs_played", "legs_won", "legs_lost",
    "total_throws", "total_score",
    "three_dart_avg", "first_nine_avg",
    "checkout_pct", "doubles_pct",
    "highest_checkout", "highest_throw",
    "ton_eighties", "ton_forties", "hundreds", "eighties", "sixties",
    "best_leg_darts", "worst_leg_darts",
    "current_streak", "best_streak",
]
