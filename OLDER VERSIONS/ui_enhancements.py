"""
UI Enhancements: Dynamic Glowing, Blurring, Unlimited Players, and Visual Feedback.
"""

from typing import List, Dict, Optional, Set, Tuple
from enum import Enum
from dataclasses import dataclass


class SegmentState(Enum):
    """State of a dartboard segment for visual rendering."""
    AVAILABLE = "available"  # Can be selected
    DISABLED = "disabled"  # Cannot be selected (blurred)
    OPTIMAL = "optimal"  # Best choice (glowing)
    RECENT = "recent"  # Recently selected
    COMPLETED = "completed"  # Already finished


@dataclass
class SegmentVisual:
    """Visual properties for a dartboard segment."""
    segment: int
    state: SegmentState
    glow_intensity: float = 0.0  # 0.0-1.0
    blur_amount: float = 0.0  # 0.0-1.0
    color_override: Optional[str] = None  # e.g., "#FF0000"
    pulse_enabled: bool = False
    pulse_speed: float = 1.0  # Hz


class UIEnhancementEngine:
    """Manages dynamic UI enhancements for the dartboard."""
    
    def __init__(self):
        self.segment_states: Dict[int, SegmentState] = {}
        self.optimal_segments: Set[int] = set()
        self.disabled_segments: Set[int] = set()
        self.recent_segments: List[int] = []
        self.glow_animations: Dict[int, float] = {}
    
    def set_disabled_segments(self, segments: Set[int]) -> None:
        """Mark segments as disabled (cannot be selected)."""
        self.disabled_segments = segments
        for seg in segments:
            self.segment_states[seg] = SegmentState.DISABLED
    
    def set_optimal_segments(self, segments: Set[int], enable_glow: bool = True) -> None:
        """Mark segments as optimal (should glow/pulse)."""
        self.optimal_segments = segments
        for seg in segments:
            self.segment_states[seg] = SegmentState.OPTIMAL
            if enable_glow:
                self.glow_animations[seg] = 1.0
    
    def mark_recent_segment(self, segment: int) -> None:
        """Mark a segment as recently selected."""
        self.recent_segments.insert(0, segment)
        self.recent_segments = self.recent_segments[:5]  # Keep last 5
        self.segment_states[segment] = SegmentState.RECENT
    
    def get_segment_visual(self, segment: int) -> SegmentVisual:
        """Get visual properties for a segment."""
        state = self.segment_states.get(segment, SegmentState.AVAILABLE)
        
        visual = SegmentVisual(
            segment=segment,
            state=state,
            glow_intensity=self.glow_animations.get(segment, 0.0),
            blur_amount=1.0 if state == SegmentState.DISABLED else 0.0,
            pulse_enabled=segment in self.optimal_segments,
            pulse_speed=1.5,
        )
        
        # Color overrides based on state
        if state == SegmentState.DISABLED:
            visual.color_override = "#888888"  # Gray
        elif state == SegmentState.OPTIMAL:
            visual.color_override = "#00FF00"  # Green
        elif state == SegmentState.RECENT:
            visual.color_override = "#FFFF00"  # Yellow
        
        return visual
    
    def get_all_segment_visuals(self) -> Dict[int, SegmentVisual]:
        """Get visual properties for all segments."""
        return {seg: self.get_segment_visual(seg) for seg in range(1, 21)} | {25: self.get_segment_visual(25)}
    
    def update_glow_animation(self, delta_time: float) -> None:
        """Update glow animations (call this in render loop)."""
        import math
        for seg in self.optimal_segments:
            # Pulsating effect: sin wave between 0.3 and 1.0
            time_value = (delta_time * 2) % (2 * math.pi)
            self.glow_animations[seg] = 0.65 + 0.35 * math.sin(time_value)
    
    def get_css_for_segment(self, segment: int) -> str:
        """Generate CSS for a segment's visual state."""
        visual = self.get_segment_visual(segment)
        
        css = f"/* Segment {segment} */\n"
        
        if visual.state == SegmentState.DISABLED:
            css += f"opacity: 0.3;\n"
            css += f"filter: blur({visual.blur_amount * 5}px) grayscale(100%);\n"
        elif visual.state == SegmentState.OPTIMAL:
            css += f"box-shadow: 0 0 20px rgba(0, 255, 0, {visual.glow_intensity});\n"
            css += f"animation: pulse 1.5s infinite;\n"
        elif visual.state == SegmentState.RECENT:
            css += f"background-color: rgba(255, 255, 0, 0.3);\n"
        
        if visual.color_override:
            css += f"border-color: {visual.color_override};\n"
        
        return css


class UnlimitedPlayerManager:
    """Manages games with unlimited players."""
    
    def __init__(self):
        self.players: List[str] = []
        self.current_player_idx: int = 0
        self.scores: Dict[str, int] = {}
        self.eliminated: Set[str] = set()
    
    def add_player(self, name: str) -> None:
        """Add a player to the game."""
        if name not in self.players:
            self.players.append(name)
            self.scores[name] = 0
    
    def remove_player(self, name: str) -> None:
        """Remove a player from the game."""
        if name in self.players:
            self.players.remove(name)
            self.scores.pop(name, None)
            self.eliminated.discard(name)
    
    def eliminate_player(self, name: str) -> None:
        """Mark a player as eliminated."""
        self.eliminated.add(name)
    
    def get_active_players(self) -> List[str]:
        """Get list of active (non-eliminated) players."""
        return [p for p in self.players if p not in self.eliminated]
    
    def get_next_active_player(self) -> Optional[str]:
        """Get the next active player in turn order."""
        active = self.get_active_players()
        if not active:
            return None
        
        # Find next active player from current index
        for i in range(len(self.players)):
            idx = (self.current_player_idx + i) % len(self.players)
            if self.players[idx] in active:
                self.current_player_idx = idx
                return self.players[idx]
        
        return None
    
    def advance_turn(self) -> Optional[str]:
        """Advance to the next player's turn."""
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
        return self.get_next_active_player()
    
    def get_scoreboard(self) -> Dict:
        """Get current scoreboard."""
        active = self.get_active_players()
        return {
            "total_players": len(self.players),
            "active_players": len(active),
            "current_player": self.players[self.current_player_idx] if self.players else None,
            "standings": [
                {
                    "rank": i + 1,
                    "name": p,
                    "score": self.scores.get(p, 0),
                    "status": "eliminated" if p in self.eliminated else "active",
                }
                for i, p in enumerate(sorted(active, key=lambda x: self.scores.get(x, 0), reverse=True))
            ],
        }


class MobileRemoteUI:
    """Generates UI for mobile remote controller."""
    
    @staticmethod
    def generate_html() -> str:
        """Generate HTML for mobile remote controller."""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dart Remote Controller</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 10px;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 20px;
            max-width: 500px;
            width: 100%;
        }
        .header {
            text-align: center;
            margin-bottom: 20px;
        }
        .header h1 {
            color: #333;
            font-size: 28px;
            margin-bottom: 5px;
        }
        .header p {
            color: #666;
            font-size: 14px;
        }
        .dartboard-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
            margin-bottom: 20px;
        }
        .segment-btn {
            aspect-ratio: 1;
            border: 2px solid #667eea;
            border-radius: 10px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            background: white;
            color: #667eea;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .segment-btn:hover:not(.disabled) {
            background: #667eea;
            color: white;
            transform: scale(1.05);
        }
        .segment-btn.disabled {
            opacity: 0.3;
            cursor: not-allowed;
            background: #ccc;
        }
        .segment-btn.optimal {
            background: #00FF00;
            color: white;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.8);
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0%, 100% { box-shadow: 0 0 20px rgba(0, 255, 0, 0.8); }
            50% { box-shadow: 0 0 30px rgba(0, 255, 0, 1); }
        }
        .multiplier-row {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-bottom: 20px;
        }
        .multiplier-btn {
            padding: 15px;
            border: 2px solid #667eea;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            background: white;
            color: #667eea;
            transition: all 0.2s;
        }
        .multiplier-btn:hover {
            background: #667eea;
            color: white;
            transform: scale(1.05);
        }
        .action-row {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }
        .action-btn {
            padding: 15px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.2s;
        }
        .action-btn.undo {
            background: #FF9800;
            color: white;
        }
        .action-btn.undo:hover {
            background: #F57C00;
        }
        .action-btn.submit {
            background: #4CAF50;
            color: white;
        }
        .action-btn.submit:hover {
            background: #45a049;
        }
        .display {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 20px;
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Dart Remote</h1>
            <p>Control the game from your phone</p>
        </div>
        
        <div class="display" id="display">0</div>
        
        <div class="dartboard-grid" id="dartboard">
            <!-- Generated by JavaScript -->
        </div>
        
        <div class="multiplier-row">
            <button class="multiplier-btn" onclick="setMultiplier(1)">Single</button>
            <button class="multiplier-btn" onclick="setMultiplier(2)">Double</button>
            <button class="multiplier-btn" onclick="setMultiplier(3)">Triple</button>
        </div>
        
        <div class="action-row">
            <button class="action-btn undo" onclick="undo()">↶ Undo</button>
            <button class="action-btn submit" onclick="submit()">✓ Submit</button>
        </div>
    </div>
    
    <script>
        let selectedSegment = null;
        let selectedMultiplier = 1;
        let currentScore = 0;
        
        function initDartboard() {
            const dartboard = document.getElementById('dartboard');
            const segments = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,25];
            
            segments.forEach(seg => {
                const btn = document.createElement('button');
                btn.className = 'segment-btn';
                btn.textContent = seg === 25 ? 'B' : seg;
                btn.onclick = () => selectSegment(seg);
                dartboard.appendChild(btn);
            });
        }
        
        function selectSegment(seg) {
            selectedSegment = seg;
            updateDisplay();
        }
        
        function setMultiplier(mult) {
            selectedMultiplier = mult;
            updateDisplay();
        }
        
        function updateDisplay() {
            if (selectedSegment === null) {
                document.getElementById('display').textContent = '0';
                return;
            }
            
            let score = selectedSegment;
            if (selectedSegment === 25) {
                score = selectedMultiplier === 2 ? 50 : 25;
            } else {
                score = selectedSegment * selectedMultiplier;
            }
            
            currentScore = score;
            document.getElementById('display').textContent = score;
        }
        
        function undo() {
            selectedSegment = null;
            selectedMultiplier = 1;
            updateDisplay();
        }
        
        function submit() {
            if (currentScore > 0) {
                console.log('Submitted:', currentScore);
                // Send to server
                fetch('/api/dart', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ score: currentScore })
                });
                undo();
            }
        }
        
        initDartboard();
    </script>
</body>
</html>
        """
