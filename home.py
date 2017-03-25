import re

from os import listdir
from upload_video import UploadVideo


VIDEOS_FOLDER = "~/Youtube/Outbox/"


videos_list = listdir(VIDEOS_FOLDER)


video = {'file': 'title': '', 'description': '', 'season': 0, 'episode': 0, 'keywords': '', 'category': 22}


video['description'] = "Breaking.Bad.s2Ep4.mkv"
video['file'] = VIDEOS_FOLDER + video['description']

# Change dots to spaces
video['title'] = video['description'][:-4].replace('.',' ') + video['description'][-4:]

# Find season
video['season'] = re.search('(?<=s|S)\d{1,2}', video['title']).group(0)
video['season'] = int(video['season']) + 100
video['season'] = str(video['season'])[1:3]

# Find episode
video['episode'] = re.search('(?<=e|E|p|P)\d{1,2}', video['title']).group(0)
video['episode'] = int(video['episode']) + 100
video['episode'] = str(video['episode'])[1:3]


upload_video1 = UploadVideo()

upload_video1.upload_video_to_youtube(video)

