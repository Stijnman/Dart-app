class LobbySystem:
    """Open lobby matchmaking system."""

    def __init__(self):
        self.lobbies: Dict[str, OnlineMatch] = {}
        self.join_codes: Dict[str, str] = {}  # code -> match_id

    def create_lobby(self, host: str, mode: str = "501") -> str:
        match_id = hashlib.md5(f"{host}{datetime.now()}".encode()).hexdigest()[:8]
        code = match_id.upper()
        self.lobbies[match_id] = OnlineMatch(match_id, host, mode)
        self.join_codes[code] = match_id
        return code

    def join_by_code(self, code: str, player: str) -> bool:
        match_id = self.join_codes.get(code.upper())
        if match_id and match_id in self.lobbies:
            return self.lobbies[match_id].join(player)
        return False

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

    def get_open_lobbies(self) -> List[Dict]:
        return [
            {"code": code, "host": self.lobbies[match_id].host, "mode": self.lobbies[match_id].mode,
             "players": f"{len(self.lobbies[match_id].players)}/{self.lobbies[match_id].max_players}"}
            for code, match_id in self.join_codes.items()
            if match_id in self.lobbies and self.lobbies[match_id].status == "waiting"
        ]

    def get_available_lobbies_count(self) -> int:
        return sum(
            1 for lobby in self.lobbies.values()
            if lobby.status == "waiting" and len(lobby.players) < lobby.max_players
        )

    def get_lobby_info(self, code: str) -> Optional[Dict]:
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
            "created_at": lobby.created_at
        }