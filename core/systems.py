    def quick_match(self, player_name: str, mode: str = "501", max_players: int = 2, player_avg: float = 50.0) -> Optional[str]:
        """Find an open lobby or create a new one. Tries to match players with similar averages."""
        best_match = None
        best_diff = 999

        for code, match_id in list(self.join_codes.items()):
            lobby = self.lobbies.get(match_id)
            if not lobby or lobby.status != "waiting":
                continue
            if len(lobby.players) >= lobby.max_players:
                continue

            # Simple skill matching
            lobby_avg = getattr(lobby, 'avg', 50.0)
            diff = abs(lobby_avg - player_avg)

            if diff < best_diff:
                best_diff = diff
                best_match = code

        if best_match:
            if self.join_by_code(best_match, player_name):
                return best_match

        # No good match found → create new lobby
        code = self.create_lobby(player_name, mode)
        if code in self.join_codes:
            match_id = self.join_codes[code]
            if match_id in self.lobbies:
                self.lobbies[match_id].avg = player_avg
        return code