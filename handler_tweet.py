import tkinter
import tkinter.messagebox
import customtkinter

import random
import os
import json
import threading

from tweet_fetcher_twint import TweetFetcher
from tweet_filter import Filter

##########################################################
##########################################################
##########################################################

class TweetHandler(object):

    MAX_NUM_TWEETS = 5000

    def __init__(self, other_self):
        self.other_self = other_self
        self.make_tweet_getter_frame()

        self.activeThread = False
        self.terminalMessage = ""

        self.valid_run = False
        self.frame_still_valid = True

    def make_tweet_getter_frame(self):
        self.frame_still_valid = True
        self.frame_get = customtkinter.CTkFrame(master=self.other_self)
        self.frame_get.grid(row=0, column=1, sticky="nswe", padx=10, pady=10)

        # configure grid layout (3x7)
        self.frame_get.rowconfigure((0, 1, 2, 3), weight=1)
        self.frame_get.rowconfigure(7, weight=10)
        self.frame_get.columnconfigure((0, 1), weight=1)
        self.frame_get.columnconfigure(2, weight=0)

        # ============ random tweets ============

        self.label_info_1 = customtkinter.CTkLabel(master=self.frame_get,
                                                   text="",
                                                   height=150,
                                                   fg_color=("white", "gray38"),
                                                   corner_radius = 10,
                                                   wraplength = 420)
        self.label_info_1.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky="ew")

        self.button_1 = customtkinter.CTkButton(master=self.frame_get,
                                                text=">",
                                                width = 40,
                                                height = 150,
                                                command = self.changeTweet)
        self.button_1.grid(row=0, column=2, pady=10, padx=10)

        # ============ parameters ============

        self.numTweets = int(round(self.MAX_NUM_TWEETS * 0.5,0))

        self.frame_num_tweets = customtkinter.CTkFrame(master=self.frame_get)
        self.frame_num_tweets.grid(row=1, column=0, columnspan=3, rowspan=2, pady=0, padx=10, sticky="nsew")
        self.frame_num_tweets.rowconfigure(0, weight=1)
        self.frame_num_tweets.columnconfigure(0, weight=1)

        self.label_info_2 = customtkinter.CTkLabel(master=self.frame_num_tweets, 
                                                    text=f"Fetch {self.numTweets} Tweets (per keyword, etc.):",
                                                    corner_radius = 10)
        self.label_info_2.grid(row=3, column=0, pady=5, padx=5, sticky="ew")

        self.slider = customtkinter.CTkSlider(master=self.frame_num_tweets,
                                                number_of_steps=10,
                                                command = self.updateSliderVal)
        self.slider.grid(row=4, column=0, pady=5, padx=5, sticky="ew")


        self.entry = customtkinter.CTkEntry(master=self.frame_get,
                                            width=120,
                                            placeholder_text="keywords, hashtags, usernames (ex: \"Macron, #macron, @EmmanuelMacron\")")
        self.entry.grid(row=5, column=0, columnspan=2, pady=10, padx=10, sticky="ew")

        self.button_2 = customtkinter.CTkButton(master=self.frame_get,
                                                text="Ok",
                                                width = 40,
                                                height = 30,
                                                command = self.update_terminal)
        self.button_2.grid(row=5, column=2, padx = 10)
        
        # ============ terminal ============

        self.label_info_3 = customtkinter.CTkLabel(master=self.frame_get,
                                                   text="Awaiting keywords..." ,
                                                   height=100,
                                                   corner_radius = 10,
                                                   fg_color=("white", "gray38"))
        self.label_info_3.grid(row=7, column=0, columnspan=3, pady=10, padx=10, sticky="sew")

        self.button_3 = customtkinter.CTkButton(master=self.frame_get,
                                                text="Confirm",
                                                width = 20,
                                                command=self.scrape_threading)
        self.button_3.grid(row=8, column=0, columnspan = 3, pady=10, padx=10, sticky = "ew")


        self.button_1.configure(state = tkinter.DISABLED)
        self.button_3.configure(state= tkinter.DISABLED)
        
        self.slider.set(0.5)

    # ============ helper functions ============

    def updateSliderVal(self, val):
        self.numTweets = int(round(val * self.MAX_NUM_TWEETS,0))
        self.label_info_2.set_text(f"Fetch {self.numTweets} Tweets (per keyword, etc.):")

    def changeTweet(self):
        tweet = self.lstDct[random.randint(0,len(self.lstDct) - 1)][0]
        self.label_info_1.set_text(tweet)

    def clicked_on(self, button):
        button.configure(fg_color = "#243b61")
        button.configure(state = tkinter.DISABLED)

    def back_to_normal(self, button):
        button.configure(fg_color = "#395E9C")
        button.configure(state = tkinter.NORMAL)

    # ============ engines ============

    def update_terminal(self):
        self.parameters = list(set(self.entry.get().split(', ')))
        if self.parameters == ['']:
            self.label_info_3.set_text("Keyword(s) required for a search!")
        else:
            self.back_to_normal(self.button_3)

            self.totalTweets = self.numTweets * len(self.parameters)
            self.label_info_3.set_text(f"Search parameters: {self.parameters}\nExpected to retrieve {self.totalTweets} tweets in {int(round(self.totalTweets / 2000,0))} minute(s)\n\nPress \"Confirm\" to continue \n(to register updated parameters \"Ok\" must be pressed again)")

    def scrape_threading(self):
        if threading.active_count() >= 4:
            self.label_info_3.set_text("Too many operations are running at once!\nplease wait a little bit...")
        else:
            self.activeThread = True
            self.terminalMessage = self.label_info_3.text.replace("Press \"Confirm\" to continue \n(to register updated parameters \"Ok\" must be pressed again)", "Currently running...")
            self.label_info_3.set_text(self.terminalMessage)
            self.clicked_on(self.button_3)
            self.clicked_on(self.button_2)

            threading.Thread(target = self.scrape_tweets).start()

    def post_scrape_update(self):
        self.label_info_3.set_text(f"{self.terminalMessage}")

        self.button_3.configure(state = tkinter.DISABLED)
        self.button_1.configure(state = tkinter.NORMAL)

        self.changeTweet()
    
    def buttons_when_fetching(self):
        self.clicked_on(self.button_2)
        self.clicked_on(self.button_3)

    def scrape_tweets(self):
        og_base_path = os.getcwd()

        self.outputFileName = "tweets_" + self.parameters[0]
        tweetFetcher = TweetFetcher(self.outputFileName)
        self.files_path = tweetFetcher.search(self.parameters, self.numTweets)

        filterHandler = Filter(self.outputFileName)
        self.terminalMessage = filterHandler.cleanEnglish()

        folder_name = self.outputFileName.replace('tweets_', "")
        f = open(os.path.join(self.files_path, folder_name +"/"+ self.outputFileName + f".json"), "r")
        self.lstDct = json.load(f)
        os.chdir(og_base_path)

        if self.frame_still_valid:
            self.post_scrape_update()
            self.button_2.configure(fg_color = "#395E9C")
            self.button_3.configure(fg_color = "#395E9C")

            self.back_to_normal(self.button_2)

        self.valid_run = True
        self.activeThread = False