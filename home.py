import re

from os import listdir
from upload_video import UploadVideo


VIDEOS_FOLDER = "/home/pi/Youtube/Outbox/"


videos_list = listdir(VIDEOS_FOLDER)[::-1]

video = {'file': '', 'title': '', 'description': '', 'keywords': '', 'category': 22}


for i in range(0, len(videos_list)):
  video['description'] = videos_list[i]
  video['file'] = VIDEOS_FOLDER + video['description']

  # Find season
  video_season = re.search('(?<=s|S)\d{1,2}', video['description']).group(0)
  video_season = int(video_season) + 100
  video_season = str(video_season)[1:3]

  # Find episode
  video_episode = re.search('(?<=e|E|p|P)\d{1,2}', video['description']).group(0)
  video_episode = int(video_episode) + 100
  video_episode = str(video_episode)[1:3]

  # Change dots to spaces
  video['title'] = video['description'][:-4].replace('.',' ') + video['description'][-4:]
  video['title'] = re.search('[^(s)|(S)\d{1,2}]*', video['title']).group(0)
  video['title'] = video['title'] + "S" + video_season + "E" + video_episode


  upload_video1 = UploadVideo()
  upload_video1.upload_video_to_youtube(video)
