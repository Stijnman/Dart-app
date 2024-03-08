import streamlit as st  # Importing Streamlit library for creating the user interface
import os  # Importing os library for file handling
from PIL import Image  # Importing PIL library for image processing
from gtts import gTTS  # Importing gTTS library for text-to-speech conversion
import io  # Importing io library for handling binary data

def play_sound(text):
    """
    Function to convert text to speech and play the audio.

    Args:
    text (str): The text to be converted to speech.
    """
    tts = gTTS(text=text, lang='en')  # Creating a gTTS object for text-to-speech conversion
    with io.BytesIO() as out:  # Creating a binary data stream
        tts.save(out)  # Saving the converted audio to the binary data stream
        out.seek(0)  # Resetting the stream position to the beginning
        st.audio(out, format='audio/mp3')  # Playing the audio using Streamlit

def crop_image(image):
    """
    Function to crop an image using Streamlit's image cropping feature.

    Args:
    image (PIL.Image): The image to be cropped.
    """
    st.write("Crop the image by dragging the corners of the box:")  # Informing the user to crop the image
    st_image = st.image(image, use_column_width=True)  # Displaying the image
    cropped_image = st.image_crop(image, key='crop')  # Cropping the image
    if cropped_image is not None:  # If the image is cropped
        st.write("Cropped image:")  # Informing the user that the cropped image will be displayed
        st.image(cropped_image, use_column_width=True)  # Displaying the cropped image
        st.download_button(label="Download cropped image", data=cropped_image, file_name="cropped_image.png")  # Allowing the user to download the cropped image

def register_player():
    """
    Function to register a player by getting their name and profile picture.

    Returns:
    dict: A dictionary containing the player's name, profile picture, active status, and score.
    """
    name = st.text_input("Enter your name (optional):")  # Getting the player's name
    image_file = st.file_uploader("Upload a profile picture:", type=['jpg', 'jpeg', 'png'])  # Getting the player's profile picture
    submitted = st.form_submit_button("Register")  # Submitting the form

    if submitted:  # If the form is submitted
        return {
            'name': name if name else "Anonymous Player",  # Setting the player's name
            'image': Image.open(image_file) if image_file else None,  # Setting the player's profile picture
            'active': False,  # Setting the player's active status
            'score': 0,  # Setting the player's score
        }

def main():
    st.title("Dart Game")  # Setting the title of the game
    players = []  # Creating an empty list to store the players
    active_players = []  # Creating an empty list to store the active players

    while True:  # Running the game indefinitely
        cols = st.beta_columns(2)  # Creating two columns for the user interface
        player_form = cols[0].form_container()  # Creating a form container for the player registration form
        game_controls = cols[1].form_container()  # Creating a form container for the game controls

        with player_form:
            player = register_player()  # Registering a player
            if player:  # If a player is registered
                players.append(player)  # Adding the player to the list of players

        active_players = [player for player in players if player['active']]  # Getting the list of active players
        game_controls.write(f"Active Players: {len(active_players)}")  # Displaying the number of active players

        if len(active_players) > 1:  # If there are more than one active players
            for player in active_players:  # For each active player
                if not player['active']:  # If the player is not currently active
                    st.write(f"{player['name']}'s turn:")  # Informing the user that it's the player's turn
                    points = game_controls.number_input("Enter points scored (0-50):", min_value=0, max_value=50)  # Getting the points scored by the player
                    if points:  # If the player entered valid points
                        player['score'] = points  # Updating the player's score
                        play_sound(f"{player['name']} scored {points} points.")  # Announcing the player's score

                        if player['image']:  # If the player has a profile picture
                            crop_image(player['image'])  # Allowing the user to crop the profile picture

                        st.write(f"{player['name']}'s score: {player['score']}")  # Displaying the player's score

                        # Deactivate the current player and activate the next player
                        player['active'] = True
                        for other_player in active_players:
                            if other_player
