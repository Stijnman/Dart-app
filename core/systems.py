
    def quick_match(self, player_name: str, mode: str = "501", max_players: int = 2) -> Optional[str]:
        """Find an open lobby or create a new one for quick matchmaking."""
        # First, try to find an open lobby that is waiting and not full
        for code, match_id in list(self.join_codes.items()):
            lobby = self.lobbies.get(match_id)
            if lobby and lobby.status == "waiting" and len(lobby.players) < lobby.max_players:
                if self.join_by_code(code, player_name):
                    return code

        # No suitable lobby found → create a new one
        return self.create_lobby(player_name, mode)

    def get_available_lobbies_count(self) -> int:
        """Return how many lobbies are currently waiting for players."""
        return sum(
            1 for lobby in self.lobbies.values()
            if lobby.status == "waiting" and len(lobby.players) < lobby.max_players
        )

    def cleanup_empty_lobbies(self):
        """Remove lobbies that have no players."""
        to_remove = []
        for match_id, lobby in self.lobbies.items():
            if len(lobby.players) == 0:
                to_remove.append(match_id)

        for match_id in to_remove:
            code = next((c for c, m in self.join_codes.items() if m == match_id), None)
            if code:
                del self.join_codes[code]
            del self.lobbies[match_id]

    def get_lobby_info(self, code: str) -> Optional[Dict]:
        """Get detailed info about a specific lobby."""
        match_id = self.join_codes.get(code.upper())
        if not match_id or match_id not in self.lobbies:
            return None

        lobby = self.lobbies[match_id]
        return {
            "code": code,
            "host": lobby.host,
            "mode": lobby.mode,
            "players": lobby.players,
            "max_players": lobby.max_players,
            "status": lobby.status,
            "spectators": len(lobby.spectators),
            "created_at": lobby.created_at
        }
