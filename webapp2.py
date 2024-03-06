import streamlit as st
import os
from PIL import Image
from gtts import gTTS
import io

def play_sound(text):
    tts = gTTS(text=text, lang='en')
    with io.BytesIO() as out:
        tts.save(out)
        out.seek(0)
        st.audio(out, format='audio/mp3')

def crop_image(image):
    st.write("Crop the image by dragging the corners of the box:")
    st.image(image, use_column_width=True)
    cropped_image = st.image_crop(image, key='crop')
    if cropped_image is not None:
        st.write("Cropped image:")
        st.image(cropped_image, use_column_width=True)
        st.download_button(label="Download cropped image", data=cropped_image, file_name="cropped_image.png")

def main():
    st.title("Dart Game")
    players = []

    with st.form("Player Registration"):
        name = st.text_input("Enter your name (optional):")
        image_file = st.file_uploader("Upload a profile picture:", type=['jpg', 'jpeg', 'png'])
        submitted = st.form_submit_button("Register")

        if submitted:
            player = {
                'name': name if name else "Anonymous Player",
                'image': Image.open(image_file) if image_file else None,
                'active': True,
            }
            players.append(player)
            st.success(f"Player {player['name']} registered!")

    for player in players:
        if player['active']:
            st.write(f"{player['name']}'s turn:")
            points = st.number_input("Enter points scored (0-50):", min_value=0, max_value=50)
            if points:
                player['score'] = points
                play_sound(f"{player['name']} scored {points} points.")

            if player['image']:
                crop_image(player['image'])

            st.write(f"{player['name']}'s score: {player['score']}")

        else:
            st.write(f"{player['name']}'s turn is over.")

    if st.button("Start Game"):
        active_players = [player for player in players if player['active']]
        if len(active_players) > 1:
            for player in active_players:
                player['active'] = False
                play_sound(f"{player['name']}'s turn is over.")

        st.write("Game started.")

    if st.button("Text-to-Speech"):
        text_to_speech("Game over! Thank you for playing.")

if __name__ == "__main__":
    main()