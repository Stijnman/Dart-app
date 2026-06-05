"""
core/themes.py
Dartboard Theme System for Dart Game Pro v2.4+

Provides multiple visual themes for the Streamlit UI.
Users can switch themes dynamically for better experience.
"""

from typing import Dict, List

THEMES: Dict[str, Dict] = {
    "classic": {
        "name": "Classic Dark",
        "primary": "#1a1a2e",
        "accent": "#e94560",
        "background": "#0f0f23",
        "board_bg": "#f5f5f5",
        "text": "#ffffff",
        "description": "Traditional professional look"
    },
    "neon": {
        "name": "Neon Nights",
        "primary": "#0f0f23",
        "accent": "#00f5ff",
        "background": "#1a0033",
        "board_bg": "#0d001a",
        "text": "#ffffff",
        "description": "Vibrant cyberpunk style"
    },
    "retro": {
        "name": "Retro Arcade",
        "primary": "#2d132c",
        "accent": "#ffcc00",
        "background": "#1a0a00",
        "board_bg": "#fff8e7",
        "text": "#ffffff",
        "description": "80s arcade vibes"
    },
    "minimal": {
        "name": "Minimal Clean",
        "primary": "#111111",
        "accent": "#00cc66",
        "background": "#fafafa",
        "board_bg": "#ffffff",
        "text": "#111111",
        "description": "Clean and modern"
    },
    "dark_pro": {
        "name": "Dark Pro",
        "primary": "#0d0d0d",
        "accent": "#ff4d4d",
        "background": "#1f1f1f",
        "board_bg": "#2a2a2a",
        "text": "#eeeeee",
        "description": "Serious competitive mode"
    }
}


def get_theme(theme_key: str = "classic") -> Dict:
    """Return theme configuration by key."""
    return THEMES.get(theme_key, THEMES["classic"])


def get_all_themes() -> List[str]:
    """Return list of available theme keys."""
    return list(THEMES.keys())


def get_theme_names() -> Dict[str, str]:
    """Return mapping of key -> display name."""
    return {key: theme["name"] for key, theme in THEMES.items()}
