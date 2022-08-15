import time
import json
import os

##########################################################
##########################################################
##########################################################

class Filter(object):

    def __init__(self, output_file):
        self.output_file = output_file
        self.raw_output_file = "tweets_raw"
        self.base_path = os.getcwd()

    def cleanEnglish(self):
        filtered_tweets = []
        original_num_tweets = 0

        index = 1
        while os.path.exists(self.base_path + "/" + self.raw_output_file + f"_{index}.json"):
            file = os.path.join(self.base_path, self.raw_output_file + f"_{index}.json")
            f = open(file, "r")
            for line in f:
                original_num_tweets += 1
                tweet = json.loads(line)
                if tweet["language"] == "en" and tweet not in filtered_tweets:
                    filtered_tweets += [[tweet["tweet"],
                                        tweet["username"],
                                        tweet["replies_count"],
                                        tweet["retweets_count"],
                                        tweet["likes_count"]]]

            f.close()

            index += 1

        folder_name = self.output_file.replace("tweets_", "")
        folder_path = os.path.join(os.getcwd(), folder_name)
        os.makedirs(folder_path)

        f = open(os.path.join(folder_path, self.output_file + f".json"), "w")

        j = json.dumps(filtered_tweets)
        f.write(j)
        f.close()

        new_num_tweets = len(filtered_tweets)
        return f"{original_num_tweets} tweets successfully fetched \nOnly {new_num_tweets} tweets were in English"
        
