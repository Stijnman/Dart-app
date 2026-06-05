    def send_chat(self, from_player: str, message: str):
        if not hasattr(self, 'chat_history'):
            self.chat_history = []
        self.chat_history.append({
            "from": from_player,
            "msg": message,
            "time": datetime.now().isoformat()
        })

    def get_chat_history(self):
        if not hasattr(self, 'chat_history'):
            self.chat_history = []
        return self.chat_history[-30:]  # Return last 30 messages

    def clear_chat(self):
        self.chat_history = []