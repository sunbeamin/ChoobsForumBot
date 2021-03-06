import sys
import os
from bs4 import BeautifulSoup
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TimestampPath = os.path.join(BASE_DIR, "PostTimestamp.txt")

class returnObject:
    def __init__(self, forumURL = None, forumPost = None, username = None, timestamp = None):
      self.forumURL = forumURL
      self.forumPost = forumPost
      self.username = username
      self.timestamp = timestamp

def getLatestForumPost():

    forumData = returnObject()

    # Get the HTML of the Iron Choobs forum page
    forumURL = 'https://secure.runescape.com/m=forum/forums?320,321,158,66243056,goto,'
    baseForumURL = 'https://secure.runescape.com/m=forum/forums'
    
    try:
        req = urllib.request.Request(url=forumURL, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req).read()
    except urllib.error.HTTPError as e:
        print("Caught HTTP Error: ", e.__dict__)
        return forumData
    except urllib.error.URLError as e:
        print("Caught URL Error: ", e.__dict__)
        return forumData
    except ConnectionResetError as e:
        print("Caught URL Error: ", e.__dict__)
        return forumData

    soup = BeautifulSoup(html, features="html.parser")

    # Retrieve the latest page on the forum from the bottom pagination boxes
    pageNumbers = soup.find(class_="pageNumbers")
    maxPaginationNumber = pageNumbers.findAll("a")[-1]


    # Concatenate the href of the last page to the base URL
    forumLastPageURL = baseForumURL + maxPaginationNumber['href']
    
    #Get the HTML of the last page on the forum
    try:
        req = urllib.request.Request(url=forumLastPageURL, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req).read()
    except urllib.error.HTTPError as e:
        print("Caught HTTP Error: ", e.__dict__)
        return forumData
    except urllib.error.URLError as e:
        print("Caught URL Error: ", e.__dict__)
        return forumData
    except ConnectionResetError as e:
        print("Caught URL Error: ", e.__dict__)
        return forumData

    soup = BeautifulSoup(html, features="html.parser")

    # Find the timestamp of the latest entry on the latest page 
    latestReplyTimestamp = soup.findAll('p', class_="forum-post__time-below")[-1].get_text()
    with open(TimestampPath, "r") as fp:
        latestReplySaved = fp.read()

    #Check if the timestamp matches that of the previously fetched latest message
    #If these do not match, it means a new message has been posted. Save the new timestamp
    if(latestReplyTimestamp != latestReplySaved):

        with open(TimestampPath, "w+") as fp:
            fp.write(latestReplyTimestamp)
            fp.close()

        #Set our object variables, these stay as None otherwise
        forumData.forumURL = forumLastPageURL
        forumData.timestamp = latestReplyTimestamp
        forumData.username = soup.findAll('a', class_="post-avatar__name-link")[-1].get_text()

        #Init the forumPost var as string so we can append our post body to it
        forumData.forumPost = ""
        for string in soup.findAll('span', class_="forum-post__body")[-1].strings:
            forumData.forumPost = f"{forumData.forumPost}\n{string}"
            
    return forumData

