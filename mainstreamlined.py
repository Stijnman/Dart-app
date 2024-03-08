import streamlit as st

class Player:
    def __init__(self, name, picture, anonymous=False):
        self.name = name or "Anonymous"
        self.picture = picture
        self.score = 501 if self.name != "Anonymous" else 0
        self.anonymous = anonymous

def main():
    st.title("Dart Game")

    name = st.text_input("Enter your name (optional):", "Anonymous")
    picture = st.file_uploader("Upload Picture (optional):", type=["jpg", "png"])

    game_option = st.selectbox("Select the game you want to play:", ["Bullseye Measurement", "501", "301", "Cricket"])

    player = Player(name, picture)
    st.success(f"Player {player.name} registered!")

    if player.score == 0:
        st.warning(f"Player {player.name} is anonymous and cannot play scoring games.")
    else:
        if st.button("Start Game"):
            if game_option == "Bullseye Measurement":
                st.write("Implement Bullseye Measurement game logic here.")
            elif game_option in ["501", "301"]:
                st.write(f"Start {game_option} game for {player.name}.")
            elif game_option == "Cricket":
                st.write(f"Start Cricket game for {player.name}.")

if __name__ == "__main__":
    main()
