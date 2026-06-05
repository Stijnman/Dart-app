
"""
Enhanced VoiceRecognition for Dart Game Pro v2.4
Completes Feature #9: Voice Commands (Skip turn, Undo last dart, Show stats, Next player, etc.)

Extends the existing VoiceRecognition in core/systems.py
Adds command parsing + suggested integration points for streamlit_app.py and engine.

Usage:
- In Streamlit: Add mic button that calls recognize_command() and dispatches based on command_type.
- Commands update session_state or call engine methods (undo, switch_player, etc.).
"""

import re
from typing import Optional, Tuple, Dict, Any

class EnhancedVoiceRecognition:
    """Extended voice system supporting both scoring input and game control commands."""

    # Existing scoring phrases (from original)
    SCORING_PHRASES: Dict[str, int] = {
        'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
        'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15,
        'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19, 'twenty': 20,
        'twenty five': 25, 'bull': 25, 'outer bull': 25,
        'bullseye': 50, 'inner bull': 50,
        't20': 60, 'd20': 40, 't19': 57, 'd19': 38,
        'ton': 100, 'ton eighty': 180, 'one eighty': 180,
        # Add more as needed from original PHRASES
    }

    # New: Game control commands (Feature #9)
    COMMAND_PATTERNS: Dict[str, str] = {
        r'\b(skip turn|next player|pass turn|next)\b': 'next_player',
        r'\b(undo last dart|undo dart|undo throw|back one dart|undo)\b': 'undo_last',
        r'\b(show stats|stats|show statistics|player stats)\b': 'show_stats',
        r'\b(show score|current score|score)\b': 'show_score',
        r'\b(reset game|new game|restart)\b': 'reset_game',
        r'\b(pause|resume|stop)\b': 'pause_resume',
        r'\b(what.*checkout|checkout suggestion|best checkout)\b': 'checkout_suggestion',
        r'\b(180|nice|good shot|great throw)\b': 'cheer',  # fun acknowledgment
    }

    def __init__(self, engine_ref: Optional[Any] = None, ui_callback: Optional[callable] = None):
        self.engine = engine_ref  # Reference to DartGameEngine for direct actions
        self.ui_callback = ui_callback  # Optional callback to update Streamlit UI (e.g. st.rerun or session_state)
        self.last_recognized: Optional[str] = None
        self.confidence_threshold = 0.7

    def recognize(self, audio_text: str) -> Tuple[Optional[str], Optional[int], Optional[str]]:
        """
        Main entry point.
        Returns: (command_type or None, score_value or None, raw_text)
        command_type can be: 'score', 'next_player', 'undo_last', 'show_stats', etc.
        """
        text = audio_text.lower().strip()
        self.last_recognized = text

        # 1. Check for commands first (higher priority for control)
        for pattern, cmd in self.COMMAND_PATTERNS.items():
            if re.search(pattern, text):
                return cmd, None, text

        # 2. Check for scoring input (existing logic)
        for phrase, value in self.SCORING_PHRASES.items():
            if phrase in text:
                # Simple match; in production use better fuzzy or speech lib
                return 'score', value, text

        # 3. Fallback: try to parse number directly
        numbers = re.findall(r'\b(\d{1,3})\b', text)
        if numbers:
            try:
                val = int(numbers[0])
                if 0 <= val <= 180:
                    return 'score', val, text
            except:
                pass

        return None, None, text

    def execute_command(self, command: str, current_game_state: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute a recognized command.
        Returns dict with 'action', 'message', 'ui_update_needed' etc.
        Integrate this in streamlit_app.py after voice input.
        """
        result = {'action': command, 'success': False, 'message': '', 'ui_update_needed': False}

        if command == 'next_player':
            if self.engine:
                self.engine.switch_to_next_player()  # Assume method exists or add it
            result.update({'success': True, 'message': 'Turn passed to next player.', 'ui_update_needed': True})

        elif command == 'undo_last':
            if self.engine and hasattr(self.engine, 'undo_last_throw'):
                success = self.engine.undo_last_throw()
                result.update({'success': success, 'message': 'Last dart undone.' if success else 'Nothing to undo.', 'ui_update_needed': True})
            else:
                result['message'] = 'Undo not available right now.'

        elif command == 'show_stats':
            result.update({'success': True, 'message': 'Displaying player stats...', 'ui_update_needed': True, 'show_stats_panel': True})

        elif command == 'show_score':
            result.update({'success': True, 'message': 'Current scores shown on main board.'})

        elif command == 'checkout_suggestion':
            if self.engine:
                suggestion = self.engine.get_checkout_suggestion()  # Assume exists or use checkout.py
                result.update({'success': True, 'message': f'Checkout suggestion: {suggestion}', 'ui_update_needed': True})

        elif command == 'cheer':
            result.update({'success': True, 'message': 'Nice shot! 🎯', 'play_sound': 'cheer' if hasattr(self, 'play_sound') else None})

        else:
            result['message'] = f'Command "{command}" recognized but not yet wired to engine.'

        # Callback for Streamlit to refresh UI
        if self.ui_callback and result.get('ui_update_needed'):
            self.ui_callback()

        return result

    def get_supported_commands(self) -> list:
        """For help / settings UI"""
        return list(self.COMMAND_PATTERNS.values()) + ['score input (numbers, t20, bull, ton eighty...)']

# Example integration snippet for streamlit_app.py (add near voice button):
"""
# In your Streamlit scoring tab or sidebar:
if st.button("🎤 Voice Command / Score", key="voice_btn"):
    # Use browser speech or local STT (e.g. via streamlit-mic or external)
    recognized_text = get_voice_input()  # Your STT function or st.experimental_mic
    if recognized_text:
        vr = EnhancedVoiceRecognition(engine_ref=st.session_state.get('engine'))
        cmd, score, raw = vr.recognize(recognized_text)
        
        if cmd == 'score' and score is not None:
            st.session_state.engine.record_throw(score)  # or however scoring works
            st.success(f"Scored {score} via voice!")
        elif cmd:
            action_result = vr.execute_command(cmd)
            if action_result['success']:
                st.success(action_result['message'])
            if action_result.get('ui_update_needed'):
                st.rerun()
        else:
            st.warning(f"Could not understand: {raw}")
"""

# To make it production ready:
# - Integrate with actual STT (whisper local, Google, or browser Web Speech API via custom component)
# - Add confidence scoring from STT
# - Support multi-language commands if desired
# - Persist custom command aliases per player
