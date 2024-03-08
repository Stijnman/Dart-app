import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os
import speech_recognition as sr
from tkinter import messagebox

class Player:
    def __init__(self, name, picture, anonymous=False):
        self.name = name
        self.picture = picture
        self.score = 501
        self.anonymous = anonymous

class DartGameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dart Game")
        self.player = None
        self.picture = None
        self.microphone_active = False
        self.initialize_ui()
        self.initialize_speech_recognition()

    def initialize_ui(self):
        self.name_var = tk.StringVar()
        self.name_entry = tk.Entry(self.root, textvariable=self.name_var)
        self.name_entry.pack()

        self.picture_button = tk.Button(self.root, text="Browse Picture", command=self.browse_picture)
        self.picture_button.pack()

        self.register_button = tk.Button(self.root, text="Register", command=self.register_player)
        self.register_button.pack()

        self.game_options = ["Bullseye Measurement", "501", "301", "Cricket"]
        self.game_var = tk.StringVar(self.root)
        self.game_var.set(self.game_options[0])
        self.game_dropdown = tk.OptionMenu(self.root, self.game_var, *self.game_options)
        self.game_dropdown.pack()

        self.start_button = tk.Button(self.root, text="Start Game", command=self.start_game)
        self.start_button.pack()

        self.microphone_button = tk.Button(self.root, text="Microphone: OFF", command=self.toggle_microphone, bg="red")
        self.microphone_button.pack()

        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=200, mode="indeterminate")
        self.progress_bar.pack()

        self.message_label = tk.Label(self.root, text="Waiting for user input...")
        self.message_label.pack()

    def initialize_speech_recognition(self):
        self.recognizer = sr.Recognizer()
        self.update_timer = self.root.after(5000, self.update_progress_and_message)

    def browse_picture(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.picture = file_path

    def register_player(self):
        name = self.name_var.get()
        if name:
            self.player = Player(name, self.picture)
        else:
            self.player = Player("Anonymous", self.picture, anonymous=True)
        self.progress_bar.stop()
        self.message_label.config(text=f"Player {self.player.name} registered!")

    def start_game(self):
        if not self.player:
            messagebox.showerror("Error", "Please register or start the game anonymously.")
            return
        self.progress_bar.start()
        self.message_label.config(text="Game starting...")
        self.select_game()

    def update_progress_and_message(self):
        if self.player:
            if not self.microphone_active:
                self.message_label.config(text="Microphone is OFF. Click on the microphone button to turn it ON.")
            else:
                self.select_game()

    def select_game(self):
        game_option = self.game_var.get()
        if game_option == "Bullseye Measurement":
            self.bullseye_measurement()
        elif game_option == "501":
            self.game_501()
        elif game_option == "301":
            self.game_301()
        elif game_option == "Cricket":
            self.game_cricket()

    def bullseye_measurement(self):
        self.player.score = 0
        self.progress_bar.start()
        self.message_label.config(text="Please say the distance to the bullseye in centimeters.")
        self.listen_and_process_speech()

    def game_501(self):
        self.player.score = 501
        self.progress_bar.start()
        self.message_label.config(text="Please say the score of each dart, separated by commas.")
        self.listen_and_process_speech()

    def game_301(self):
        self.player.score = 301
        self.progress_bar.start()
        self.message_label.config(text="Please say the score of each dart, separated by commas.")
        self.listen_and_process_speech()

    def game_cricket(self):
        # Implement the logic for the cricket game
        pass

    def toggle_microphone(self):
        if self.microphone_active:
            self.microphone_active = False
            self.microphone_button.config(text="Microphone: OFF", bg="red")
        else:
            self.microphone_active = True
            self.microphone_button.config(text="Microphone: ON", bg="green")

    def listen_and_process_speech(self):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            try:
                audio = self.recognizer.listen(source)
                text
