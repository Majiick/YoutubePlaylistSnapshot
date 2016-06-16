#!/usr/bin/python

import os
import zipfile
import argparse
import codecs
import datetime
import sys
from apiclient.discovery import build

DEVELOPER_KEY = "REPLACE_THIS_WITH_YOUR_OWN_API_KEY"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
RESULTS_PER_PAGE = 50 #1-50 as per Google's rules.
MAX_PLAYLIST_SIZE = 5000

def getArgs():
    parser = argparse.ArgumentParser(description='Retrieve a list of youtube videos in a playlist.')
    parser.add_argument("id", type=str, metavar="id", help="Youtube ID of the playlist to scrap.")
    parser.add_argument('-dt', '--date', action='store_true', help="Include the date when the video was added to the playlist?")
    parser.add_argument('-ds', '--description', action='store_true', help="Include the description of videos?")
    parser.add_argument('-un', '--uploadername', action='store_true', help="Include the channel name of the uploader of video?")

    args = parser.parse_args()
    args = vars(args) #Turn into dict-like view.
    return args

def getExtraFields(args):
    """
    Returns a string of what information to filter in the Google API based on args optional parameters.
    """
    extraFields = ""
    
    if args["description"]:
        extraFields += ",description"

    if args["date"]:
        extraFields += ",publishedAt"

    if args["uploadername"]:
        extraFields += ",resourceId(videoId)"

    return extraFields

def getExtraInfo(args, item):
    """
    Returns a string of what information to save with the video name based on args optional parameters.
    """
    extraInfo = ""
    
    if args["uploadername"]:
        extraInfo += " |Uploader: {}|".format(item["snippet"]["resourceId"]["uploader"])
    
    if args["date"]:
        extraInfo += " |Date Added: {}|".format(item["snippet"]["publishedAt"][:-5]) #-5 to remove 000Z

    if args["description"]:
        extraInfo += " |Description: {}|".format(item["snippet"]["description"])

    return extraInfo

def save(pages, fileName, args):
    """
    Saves selected playlistItems' information in a txt. 
    """
    f = codecs.open(fileName, "wb", "utf-8")
    
    i = 0
    for playlistItems in pages:
        for items in playlistItems["items"]:
            i = i + 1
            f.write("{}.".format(i) + str(items["snippet"]["title"]) + getExtraInfo(args, items) + u'\r\n')

    f.close()


def setChannelNames(pages):
    """
    Retrieves all the videos in pages and gets the uploader's name.
    Sets the uploader's name to the playlistItem's ["snippet"]["resourceId"]["uploader"].
    """
    #videoIds = [item["snippet"]["resourceId"]["videoId"] for playlistItem in pages for item in playlistItem["items"]]
    videoIds = []
    for playlistItems in pages:
        for items in playlistItems["items"]:
            videoIds.append(items["snippet"]["resourceId"]["videoId"])
    
    for i in range(1, playlistItems["pageInfo"]["totalResults"]):
        videoIdsString = ""
        if i % RESULTS_PER_PAGE == 0 or i == playlistItems["pageInfo"]["totalResults"] - 1: #Every 50 or on the last iteration.
            for id in videoIds[:RESULTS_PER_PAGE]: #Generate the string of ids to put into the API request.
                videoIdsString += "{},".format(id)
                
            videoIdsString = videoIdsString[:-1] #Remove last ','
            videoIds = videoIds[RESULTS_PER_PAGE:]
            
            videos = youtube.videos().list(
                                        part="snippet",
                                        id=videoIdsString,
                                        fields="items(snippet(channelTitle))",
                                        maxResults=RESULTS_PER_PAGE
                                    ).execute()

            #Associate the channelTitles with their respective videos.
            j = 0
            for items in pages[int((i - 1) / 50)]["items"]:
                if j > len(videos["items"]) - 1:
                    print(j)
                    break
                
                items["snippet"]["resourceId"]["uploader"] = videos["items"][j]["snippet"]["channelTitle"]
                j+=1
                                
if __name__ == "__main__":
    if DEVELOPER_KEY == "REPLACE_THIS_WITH_YOUR_OWN_API_KEY":
        print("You must first enter your own Youtube Data API developer key. Check for more info: https://github.com/Majiick/YoutubePlaylistSnapshot/blob/master/README.md#usage")
        sys.exit()

    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
    args = getArgs()
    extraFields = getExtraFields(args)
    

    pages = []
    nextPageToken = ""
    while True: #Get all the playListItems
        playlistItems = youtube.playlistItems().list(
            part="snippet", #What part to return.
            maxResults=RESULTS_PER_PAGE,
            playlistId=args["id"],
            pageToken=nextPageToken,
            fields="nextPageToken,pageInfo,items(snippet(title{0}))".format(extraFields) #Filters down returned information to only these fields.
        ).execute()

        if playlistItems["pageInfo"]["totalResults"] > MAX_PLAYLIST_SIZE:
            print("Playlist is too large. Edit MAX_PLAYLIST_SIZE to a higher value.")
            sys.exit()

        pages.append(playlistItems)

        if "nextPageToken" in playlistItems:
            nextPageToken = playlistItems["nextPageToken"]
        else:
            break

    if args["uploadername"]:
        setChannelNames(pages)


    playlistName = youtube.playlists().list(part="snippet", id=args["id"], fields="items(snippet(title))").execute()["items"][0]["snippet"]["title"]
    save(pages, "{} {}.txt".format(playlistName, datetime.datetime.today().strftime('%d-%m-%Y')), args)
