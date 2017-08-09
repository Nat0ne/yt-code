import re

from os import listdir
from upload_video import UploadVideo


VIDEOS_FOLDER = "/media/pi/Windows8_OS/TRANSACTIONS/torrent_complete/"


videos_list = sorted(listdir(VIDEOS_FOLDER))

video = {'file': '', 'title': '', 'description': '', 'keywords': '', 'category': 22}


for i in range(0, len(videos_list)):
  video['description'] = videos_list[i]
  video['file'] = VIDEOS_FOLDER + video['description']

  # Change dots to spaces
  video['title'] = video['description'][:-4].replace('.',' ') + video['description'][-4:]

  # Find season
  video_season = re.search('(?<=s|S)\d{1,2}', video['description'])

  # Find episode
  video_episode = re.search('(?<=e|E|p|P)\d{1,2}', video['description'])


  if video_season and video_episode:   # It is a series
    video_season = int(video_season.group(0)) + 100
    video_season = str(video_season)[1:3]

    video_episode = int(video_episode.group(0)) + 100
    video_episode = str(video_episode)[1:3]

    video['title'] = re.search('([\w\s,-]+)\s(s|S)\d{1,2}', video['title']).group(1)
    video['title'] = video['title'] + " S" + video_season + "E" + video_episode

    print "Series"

  else: # it is a movie
    print "Movie"
  
  print "%s\n" % video

  upload_video1 = UploadVideo()
  upload_video1.upload_video_to_youtube(video)
