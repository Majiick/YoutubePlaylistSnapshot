# Description
Tired of seeing and not knowing which video got removed?
![I know this breaks your heart.](http://i.imgur.com/OalHqgO.png)

No worries, **YoutubePlaylistSnapshot.py** will save all of your playlist videos in a text file so you will know which one(s) was removed from YouTube.

### Usage
**Before using**, you have to open up the script and enter your own Google API key in place of DEVELOPER_KEY = "REPLACE_THIS_WITH_YOUR_OWN_API_KEY"

You can follow [the steps here to get your own key.](https://developers.google.com/youtube/v3/getting-started#before-you-start)

Do "*YoutubePlaylistSnapshot.py -h*" for help.
  
### Example Usage
Say you want to take a snapshot of this playlist: https://www.youtube.com/watch?v=fRh_vgS2dFE&list=PLDcnymzs18LVXfO_x0Ei0R24qDbVtyy66

And we also want to save each video uploader's name and the date of when the video was added to the playlist:

*YoutubePlaylistSnapshot.py -dt -un PLDcnymzs18LVXfO_x0Ei0R24qDbVtyy66*