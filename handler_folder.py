import tkinter
import tkinter.messagebox
import customtkinter
import threading

import os
import json
import shutil

from tweet_analysis import Analyzer

##########################################################
##########################################################
##########################################################

class FolderHandler(object):

    def __init__(self, other_self):
        self.analyzer = Analyzer()
        
        self.other_self = other_self

        self.base_path = os.path.join(os.getcwd(), "data_files")
        self.cur_path = self.base_path

        self.lookUp = self.make_directory_data_structure(self.base_path)
        self.cur_lookUp = self.lookUp

        self.cur_file_tweets = []
        self.cur_file_name = ""
        self.dctTweets = {}

        self.dctClusters = {}

        self.past_threads = []

    def updateDirectory(self):
        self.lookUp = self.make_directory_data_structure(self.base_path)
        if ".json" not in self.cur_path:
            self.cur_lookUp = self.findFolder(self.lookUp, self.cur_path)
        else:
            self.cur_lookUp = self.findFolder(self.lookUp, self.cur_path.replace("/" + self.cur_file_name, ""))
        
    # ============ underlying engines ============

    def make_directory_data_structure(self, dir):
        lstContents = os.listdir(dir)
        lstUseless = ['.DS_Store', "__pycache__"]
        lstReturn = []
        for file in lstContents:
            if file not in lstUseless:
                if "." not in file:
                    new_path = os.path.join(dir, file)
                    lstReturn += [self.make_directory_data_structure(new_path)]
                else:
                    lstReturn += [file]
        return {dir : lstReturn}
    
    def clickFolder(self, folder):
        new_path = os.path.join(self.cur_path, folder)
        for elems in self.cur_lookUp[self.cur_path]:
            if type(elems) == dict and new_path == list(elems.keys())[0]:
                self.cur_lookUp = elems
                self.cur_path = new_path

                self.frame_folders.destroy()
                self.make_analysis_frame()

                if self.cur_path != self.base_path:
                    self.button_5.configure(state = tkinter.NORMAL)

                break

    def findFolder(self, curDct, folder):
        cur_folder = list(curDct.keys())[0]
        if folder == cur_folder:
            return curDct
        
        for elem in curDct[cur_folder]:
            if type(elem) == dict:
                output_dct = self.findFolder(elem, folder)
                if output_dct: return output_dct

        return None

    def goToParrent(self):
        old_path = self.cur_path.split("/")
        old_path = "/".join(old_path[:len(old_path)-1])
        if len(old_path) >= len(self.base_path):
            self.cur_lookUp = self.findFolder(self.lookUp, old_path)
            self.cur_path = old_path

            self.frame_folders.destroy()
            self.make_analysis_frame()

    def clicked_on(self, button):
        button.configure(fg_color = "#243b61")
        button.configure(state = tkinter.DISABLED)

    def back_to_normal(self, button):
        button.configure(fg_color = "#395E9C")
        button.configure(state = tkinter.NORMAL)

    def make_folder_file(self, lstTweets, file_name):
        path_location = (self.cur_path).replace("/" + self.cur_file_name, "")
        self.make_folder(path_location, file_name)
        self.make_file(os.path.join(path_location, file_name), lstTweets, file_name)
        self.updateDirectory()

    def make_folder(self, path, folder_name):
        os.makedirs(os.path.join(path, folder_name))
    
    def make_file(self, path, lstTweets, file_name):
        f = open(os.path.join(path, file_name + ".json"), "w")
        j = json.dumps(lstTweets)
        f.write(j)
        f.close()

    def clear_folders(self):
        trueDir = self.cur_path
        if "." in self.cur_path.split("/")[-1]:
            trueDir = "/".join(trueDir.split("/")[:-1])
        for elem in os.listdir(trueDir):
            if "." not in elem:
                shutil.rmtree(os.path.join(trueDir, elem))
        
        self.updateDirectory()
        if trueDir == self.cur_path:
            self.make_analysis_frame()

    # ============ opening .json files ============
    def openFile(self, file_name):
        self.cur_file_name = file_name

        if file_name in self.dctTweets:
            new_path = os.path.join(self.cur_path, file_name)
            self.cur_path = new_path
            self.cur_file_tweets = self.dctTweets[file_name]

            self.frame_folders.destroy()
            self.make_file_frame()

            self.tweet_index = 0
            self.changeTweet()

        elif ".json" in file_name:
            new_path = os.path.join(self.cur_path, file_name)
            self.cur_path = new_path
            f = open(new_path, "r")

            self.cur_file_tweets = []
            if "raw" in file_name:
                for line in f:
                    tweet = json.loads(line)
                    self.cur_file_tweets += [[tweet["tweet"],
                                        tweet["username"],
                                        tweet["replies_count"],
                                        tweet["retweets_count"],
                                        tweet["likes_count"]]]
            elif "tweets_" in file_name:
                self.cur_file_tweets = json.load(f)

            self.dctTweets[file_name] = self.cur_file_tweets

            self.frame_folders.destroy()
            self.make_file_frame()

            self.tweet_index = 0
            self.changeTweet()
    
    def last_tweet(self):
        if self.tweet_index == 0:   self.tweet_index = len(self.cur_file_tweets) - 1
        else:
            self.tweet_index += -1
        
        self.changeTweet()

    def next_tweet(self):
        if self.tweet_index == len(self.cur_file_tweets) - 1:   self.tweet_index = 0
        else:
            self.tweet_index += 1
        self.changeTweet()

    def changeTweet(self):
        tweet = self.cur_file_tweets[self.tweet_index]
        self.label_tweets.set_text(f"{tweet[0]}\n\nUser: {tweet[1]}\nReplies: {tweet[2]} Retweets: {tweet[3]} Likes: {tweet[4]} ")
        self.label_tweets.set_dimensions(150, 120)

    def sentimentAnalysis(self):
        old_dir = self.cur_path
        sentiment_lst = self.analyzer.get_sentiment(self.cur_file_tweets, self.cur_file_name)
        if self.cur_path == old_dir:
            self.label_s_neg.configure(state=tkinter.NORMAL)
            self.label_s_neu.configure(state=tkinter.NORMAL)
            self.label_s_pos.configure(state=tkinter.NORMAL)

            self.label_s_neg.tag_configure("center", justify='center')
            self.label_s_neg.insert("1.0", f"Negative\n{sentiment_lst[0]}", "center")

            self.label_s_neu.tag_configure("center", justify='center')
            self.label_s_neu.insert("1.0", f"Neutral\n{sentiment_lst[1]}", "center")

            self.label_s_pos.tag_configure("center", justify='center')
            self.label_s_pos.insert("1.0", f"Positive\n{sentiment_lst[2]}", "center")

            self.label_s_neg.configure(state=tkinter.DISABLED)
            self.label_s_neu.configure(state=tkinter.DISABLED)
            self.label_s_pos.configure(state=tkinter.DISABLED)

    def runSentiment(self):
        self.clicked_on(self.button_4)

        if self.cur_file_name not in self.past_threads:
            if threading.active_count() >= 4:
                pass
            else:
                threading.Thread(target = self.sentimentAnalysis).start()
                self.past_threads += [self.cur_file_name]
        elif self.cur_file_name in self.analyzer.dctSentiment:
            self.sentimentAnalysis()

    def runClustering(self):
        self.clicked_on(self.button_3)
        if not self.has_folders():
            if threading.active_count() >= 4:
                pass
            else:
                threading.Thread(target = self.find_subtopics).start()
        else:
            self.clear_folders()
            threading.Thread(target = self.find_subtopics).start()

    def find_subtopics(self):
        old_dir = self.cur_path
        
        k_means_output = self.analyzer.clustering(self.cur_file_tweets, self.cur_file_name)
        str_output = k_means_output[0]
        group_labels = k_means_output[1]
        
        if self.cur_path == old_dir:
            self.textbox_clustering.insert("1.0", str_output)
            
        self.dctClusters[old_dir] = str_output

        dctOrg = {}
        index = 0
        for label in group_labels:
            if label in dctOrg:
                dctOrg[label] += [self.cur_file_tweets[index]]
            else:
                dctOrg[label] = [self.cur_file_tweets[index]]
            index += 1
        for key in set(group_labels):
            total = len(dctOrg[key])
            self.make_folder_file(dctOrg[key], f"tweets_{key}_{total}")

    def has_folders(self):
        for elem in self.cur_lookUp[self.cur_path.replace("/" + self.cur_file_name, "")]:
            if "." not in elem: return True
        return False

    def make_file_frame(self):
        self.frame_folders = customtkinter.CTkFrame(master=self.other_self)
        self.frame_folders.grid(row=0, column=1, pady=10, padx=10, sticky = "nsew")

        # configure grid layout (3x7)
        self.frame_folders.rowconfigure((0, 1, 2, 3), weight=1)
        self.frame_folders.rowconfigure(7, weight=10)
        self.frame_folders.columnconfigure((0, 1), weight=1)
        self.frame_folders.columnconfigure(2, weight=0)

        self.label_tweets = customtkinter.CTkLabel(master=self.frame_folders,
                                                   text="",
                                                   height = 120,
                                                   width = 150,
                                                   fg_color=("white", "gray38"),
                                                   corner_radius = 10,
                                                   wraplength = 400,)
        self.label_tweets.grid(row=0, column=0, rowspan = 2, columnspan=2, pady = 5, padx = 5, sticky = "news")

        self.button_1 = customtkinter.CTkButton(master=self.frame_folders,
                                                text="<",
                                                height = 55,
                                                width = 30,
                                                command=self.last_tweet)
        self.button_1.grid(row=0, column=2, pady = 5, padx = 5, sticky = "ew")

        self.button_2 = customtkinter.CTkButton(master=self.frame_folders,
                                                text=">",
                                                height = 55,
                                                width = 30,
                                                command=self.next_tweet)
        self.button_2.grid(row=1, column=2, pady = 5, padx = 5, sticky = "ew")

        self.button_3 = customtkinter.CTkButton(master=self.frame_folders,
                                                text="Clustering",
                                                height = 30,
                                                width = 60,
                                                command=self.runClustering)
        self.button_3.grid(row=3, column=0, pady = 5, padx=5, sticky = "nsew")

        self.button_4 = customtkinter.CTkButton(master=self.frame_folders,
                                                text="Sentiment Analysis",
                                                height = 50,
                                                width = 60,
                                                command=self.runSentiment)
        self.button_4.grid(row=2, column=0, pady = 5, padx=5, sticky = "ew")

        self.textbox_clustering= customtkinter.CTkTextbox(master=self.frame_folders,
                                                   width = 200,
                                                   corner_radius = 10,
                                                   fg_color=("white", "gray38"))
        self.textbox_clustering.grid(row=3, column=1, columnspan = 1, rowspan = 5, pady=5, padx=5, sticky = 'news')

        if self.cur_path in self.dctClusters and self.has_folders():
            self.textbox_clustering.insert("1.0", self.dctClusters[self.cur_path])

        self.frame_sentiment = customtkinter.CTkFrame(master=self.frame_folders,
                                                        height = 40,
                                                        width = 100)
        self.frame_sentiment.grid(row=2, column=1, columnspan=1, rowspan=1, pady=5, padx=5, sticky="nsew")
        self.frame_sentiment.rowconfigure(0, weight=1)
        self.frame_sentiment.columnconfigure((0, 1, 2), weight=1)

        self.label_s_neg= customtkinter.CTkTextbox(master=self.frame_sentiment,
                                                   corner_radius = 10,
                                                   width = 50,
                                                   height = 50,
                                                   fg_color=("white", "gray38"))
        self.label_s_neg.grid(row=0, column=0, padx = 2, pady=5, sticky = "news")

        self.label_s_neu= customtkinter.CTkTextbox(master=self.frame_sentiment,
                                                   corner_radius = 10,
                                                   width = 50,
                                                   height = 50,
                                                   fg_color=("white", "gray38"))
        self.label_s_neu.grid(row=0, column=1, padx = 2, pady=5, sticky = "news")

        self.label_s_pos= customtkinter.CTkTextbox(master=self.frame_sentiment,
                                                   corner_radius = 10,
                                                   width = 50,
                                                height = 50,
                                                   fg_color=("white", "gray38"))
        self.label_s_pos.grid(row=0, column=2, padx = 2, pady=5, sticky = "news")

        self.label_s_neg.configure(state=tkinter.DISABLED)
        self.label_s_neu.configure(state=tkinter.DISABLED)
        self.label_s_pos.configure(state=tkinter.DISABLED)

        self.textbox_word_freq = customtkinter.CTkTextbox(master=self.frame_folders,
                                                   height = 240,
                                                   width = 175,
                                                   corner_radius = 10,
                                                   fg_color=("white", "gray38"))
        self.textbox_word_freq.grid(row=2, column=2, rowspan = 6, pady=5, padx=5, sticky = "news")
        self.textbox_word_freq.tag_configure("center", justify='center')
        self.textbox_word_freq.insert("1.0", self.analyzer.get_word_frequency(self.cur_file_tweets), "center")
        self.textbox_word_freq.configure(state = tkinter.DISABLED)

        self.button_5 = customtkinter.CTkButton(master=self.frame_folders,
                                                text="Back",
                                                fg_color = "#5d6b70",
                                                hover_color = "#353d40",
                                                height = 40,
                                                command=self.back_button)
        self.button_5.grid(row=8, column=2, pady=5, padx=5, sticky = "ew")
    
        if self.cur_file_name in self.past_threads:
            self.runSentiment()

    # ============ folder handler ============
    def display_folder(self, folder_name, x, y):
        folder_name = list(folder_name.keys())[0]
        folder_name = folder_name.split("/")[-1]
        temp_button = customtkinter.CTkButton(master=self.frame_folders,
                                                text=folder_name,
                                                fg_color = "#D35B58",
                                                hover_color = "#C77C78",
                                                width = 200,
                                                height = 40,
                                                command = lambda: self.clickFolder(folder_name))
        temp_button.grid(row=y, column=x, pady=5, padx=5)

    def display_file(self, file_name, x, y):
        temp_button = customtkinter.CTkButton(master=self.frame_folders,
                                                text=file_name,
                                                width = 200,
                                                height = 40,
                                                command = lambda: self.openFile(file_name))
        temp_button.grid(row=y, column=x, pady=5, padx=5)

    def back_button(self):
        self.goToParrent()
        if self.cur_path == self.base_path:
            self.button_5.configure(state = tkinter.DISABLED)

    def make_analysis_frame(self):
         # ============ frame_info ============
        self.frame_folders = customtkinter.CTkFrame(master=self.other_self)
        self.frame_folders.grid(row=0, column=1, sticky="nswe", padx=10, pady=10)

        short_path = self.cur_path.replace(self.base_path, "")
        if not short_path:  short_path = self.base_path
        self.label_1 = customtkinter.CTkLabel(master=self.frame_folders,
                                              text=short_path,
                                              text_font=("Roboto Medium", -12))  # font name and size in px
        self.label_1.grid(row=0, column=0, columnspan = 3, pady=5, padx=5)


        # configure grid layout (3x7)
        self.frame_folders.rowconfigure((0, 1, 2, 3), weight=1)
        self.frame_folders.rowconfigure(7, weight=10)
        self.frame_folders.columnconfigure((0, 1), weight=1)
        self.frame_folders.columnconfigure(2, weight=0)

        index = 3
        for elem in self.cur_lookUp[self.cur_path]:
            x = index % 3
            y = index // 3

            if index == 23: index += 1
            if index == 26: break
                
            if "." in elem:
                self.display_file(elem, x, y)
            else:
                self.display_folder(elem, x, y)
            
            index += 1

        self.button_5 = customtkinter.CTkButton(master=self.frame_folders,
                                                text="Back",
                                                fg_color = "#5d6b70",
                                                hover_color = "#353d40",
                                                height = 40,
                                                command=self.back_button)
        self.button_5.grid(row=8, column=2, pady=5, padx=5, sticky = "swe")

        self.button_6 = customtkinter.CTkButton(master=self.frame_folders,
                                                text="Clear Folders",
                                                fg_color = "#5d6b70",
                                                hover_color = "#353d40",
                                                height = 40,
                                                command=self.clear_folders)
        self.button_6.grid(row=7, column=2, pady=5, padx=5, sticky = "swe")

        if self.cur_path == self.base_path:
            self.button_5.configure(state = tkinter.DISABLED)


##########################################################
##########################################################
##########################################################