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
        self.label_name = tk.Label(self.root, text="Enter your name (optional):")
        self.label_name.pack()
        self.entry_name = tk.Entry(self.root)
        self.entry_name.pack()

        self.button_browse = tk.Button(self.root, text="Browse Picture", command=self.browse_picture)
        self.button_browse.pack()

        self.button_register = tk.Button(self.root, text="Register (optional)", command=self.register_player)
        self.button_register.pack()

        self.label_game_options = tk.Label(self.root, text="Select the game you want to play:")
        self.label_game_options.pack()

        self.var_game_option = tk.StringVar(self.root)
        self.var_game_option.set("Bullseye Measurement")
        self.game_options = {"Bullseye Measurement": self.bullseye_measurement, "501": self.game_501, "301": self.game_301, "Cricket": self.game_cricket}
        self.dropdown_game_option = tk.OptionMenu(self.root, self.var_game_option, *self.game_options.keys())
        self.dropdown_game_option.pack()

        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=200, mode="indeterminate")
        self.progress_bar.pack()
        self.message_label = tk.Label(self.root, text="Waiting for user input...")
        self.message_label.pack()

        self.button_start_game = tk.Button(self.root, text="Start Game", command=self.start_game)
        self.button_start_game.pack()

        self.microphone_button = tk.Button(self.root, text="Microphone: OFF", command=self.toggle_microphone, bg="red")
        self.microphone_button.pack()

    def initialize_speech_recognition(self):
        self.recognizer = sr.Recognizer()
        self.update_timer = self.root.after(5000, self.update_progress_and_message)

    def browse_picture(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.picture = file_path

    def register_player(self):
        name = self.entry_name.get()
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
                if self.var_game_option.get() != "Bullseye Measurement":
                    self.select_game()
                else:
                    self.message_label.config(text="Please say the distance to the bullseye in centimeters.")
                    self.listen_and_process_speech()

    def listen_and_process_speech(self):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            try:
                audio = self.recognizer.listen(source)
                text = self.recognizer.recognize_google(audio)
                distance = float(text)
                if 0 <= distance <= 15.9:
                    self.message_label.config(text=f"Congratulations, {self.player.name}! You have hit the bullseye!")
                    self.root.after_cancel(self.update_timer)
                else:
                    self.message_label.config(text="Sorry, you missed the bullseye. Please try again.")
            except sr.UnknownValueError:
                self.message_label.config(text="Sorry, I could not understand you. Please try again.")
            except sr.RequestError as e:
                self.message_label.config(text=f"Could not request results; {e}")

    def select_game(self):
        game_option = self.var_game_option.get()
        self.game_options[game_option]()

    def bullseye_measurement(self):
        self.player.score = 0
        self.progress_bar.start()
        self.message_label.config(text="Please say the distance to the bullseye in centimeters.")

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

if __name__ == "__main__":
    root = tk.Tk()
    app = DartGameApp(root)
    root.mainloop()
