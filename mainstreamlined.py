import streamlit as st

class Player:
    def __init__(self, name, picture, anonymous=False):
        self.name = name
        self.picture = picture
        self.score = 501
        self.anonymous = anonymous

def main():
    st.title("Dart Game")

    name = st.text_input("Enter your name (optional):")
    picture = st.file_uploader("Upload Picture (optional):", type=["jpg", "png"])

    game_option = st.selectbox("Select the game you want to play:", ["Bullseye Measurement", "501", "301", "Cricket"])

    if st.button("Register (optional)"):
        player = Player(name, picture)
        st.success(f"Player {player.name} registered!")

        # Add game logic based on the selected option
        if game_option == "Bullseye Measurement":
            st.write("Implement Bullseye Measurement game logic here.")
        elif game_option == "501":
            st.write("Implement 501 game logic here.")
        elif game_option == "301":
            st.write("Implement 301 game logic here.")
        elif game_option == "Cricket":
            st.write("Implement Cricket game logic here.")

if __name__ == "__main__":
    main()
