import tkinter as tk
from tkinter import ttk, filedialog
import os
import speech_recognition as sr

class Player:
    def __init__(self, name, picture, anonymous=False):
        """
        Initialize a new Player instance with a name, picture, and an anonymous flag.

        :param name: The name of the player.
        :param picture: The file path of the player's picture.
        :param anonymous: A boolean indicating if the player is anonymous.
        """
        self.name = name
        self.picture = picture
        self.score = 501  # Default score for dart games
        self.anonymous = anonymous

class DartGameApp:
    def __init__(self, root):
        """
        Initialize a new DartGameApp instance with a root tkinter window.

        :param root: The root tkinter window for the application.
        """
        self.root = root
        self.root.title("Dart Game")
        self.player = None
        self.picture = None
        self.microphone_active = False
        self.initialize_ui()
        self.initialize_speech_recognition()

    def initialize_ui(self):
        """
        Initialize and layout the user interface components.
        """
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

        self.result_label = tk.Label(self.root, text="")
        self.result_label.pack()

    def initialize_speech_recognition(self):
        """
        Initialize the speech recognition system.
        """
        self.recognizer = sr.Recognizer()
        self.update_timer = self.root.after(5000, self.update_progress_and_message)

    def browse_picture(self):
        """
        Open a file dialog to let the user select a picture.
        """
        file_path = filedialog.askopenfilename()
        if file_path:
            self.picture = file_path

    def register_player(self):
        """
        Register a new player with the given name and picture.
        """
        name = self.name_var.get()
        if name:
            self.player = Player(name, self.picture)
        else:
            self.player = Player("Anonymous", self.picture, anonymous=True)
        self.progress_bar.stop()
        self.message_label.config(text=f"Player {self.player.name} registered!")

    def start_game(self):
        """
        Start the game with the selected game mode.
        """
        if not self.player:
            messagebox.showerror("Error", "Please register or start the game anonymously.")
            return
        self.progress_bar.start()
        self.message_label.config(text="Game starting...")
        self.select_game()

    def update_progress_and_message(self):
        """
        Update the progress bar and message label.
        """
        if self.player:
            if not self.microphone_active:
                self.message_label.config(text="Microphone is OFF. Click on the microphone button to turn it ON.")
            else:
                self.select_game()

    def select_game(self):
        """
        Select and start the game based on the selected game mode.
        """
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
        """
        Start the bullseye measurement game.
        """
        self.player.score = 0
        self.progress_bar.start()
        self.message_label.config(text="Please say the distance to the bullseye in centimeters.")
        self.listen_and_process_speech()

    def game_501(self):
        """
        Start the 501 game.
        """
        self.player.score = 501
        self.progress_bar.start()
        self.message_label.config(text="
