import tkinter
import tkinter.messagebox
import customtkinter
from PIL import Image, ImageTk

import os

from handler_tweet import TweetHandler
from handler_folder import FolderHandler

##########################################################
##########################################################
##########################################################

class App(customtkinter.CTk):

    WIDTH = 900
    HEIGHT = 550

    def __init__(self):
        super().__init__()

        data_dir = os.path.join(os.getcwd(), "data_files")
        if not os.path.isdir(data_dir):
            os.mkdir(data_dir)

        icon = Image.open(os.path.join(os.getcwd(), "images/icon_french_embassy.png"))
        icon = ImageTk.PhotoImage(icon)
        self.iconphoto(False, icon)

        self.title("French Embassy Twitter Tool")
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # call .on_closing() when app gets closed

        # configure grid layout (2x1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ============ frame_left ============

        self.frame_left = customtkinter.CTkFrame(master=self,
                                                 width=180,
                                                 corner_radius=0)
        self.frame_left.grid(row=0, column=0, sticky="nswe")

        # configure grid layout (1x11)
        self.frame_left.grid_rowconfigure(0, minsize=10)   # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(5, weight=1)  # empty row as spacing
        self.frame_left.grid_rowconfigure(8, minsize=20)    # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(11, minsize=10)  # empty row with minsize as spacing

        self.side_bar()

        self.clicked_on(self.button_1)

        self.tweet_handler = TweetHandler(self)
        self.frame_right = self.tweet_handler.frame_get

        self.processStep = 0

        self.folder_handler = FolderHandler(self)

    def clicked_on(self, button):
        button.configure(fg_color = "#243b61")
        button.configure(state = tkinter.DISABLED)

    def back_to_normal(self, button):
        button.configure(fg_color = "#395E9C")
        button.configure(state = tkinter.NORMAL)

    def side_bar(self):
        self.label_1 = customtkinter.CTkLabel(master=self.frame_left,
                                              text="Twitter Tool",
                                              text_font=("Roboto Medium", -16))  # font name and size in px
        self.label_1.grid(row=1, column=0, pady=10, padx=20)

        self.button_1 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Get Tweets",
                                                command=self.get_tweets)
        self.button_1.grid(row=2, column=0, pady=10, padx=20)

        self.button_2 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Analyze Results",
                                                command=self.analyze_tweets)
        self.button_2.grid(row=4, column=0, pady=10, padx=20)

        image = Image.open(os.path.join(os.getcwd(), "images/logo_french_embassy.png")).resize((100,100))
        self.french_logo = ImageTk.PhotoImage(image)
        self.image_label = tkinter.Label(master=self.frame_left, image=self.french_logo)
        self.image_label.grid(row = 6, column = 0)
        

    # ============ engines ============

    def get_tweets(self):
         if self.processStep != 0:
            self.processStep = 0

            self.clicked_on(self.button_1)
            self.back_to_normal(self.button_2)
            
            self.frame_right.destroy()
            self.tweet_handler.make_tweet_getter_frame()

            self.tweet_handler.label_info_3.set_text(self.tweet_handler.terminalMessage)
            
            if self.tweet_handler.activeThread:
                self.tweet_handler.buttons_when_fetching()
            elif self.tweet_handler.valid_run:
                self.tweet_handler.post_scrape_update()

            self.frame_right = self.tweet_handler.frame_get
    
    def analyze_tweets(self):
        if self.processStep != 1:
            self.processStep = 1
            self.tweet_handler.frame_still_valid = False

            self.clicked_on(self.button_2)
            self.back_to_normal(self.button_1)

            self.folder_handler.updateDirectory()

            self.frame_right.destroy()
            
            if ".json" in self.folder_handler.cur_path:
                self.folder_handler.make_file_frame()
            else:
                self.folder_handler.make_analysis_frame()
            self.frame_right = self.folder_handler.frame_folders

    ######################################################
    
    def on_closing(self, event=0):
        self.destroy()

##########################################################
##########################################################
##########################################################

if __name__ == "__main__":
    customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
    customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

    app = App()
    app.mainloop()