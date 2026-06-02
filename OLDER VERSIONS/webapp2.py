import streamlit as st  # Import Streamlit library for creating the user interface
import os  # Import os library for file handling
from PIL import Image  # Import PIL library for image processing
from gtts import gTTS  # Import gTTS library for text-to-speech conversion
import io  # Import io library for handling binary data
import base64  # Import base64 library for encoding binary data

def play_sound(text):
    """
    Function to convert text to speech and play the audio.
    :param text: str, text to be converted to speech
    """
    tts = gTTS(text=text, lang='en')  # Initialize gTTS object
    with io.BytesIO() as out:  # Create an in-memory byte stream
        tts.save(out)  # Save the generated audio to the byte stream
        out.seek(0)  # Reset the stream position to the beginning
        st.audio(out, format='audio/mp3')  # Play the audio using Streamlit

def crop_image(image):
    """
    Function to let the user crop an image and download it.
    :param image: PIL.Image, the image to be cropped
    """
    st.write("Crop the image by dragging the corners of the box:")  # Instruct the user to crop the image
    st.image(image, use_column_width=True)  # Display the image
    cropped_image = st.image_crop(image, key='crop')  # Let the user crop the image
    if cropped_image is not None:
        st.write("Cropped image:")
        st.image(cropped_image, use_column_width=True)  # Display the cropped image
        img_bytes = cropped_image.tobytes()  # Convert the cropped image to bytes
        img_b64 = base64.b64encode(img_bytes).decode()  # Encode the bytes to base64
        download_link = f'<a href="data:image/png;base64,{img_b64}" download="cropped_image.png">Download cropped image</a>'  # Create a download link
        st.markdown(download_link, unsafe_allow_html=True)  # Display the download link

def main():
    st.title("Dart Game")  # Set the title of the user interface
    players = []  # Initialize an empty list to store the players

    with st.form("Player Registration"):  # Create a form for registering players
        name = st.text_input("Enter your name (optional):")  # Input for the player's name
        image_file = st.file_uploader("Upload a profile picture:", type=['jpg', 'jpeg', 'png'])  # Input for the player's profile picture
        submitted = st.form_submit_button("Register")  # Submit button for registering the player

        if submitted:
            player = {
                'name': name if name else "Anonymous Player",  # Set the player's name
                'image': Image.open(image_file) if image_file else None,  # Open and set the player's profile picture
                'active': True,  # Set the player's turn to active
                'score': 0  # Initialize the player's score
            }
            players.append(player)  # Add the player to the list of players
            st.success(f"Player {player['name']} registered!")  # Confirm the registration

    for player in players:
        if player['active']:
            st.write(f"{player['name']}'s turn:")  # Display the active player's name
            points = st.number_input("Enter points scored (0-50):", min_value=0, max_value=50)  # Input for the points scored
            if points:
                player['score'] = points  # Update the player's score
                play_sound(f"{player['name']} scored {points} points.")  # Play a sound with the player's name and points

            if player['image']:
                crop_image(player['image'])  # Let the player crop their
