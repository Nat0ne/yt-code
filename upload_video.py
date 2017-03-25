### =============================================
###  MODULE: UploadVideo
###  DESCRIPTION: Upload video to Youtube
###  VERSION: 2.0
###  INITIAL VERSION DESIGNER: Youtube
###  EXTENTION DESIGNER: Antonio Eleuterio
###  DATE: 20-03-2017
### =============================================

import httplib
import httplib2
import os
import random
import sys
import time

from argparse import Namespace
from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow


class UploadVideo():
  AUTH_FOLDER = "../Auth/"
  httplib2.RETRIES = 1
  VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")

  PARAMETERS_DEFAULT = {'MAX_RETRIES': 10,
                        'RETRIABLE_EXCEPTIONS': (httplib2.HttpLib2Error, 
                                                 IOError, 
                                                 httplib.NotConnected,
                                                 httplib.IncompleteRead,
                                                 httplib.ImproperConnectionState,
                                                 httplib.CannotSendRequest,
                                                 httplib.CannotSendHeader,
                                                 httplib.ResponseNotReady,
                                                 httplib.BadStatusLine),
                        'RETRIABLE_STATUS_CODES': [500, 502, 503, 504],
                        'OAuth_folders': {'CLIENT_SECRETS_FILE': AUTH_FOLDER + "client_secrets.json",
                                          'OAUTH_FILE': AUTH_FOLDER + "oauth2.json"
                                         },
                        'Youtube_properties': {'YOUTUBE_UPLOAD_SCOPE': "https://www.googleapis.com/auth/youtube.upload",
                                               'YOUTUBE_API_SERVICE_NAME': "youtube",
                                               'YOUTUBE_API_VERSION': "v3"
                                              },
                        'MISSING_CLIENT_SECRETS_MESSAGE': "Client Secrests file missing"
                       }

  PARAMETERS = {}
  

  def __init__(self, parameters = PARAMETERS_DEFAULT):
    self.PARAMETERS = parameters


  def upload_video_to_youtube(self, video):
    args = self._create_namespace_args(video)
    youtube = self._get_authenticated_service(args)

    try:
      self._initialize_upload(youtube, args)
    except HttpError, e:
      print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)


  def _create_namespace_args(self, video):
    return Namespace(auth_host_name = 'localhost', 
                     auth_host_port = [8080, 8090], 
                     category = video['category'], 
                     description = video['description'], 
                     file = video['file'],
                     keywords = video['keywords'], 
                     logging_level = 'ERROR',
                     noauth_local_webserver = False, 
                     privacyStatus = 'private', 
                     title = video['title']
                    )


  def _get_authenticated_service(self, args):
    flow = flow_from_clientsecrets(self.PARAMETERS['OAuth_folders']['CLIENT_SECRETS_FILE'],
      scope = self.PARAMETERS['Youtube_properties']['YOUTUBE_UPLOAD_SCOPE'],
      message = self.PARAMETERS['MISSING_CLIENT_SECRETS_MESSAGE'])

    storage = Storage(self.PARAMETERS['OAuth_folders']['OAUTH_FILE'])
    credentials = storage.get()

    if credentials is None or credentials.invalid:
      credentials = run_flow(flow, storage, args)

    return build(self.PARAMETERS['Youtube_properties']['YOUTUBE_API_SERVICE_NAME'], 
                 self.PARAMETERS['Youtube_properties']['YOUTUBE_API_VERSION'],
                 http=credentials.authorize(httplib2.Http()))


  def _initialize_upload(self, youtube, options):
    tags = None
    if options.keywords:
      tags = options.keywords.split(",")

    body=dict(
      snippet=dict(
        title=options.title,
        description=options.description,
        tags=tags,
        categoryId=options.category
      ),
      status=dict(privacyStatus=options.privacyStatus)
    )

    insert_request = youtube.videos().insert(
      part=",".join(body.keys()),
      body=body,
      media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True)
    )

    self._resumable_upload(insert_request)


  # This method implements an exponential backoff strategy to resume a failed upload.
  def _resumable_upload(self, insert_request):
    response = None
    error = None
    retry = 0    
    while response is None:
      try:
        print "Uploading file..."
        status, response = insert_request.next_chunk()
        if response is not None:
          if 'id' in response:
            print "Video id '%s' was successfully uploaded." % response['id']
          else:
            exit("The upload failed with an unexpected response: %s" % response)
      except HttpError, e:
        if e.resp.status in self.PARAMETERS['RETRIABLE_STATUS_CODES']:
          error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
                                                              e.content)
        else:
          raise
      except self.PARAMETERS['RETRIABLE_EXCEPTIONS'], e:
        error = "A retriable error occurred: %s" % e

      if error is not None:
        print error
        retry += 1
        if retry > self.PARAMETERS['MAX_RETRIES']:
          exit("No longer attempting to retry.")

        max_sleep = 2 ** retry
        sleep_seconds = random.random() * max_sleep
        print "Sleeping %f seconds and then retrying..." % sleep_seconds
        time.sleep(sleep_seconds)

