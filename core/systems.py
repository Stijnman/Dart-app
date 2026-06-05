    def get_open_lobbies(self) -> List[Dict]:
        return [
            {"code": code, "host": self.lobbies[match_id].host, "mode": self.lobbies[match_id].mode, "players": f"{len(self.lobbies[match_id].players)}/{self.lobbies[match_id].max_players}"}
            for code, match_id in self.join_codes.items()
            if match_id in self.lobbies and self.lobbies[match_id].status == "waiting"
        ]