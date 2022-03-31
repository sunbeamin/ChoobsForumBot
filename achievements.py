import json
import requests
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TimestampPath = os.path.join(BASE_DIR, "AchievementTimestamp.txt")

class returnObject:
    def __init__(self, user = None, metric = None, measure = None, name = None, timestamp = None):
      self.user = user
      self.metric = metric
      self.measure = measure
      self.name = name
      self.timestamp = timestamp

def getLatestAchievement():
    achievementData = returnObject()
    
    #Get the latest achievement from the wiseoldman API, parse to JSON 
    try:
        response = requests.get("https://api.wiseoldman.net/groups/2303/achievements?limit=1").json()[0]
    except Exception as e:
        return achievementData

    #We get a list with the JSON contents, only of size 1 so just index the first entry for our JSON result
    latestReplyTimestamp = response['createdAt']
    player = response['player']
    with open(TimestampPath, "r") as fp:
        latestReplySaved = fp.read()

    #Check if the timestamp matches that of the previously posted latest achievement
    #If these do not match, it means a new achievement has been reached. Save the new timestamp
    if(latestReplyTimestamp != latestReplySaved):
        with open(TimestampPath, "w+") as fp:
            fp.write(latestReplyTimestamp)
            fp.close()
            
        achievementData.user = player['displayName']
        achievementData.metric = response['metric']
        achievementData.name = response['name']
        achievementData.timestamp = latestReplyTimestamp
    
    return achievementData
