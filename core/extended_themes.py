
"""
Extended Theme System for Dart Game Pro v2.4
Polishes Feature #29 (Customizable Themes) and enhances #30 (Dark Mode with Eye Comfort).

Adds:
- 'holographic' theme (futuristic neon + glassmorphism approximation)
- Eye comfort options: blue_light_filter (warmer tones), brightness multiplier, oled_optimized toggle
- Easy integration with existing themes.py

Use in streamlit_app.py:
from extended_themes import get_enhanced_theme, apply_eye_comfort
theme = get_enhanced_theme(st.session_state.get('selected_theme', 'classic'), eye_comfort=True, brightness=0.9)
"""

from typing import Dict, Any

# Base themes from your existing core/themes.py (classic, neon, retro, minimal, dark_pro)
BASE_THEMES = {
    "classic": {
        "name": "Classic Dark",
        "primary": "#1a1a2e",
        "accent": "#e94560",
        "background": "#0f0f23",
        "board_bg": "#16213e",
        "text": "#eaeaea",
        "description": "Traditional professional look"
    },
    "neon": {
        "name": "Neon Nights",
        "primary": "#0f0f23",
        "accent": "#00f9ff",
        "background": "#050505",
        "board_bg": "#1a0033",
        "text": "#ffffff",
        "description": "Vibrant cyberpunk style"
    },
    "retro": {
        "name": "Retro Arcade",
        "primary": "#2d132c",
        "accent": "#ff6b6b",
        "background": "#1a0f0f",
        "board_bg": "#3d1a1a",
        "text": "#f5e8c7",
        "description": "80s arcade vibes"
    },
    "minimal": {
        "name": "Minimal Clean",
        "primary": "#1f1f1f",
        "accent": "#4ecdc4",
        "background": "#121212",
        "board_bg": "#2a2a2a",
        "text": "#f0f0f0",
        "description": "Clean and modern"
    },
    "dark_pro": {
        "name": "Dark Pro",
        "primary": "#0a0a0f",
        "accent": "#c9a227",
        "background": "#050505",
        "board_bg": "#111111",
        "text": "#e0e0e0",
        "description": "Serious competitive mode"
    }
}

def get_enhanced_theme(theme_key: str = "classic", eye_comfort: bool = False, brightness: float = 1.0, 
                       blue_light_filter: bool = False, oled_optimized: bool = True) -> Dict[str, Any]:
    """
    Returns enhanced theme config.
    Apply eye comfort transformations for late-night play (Feature #30).
    """
    base = BASE_THEMES.get(theme_key, BASE_THEMES["classic"]).copy()

    # Apply brightness
    if brightness != 1.0:
        for key in ["primary", "accent", "background", "board_bg", "text"]:
            if key in base and base[key].startswith("#"):
                base[key] = _adjust_brightness(base[key], brightness)

    if eye_comfort or blue_light_filter:
        # Soften blues, add warmth (reduce blue channel slightly, boost red/yellow)
        base = _apply_eye_comfort(base)

    if oled_optimized:
        # Pure blacks and high contrast for OLED (common in modern laptops/phones)
        base["background"] = "#000000"
        base["board_bg"] = _darken_color(base.get("board_bg", "#111111"), 0.15)
        base["text"] = "#f5f5f5"

    # New holographic theme (glass + strong neon + transparency feel)
    if theme_key == "holographic":
        base.update({
            "name": "Holographic Future",
            "primary": "#0a0a1f",
            "accent": "#7b2cbf",  # vibrant purple
            "background": "#05050f",
            "board_bg": "#1a0033",
            "text": "#e0d4ff",
            "secondary_accent": "#00f5d4",  # cyan
            "description": "Futuristic holographic / glassmorphism style (best with dark room)"
        })
        if eye_comfort:
            base = _apply_eye_comfort(base)

    base["eye_comfort_applied"] = eye_comfort or blue_light_filter
    base["brightness"] = brightness
    base["oled_optimized"] = oled_optimized
    return base

def _adjust_brightness(hex_color: str, factor: float) -> str:
    """Simple brightness adjustment for hex colors."""
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    new_rgb = tuple(max(0, min(255, int(c * factor))) for c in rgb)
    return '#{:02x}{:02x}{:02x}'.format(*new_rgb)

def _darken_color(hex_color: str, factor: float = 0.2) -> str:
    return _adjust_brightness(hex_color, 1.0 - factor)

def _apply_eye_comfort(theme: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce blue light: warm up accents and backgrounds slightly."""
    for key in ["accent", "secondary_accent"]:
        if key in theme and theme[key].startswith("#"):
            # Shift toward warmer tones (increase red, slightly decrease blue)
            theme[key] = _shift_towards_warm(theme[key])
    if "background" in theme:
        theme["background"] = _shift_towards_warm(theme["background"], strength=0.08)
    return theme

def _shift_towards_warm(hex_color: str, strength: float = 0.15) -> str:
    hex_color = hex_color.lstrip('#')
    r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    r = min(255, int(r + (255 - r) * strength * 0.6))
    b = max(0, int(b - b * strength * 0.5))
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

def get_all_enhanced_themes() -> Dict[str, str]:
    """For theme selector UI"""
    themes = {k: v["name"] for k, v in BASE_THEMES.items()}
    themes["holographic"] = "Holographic Future ✨"
    return themes

# Example UI code for streamlit_app.py settings tab:
"""
import streamlit as st
from extended_themes import get_enhanced_theme, get_all_enhanced_themes

st.subheader("🎨 Dartboard Theme & Eye Comfort")

theme_options = get_all_enhanced_themes()
selected = st.selectbox("Choose Theme", list(theme_options.keys()), 
                        format_func=lambda x: theme_options[x],
                        index=list(theme_options.keys()).index(st.session_state.get('theme', 'classic')))

col1, col2 = st.columns(2)
with col1:
    eye_comfort = st.toggle("Eye Comfort Mode (reduce blue light)", value=True)
    oled = st.toggle("OLED Optimized (pure black)", value=True)
with col2:
    brightness = st.slider("Brightness", 0.6, 1.2, 1.0, 0.05)

if st.button("Apply Theme"):
    new_theme = get_enhanced_theme(selected, eye_comfort=eye_comfort, brightness=brightness, oled_optimized=oled)
    st.session_state.theme = selected
    st.session_state.current_theme_config = new_theme
    st.success(f"Theme '{new_theme['name']}' applied with eye comfort!")
    st.rerun()

# Then use st.session_state.current_theme_config in your dartboard drawing and page styling
"""
