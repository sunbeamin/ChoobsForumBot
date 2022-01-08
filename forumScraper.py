import sys
from bs4 import BeautifulSoup
import urllib.request

class returnObject:
    def __init__(self, forumURL = None, forumPost = None, username = None, timestamp = None):
      self.forumURL = forumURL
      self.forumPost = forumPost
      self.username = username
      self.timestamp = timestamp

def getLatestForumPost():

    forumData = returnObject()

    # Get the HTML of the Iron Choobs forum page
    forumURL = 'https://secure.runescape.com/m=forum/c=zaAuPnMkWRg/forums?320,321,155,66237297,goto,'
    try:
        req = urllib.request.Request(url=forumURL, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req).read()
    except urllib.error.HTTPError as e:
        print("Caught HTTP Error: ", e.__dict__)
        return forumData
    except urllib.error.URLError as e:
        print("Caught URL Error: ", e.__dict__)
        return forumData

    soup = BeautifulSoup(html, features="html.parser")

    # Retrieve the latest page on the forum from the bottom pagination boxes
    maxPaginationNumber = soup.find('input',class_="paginationWrap__number text")["max"]

    # Concatenate the last page number to the original URL
    forumLastPageURL = forumURL + maxPaginationNumber
    
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

    soup = BeautifulSoup(html, features="html.parser")

    # Find the timestamp of the latest entry on the latest page 
    latestReplyTimestamp = soup.findAll('p', class_="forum-post__time-below")[-1].get_text()
    with open(r"PostTimestamp.txt", "r") as fp:
        latestReplySaved = fp.read()

    #Check if the timestamp matches that of the previously fetched latest message
    #If these do not match, it means a new message has been posted. Save the new timestamp
    if(latestReplyTimestamp != latestReplySaved):

        with open(r"PostTimestamp.txt", "w+") as fp:
            fp.write(latestReplyTimestamp)
            fp.close()

        #Set our object variables, these stay as None otherwise
        forumData.forumURL = forumLastPageURL
        forumData.timestamp = latestReplyTimestamp
        forumData.username = soup.findAll('a', class_="post-avatar__name-link")[-1].get_text()

        #Init the forumPost var as string so we can append our post body to it
        forumData.forumPost = ""
        for string in soup.findAll('span', class_="forum-post__body")[-1].strings:
            forumData.forumPost = f"{forumData.forumPost}\n {string}"
            
    return forumData
