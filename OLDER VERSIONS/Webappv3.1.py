import streamlit as st  # Importing Streamlit library for creating the user interface
import os  # Importing os library for handling file paths
from PIL import Image  # Importing PIL library for handling images
from gtts import gTTS  # Importing gTTS library for converting text to speech
import io  # Importing io library for handling binary I/O

def play_sound(text):  # Function to convert text to speech and play it
    """
    This function takes a string as input, converts it to speech using gTTS, and plays the audio using Streamlit.

    Parameters:
    text (str): The text to be converted to speech.
    """
    tts = gTTS(text=text, lang='en')  # Convert the text to speech using gTTS
    with io.BytesIO() as out:  # Create an in-memory byte stream
        tts.save(out)  # Save the converted speech to the byte stream
        out.seek(0)  # Reset the stream position to the beginning
        st.audio(out, format='audio/mp3')  # Play the audio using Streamlit

def crop_image(image):  # Function to crop an image using Streamlit's image_crop method
    """
    This function takes an image as input, displays it with an option to crop, and returns the cropped image.

    Parameters:
    image: The image to be cropped.

    Returns:
    cropped_image: The cropped image.
    """
    st.write("Crop the image by dragging the corners of the box:")  # Instruct the user to crop the image
    st_image = st.image(image, use_column_width=True)  # Display the image
    cropped_image = st.image_crop(image, key='crop')  # Display the image with a crop tool
    if cropped_image is not None:  # If the user has cropped the image
        st.write("Cropped image:")  # Instruct the user that the cropped image will be displayed
        st.image(cropped_image, use_column_width=True)  # Display the cropped image
        st.download_button(label="Download cropped image", data=cropped_image, file_name="cropped_image.png")  # Allow the user to download the cropped image
        return cropped_image  # Return the cropped image

def register_player():  # Function to register a new player
    """
    This function takes no input and returns a dictionary containing the player's name, image, and score.

    Returns:
    player (dict): A dictionary containing the player's name, image, and score.
    """
    name = st.text_input("Enter your name (optional):")  # Allow the user to enter their name
    image_file = st.file_uploader("Upload a profile picture:", type=['jpg', 'jpeg', 'png'])  # Allow the user to upload a profile picture
    submitted = st.form_submit_button("Register")  # Allow the user to submit the form

    if submitted:  # If the user has submitted the form
        if not name:  # If the user did not enter a name
            name = "Anonymous Player"  # Set the name to "Anonymous Player"

        if image_file:  # If the user uploaded a profile picture
            try:  # Try to open the image file
                image = Image.open(image_file)
            except Exception as e:  # If there is an error opening the image file
                st.error(f"Error: {e}")  # Display an error message
                return None  # Return None
        else:  # If the user did not upload a profile picture
            image = None  # Set the image to None

        return {'name': name, 'image': image, 'active': True, 'score': 0}  # Return a dictionary containing the player's name, image, and score

def announce_next_player(player):  # Function to announce the next player's turn
    """
    This function takes a player dictionary as input and plays a text-to-speech message announcing the next player's turn.

    Parameters:
    player (dict): A dictionary containing the next player's name and image.
    """
    play_sound(f"{player['name']}'s turn.")  # Play a text-to-speech message announcing the next player's turn

def main():  # Main function
    """
    This function contains the main game loop and handles user input and game logic.
    """
    st.title("Dart Game")  # Display the game title
    players = []  # Initialize an empty list to store the players

    while True:  # Game loop
        cols = st.beta_columns(2)  # Create two columns for the player registration form and game controls
        player_form = cols[0].form_container()  # Create a form container for the player registration form
        game_controls = cols[1].form_container()  # Create a form container for the game controls

        player = register_player()  # Register a new player
        if player:  # If a new player was registered
            players.append(player)  # Add the new player to the list of players

        active_players = [player for player in players if player['active']]  # Get a list of active players
        if len(active_players) > 0:  # If there are any active players
            current_player = active_players[0]  # Get the current player
            announce_next_player(current_player)  # Announce the current player's turn

            for player in active_players:  # Loop through all active players
                if player['active']:  # If the player is active
                    st.write(f"{player['name']}'s turn:")  # Display a message indicating the player's turn
                    points = game_controls.number_input("Enter points scored (0-50):", min_value=0, max_value=50)  # Allow the user to enter the points scored
                    if points:  # If the user entered a valid number
                        player['score'] = points  # Update the player's
