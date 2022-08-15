import twint

import time
import json
import os
import shutil

##########################################################
##########################################################
##########################################################

class TweetFetcher(object):

    def __init__(self, output_file):
        og_base_path = os.getcwd()
        data_dir = os.path.join(og_base_path, "data_files")
        if not os.path.isdir(data_dir):
            os.mkdir(data_dir)
        os.chdir(data_dir)

        self.output_file = output_file
        self.raw_output_file = "tweets_raw"
        self.base_path = os.getcwd()

        self.start_time = time.time()
        self.total_time = 0
        
        self.config = twint.Config()

        self.cleanPastFiles()

    def cleanPastFiles(self):
        tempPath = self.base_path + "/" + self.raw_output_file
        index = 1
        while os.path.exists(tempPath + f"_{index}.json"):
            os.remove(tempPath + f"_{index}.json")
            index += 1
        
        tempPath = self.base_path + "/" + self.output_file.replace("tweets_", "")
        if os.path.exists(tempPath):
            shutil.rmtree(tempPath)
        
    def searchOnce(self, keyword, numTweets, outputNum):
        self.start_time = time.time()
        config = self.config
        config.Search = keyword

        config.Lang = "en"
        config.Limit = numTweets
        #config.Since = "2022-06-01"
        #config.Until = "2022-06-30"

        config.Hide_output = True

        config.Store_json = True
        config.Output = self.raw_output_file + f"_{outputNum}.json"

        #running search
        twint.run.Search(config)

        self.total_time = round(time.time() - self.start_time, 2)
        self.start_time = time.time()

    def search(self, lstKeywords, numTweets):
        count = 1
        for keyword in lstKeywords:
            self.searchOnce(keyword, numTweets, count)
            count += 1
        return self.base_path

##########################################################
##########################################################
##########################################################