import json
import os
import random
from dataclasses import dataclass, field, asdict
from typing import List, Optional

"""
Dart Game Pro v3.0 — Custom Game Mode System
Sublime wizard with Surprise Me, preview cards, 15+ polish (stats, export, edit, etc.).
"""

SAVE_PATH = "data/custom_modes.json"


@dataclass
class CustomGameMode:
    name: str
    starting_score: int
    win_condition: str
    special_rules: List[str] = field(default_factory=list)
    lives: Optional[int] = None
    round_limit: Optional[int] = None
    scoring_multiplier: float = 1.0
    allowed_targets: Optional[List[int]] = None
    emoji: str = "🎯"
    description: str = ""
    tags: List[str] = field(default_factory=list)
    estimated_minutes: int = 10
    play_count: int = 0
    best_score: Optional[int] = None
    last_played: Optional[str] = None

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        # backward compat for old saves
        import dataclasses
        for f in dataclasses.fields(cls):
            if f.name not in data:
                if f.default is not dataclasses.MISSING:
                    data[f.name] = f.default
                elif f.default_factory is not dataclasses.MISSING:
                    data[f.name] = f.default_factory()
        return cls(**data)


def generate_name_suggestions(style: str, difficulty: str) -> List[str]:
    """Generate 5 wack, funny, high-impact name suggestions."""
    base = {
        "Scoring Race": [
            "Scorepocalypse", "Point Pandemonium", "Dart Dash Deluxe", "High Score Heist",
            "The Great Point Grab", "Scoregasm 3000"
        ],
        "Target Hunting": [
            "Bullseye Bloodbath", "Segment Slayer 9000", "Target Tyrant", "Number Ninja Nightmare",
            "The Hunt for Red October (Darts)", "Dartboard Dominator"
        ],
        "Survival": [
            "Last Dart on Earth", "Lives? What Lives?", "Sudden Death by Chocolate", "One Dart Left Standing",
            "Darts Don't Die, Players Do", "Heart Attack Darts"
        ],
        "Chaos Mode": [
            "Total Dart Chaos", "Madhouse Mayhem", "Anarchy Arrows", "Random Acts of Darts",
            "Darts Gone Wild", "The Chaos Theory of Scoring"
        ]
    }
    
    names = base.get(style, ["Mystery Dart Mayhem"])
    prefixes = {
        "Easy": ["Chill", "Casual", "Vibe", "Chillax"],
        "Normal": ["Classic", "Solid", "Respectable"],
        "Hard": ["Brutal", "Ruthless", "Savage", "No Mercy"],
        "Brutal": ["Insane", "Psycho", "Apocalyptic", "God Mode"]
    }
    prefix = random.choice(prefixes.get(difficulty, ["Wack"]))
    
    suggestions = []
    for n in random.sample(names, min(4, len(names))):
        full = f"{prefix} {n}".strip()
        suggestions.append(full)
    
    # extra wacky ones
    wack = [
        f"{random.choice(['Neon', 'Shadow', 'Turbo', 'Quantum', 'Disco', 'Ninja'])} {style} {random.choice(['Edition', 'Revenge', 'Reloaded', 'Unleashed'])}",
        f"The {random.choice(['Forbidden', 'Legendary', 'Cursed', 'Mythic'])} {style}",
        f"{difficulty} {style} but Make it {random.choice(['Fashion', 'Spicy', 'Extra', 'Meme'])}"
    ]
    suggestions.extend(random.sample(wack, 1))
    return suggestions[:5]


def generate_custom_game_mode(answers: dict) -> CustomGameMode:
    style = answers.get("style", "Scoring Race")
    starting_score = answers.get("starting_score", 501)
    difficulty = answers.get("difficulty", "Normal")
    special = answers.get("special_rules", [])

    win_condition = "First to finish"
    lives = None
    round_limit = None
    multiplier = 1.0
    rules = []

    if style == "Scoring Race":
        win_condition = "Highest score after rounds"
        round_limit = random.choice([5, 7, 10])
    elif style == "Target Hunting":
        win_condition = "Hit all required targets"
    elif style == "Survival":
        win_condition = "Last player with lives remaining"
        lives = random.choice([3, 5])
    elif style == "Chaos Mode":
        multiplier = random.choice([0.7, 1.5, 2.0])

    # Expanded special rules (easy high-impact addition)
    special_pool = {
        "Only Doubles": ("Only doubles score points", 1.2),
        "Bust = Lose Life": ("Busting costs 1 life", 0.9),
        "Must hit bull to win": ("Must checkout on Bull", 1.1),
        "Triple points only": ("Only triples count", 1.3),
        "No 180s allowed": ("180s are banned (sad)", 0.8),
        "Reverse scoring (lowest wins)": ("Lowest final score wins", 0.7),
        "Sudden death on any checkout": ("First checkout wins instantly", 1.4),
        "All scores doubled after round 3": ("Late game 2x points", 1.0),
    }

    for rule in special:
        if rule in special_pool:
            desc, mult = special_pool[rule]
            rules.append(desc)
            multiplier *= mult

    if difficulty == "Hard":
        multiplier *= 1.2
    elif difficulty == "Brutal":
        multiplier *= 1.5

    # Emoji + flavor + tags + estimate (high impact polish)
    emoji_map = {
        "Scoring Race": "🏃‍♂️💨",
        "Target Hunting": "🎯🔍",
        "Survival": "💀🩸",
        "Chaos Mode": "🌪️🤪"
    }
    emoji = emoji_map.get(style, "🎲🔥")

    flavor = {
        "Easy": "relaxed vibes",
        "Normal": "solid challenge",
        "Hard": "brutal test of skill",
        "Brutal": "absolute chaos and pain"
    }.get(difficulty, "")

    description = f"A {flavor} {style.lower()} experience. {win_condition}."

    tags = [style.replace(" ", "-").lower(), difficulty.lower()]
    if lives: tags.append("lives")
    if round_limit: tags.append("rounds")
    if multiplier > 1.2: tags.append("high-score")
    if any("double" in r.lower() for r in rules): tags.append("doubles-only")

    est = (round_limit or 8) * (1.2 if "Survival" in style else 1.0)
    est = max(4, min(25, int(est)))

    cm = CustomGameMode(
        name="",
        starting_score=starting_score,
        win_condition=win_condition,
        special_rules=rules,
        lives=lives,
        round_limit=round_limit,
        scoring_multiplier=round(multiplier, 2),
        emoji=emoji,
        description=description,
        tags=tags,
        estimated_minutes=est
    )
    return cm


# ==================== SAVE / LOAD ====================

def save_custom_mode(mode: CustomGameMode):
    """Upsert by name (supports edit/duplicate/save)."""
    os.makedirs("data", exist_ok=True)
    update_custom_mode(mode)


def load_all_custom_modes() -> List[dict]:
    if not os.path.exists(SAVE_PATH):
        return []
    with open(SAVE_PATH, "r") as f:
        return json.load(f)


def get_saved_modes() -> List[CustomGameMode]:
    return [CustomGameMode.from_dict(m) for m in load_all_custom_modes()]


def generate_surprise_mode() -> CustomGameMode:
    """Surprise Me! Random high-impact custom mode."""
    styles = ["Scoring Race", "Target Hunting", "Survival", "Chaos Mode"]
    diffs = ["Easy", "Normal", "Hard", "Brutal"]
    special_pool = list({
        "Only Doubles", "Bust = Lose Life", "Must hit bull to win",
        "Triple points only", "No 180s allowed", "Reverse scoring (lowest wins)",
        "Sudden death on any checkout", "All scores doubled after round 3"
    })
    answers = {
        "style": random.choice(styles),
        "starting_score": random.choice([101, 301, 501, 701, 1001]),
        "difficulty": random.choice(diffs),
        "special_rules": random.sample(special_pool, k=random.randint(0, 3))
    }
    mode = generate_custom_game_mode(answers)
    # Give it a surprise name
    mode.name = random.choice(generate_name_suggestions(answers["style"], answers["difficulty"]))
    return mode


def play_custom_mode(mode_name: str, achieved_score: Optional[int] = None):
    """Call this when a player finishes a game with this custom mode.
    Increments play count and updates best score if better."""
    modes = load_all_custom_modes()
    updated = False
    for m in modes:
        if m.get("name") == mode_name:
            m["play_count"] = m.get("play_count", 0) + 1
            if achieved_score is not None:
                if m.get("best_score") is None or achieved_score > m.get("best_score", 0):
                    m["best_score"] = achieved_score
            from datetime import datetime
            m["last_played"] = datetime.now().isoformat()
            updated = True
            break
    if updated:
        with open(SAVE_PATH, "w") as f:
            json.dump(modes, f, indent=2)


def delete_custom_mode(mode_name: str):
    """Remove a saved mode."""
    modes = [m for m in load_all_custom_modes() if m.get("name") != mode_name]
    with open(SAVE_PATH, "w") as f:
        json.dump(modes, f, indent=2)


def update_custom_mode(updated_mode: CustomGameMode):
    """Edit / duplicate support - replace by name."""
    modes = load_all_custom_modes()
    for i, m in enumerate(modes):
        if m.get("name") == updated_mode.name:
            modes[i] = updated_mode.to_dict()
            break
    else:
        modes.append(updated_mode.to_dict())
    with open(SAVE_PATH, "w") as f:
        json.dump(modes, f, indent=2)
