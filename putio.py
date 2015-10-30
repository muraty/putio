from client import Client


class Putio:

    def __init__(self, oauth_token=None, client_id=None):
        self.OAUTH_TOKEN = oauth_token
        self.CLIENT_ID = client_id

    @property
    def File(self):
        return File(self.OAUTH_TOKEN, self.CLIENT_ID)

    @property
    def Account(self):
        return Account(self.OAUTH_TOKEN, self.CLIENT_ID)

    @property
    def Transfer(self):
        return Transfer(self.OAUTH_TOKEN, self.CLIENT_ID)

    @property
    def Friend(self):
        return Friend(self.OAUTH_TOKEN, self.CLIENT_ID)

    @property
    def Event(self):
        return Event(self.OAUTH_TOKEN, self.CLIENT_ID)


class Resource:

    def __init__(self, oauth_token=None, client_id=None):
        self.OAUTH_TOKEN = oauth_token
        self.CLIENT_ID = client_id
        self.client = self._get_client()

    def _get_client(self):
        client = Client(oauth_token=self.OAUTH_TOKEN,
                        client_id=self.CLIENT_ID)
        return client

    def _call(self, action=None, method=None, params=None, data=None):
        url = self.BASE_URL
        return self.client.call(url, action=action, params=params, data=data,
                                method=method)


class File(Resource):

    def __init__(self, oauth_token=None, client_id=None):
        self.OAUTH_TOKEN = oauth_token
        self.CLIENT_ID = client_id
        self.BASE_URL = 'files/'
        self.client = self._get_client()

    def _download_file(self, response):
        filename = response.headers['Content-Disposition']

        seperator_pattern = '; filename='
        separator = filename.find(seperator_pattern)
        filename = filename[separator + len(seperator_pattern):]
        # If file name has spaces, it must have quotes around.
        filename = filename.strip('"')

        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()

    def _call(self, action=None, method=None, file_id=None, params=None,
              data=None, files=None, stream=False):
        url = self.BASE_URL
        if file_id is not None:
            url += str(file_id)
        return self.client.call(url, action=action, params=params, data=data,
                                method=method, files=files, stream=stream)

    def list_files(self):
        """Lists files in a folder."""
        response = self._call(action='list')
        return response.json()

    def search(self, query, page=1):
        """
        Searches your (and shared) files. Returns 50 results at a time.
        The url for next 50 results is given in the "next" paramater..

        Parameters:

        query:  The keyword to search.
        page:   Optional. Defaults to 1. If -1 given, returns all results
                at a time.

        Search Syntax:

        from:   me, shares, jack or all
        type:   video, audio, image, iphone or all
        ext:    mp3, avi, jpg, mp4 or all
        """
        action = 'search/%s/page/%s' % (query, page)
        response = self._call(action=action)
        return response.json()

    def upload(self, path, filename=None, parent_id=0):
        """
        Uploads a file. If the uploaded file is a torrent file,
        starts it as a transfer. This endpoint must be used with
        upload.put.io domain.
        """
        data = {'parent_id': parent_id}
        with open(path) as f:
            if filename:
                files = {'file': (filename, f)}
            else:
                files = {'file': f}
            response = self._call(action='upload', method='POST',
                                  files=files, data=data)
        return response.json()

    def create_folder(self, foldername, parent_id=0):
        """ Creates a new folder. """
        data = {'name': foldername,
                'parent_id': parent_id}
        response = self._call(action='create-folder', data=data,
                              method='POST')
        return response.json()

    def get_file_property(self, file_id):
        """ Returns a file's properties. """
        response = self._call(file_id=str(file_id))
        return response.json()

    def delete(self, file_ids):
        """ Deletes given files. """
        data = {'file_ids': file_ids}
        response = self._call(action='delete', method='POST', data=data)
        return response.json()

    def rename(self, file_id, name):
        """ Renames given file. """
        data = {'file_id': str(file_id),
                'name': name}
        response = self._call(action='rename', data=data, method='POST')
        return response.json()

    def move(self, file_ids, parent_id=0):
        """ Moves files to the given destination. """
        data = {'file_ids': file_ids,
                'parent_id': parent_id}
        response = self._call(action='move', data=data, method='POST')
        return response.json()

    def convert_to_mp4(self, file_id):
        """ Starts the conversion of the given file to mp4. """
        action = '%s/mp4' % file_id
        response = self._call(action=action, method='POST')
        return response.json()

    def get_mp4_status(self, file_id):
        """ Returns the status of mp4 conversion of the given file. """
        action = '%s/mp4' % file_id
        response = self._call(action=action)
        return response.json()

    def download(self, file_id):
        """
        Downloads the contents of the file. Only files can be downdloaded,
        For directories, you should use zip_and_download method.
        """
        action = '%s/download' % file_id
        response = self._call(action=action, stream=True)
        # Since this method can't be used for downloading folders,
        # see Zip-and-Download instead.
        self._download_file(response)

    def zip_and_download(self, file_ids):
        """
        Create zipstream for given files. A redirect to created zipstream
        will be returned.
        """
        params = {'file_ids': file_ids}
        response = self._call(action='zip', params=params)
        # put.io returns error for 'application/x-directory' typed
        # attachments. So, we assume that we will always get files as
        # attachments not directories.
        self._download_file(response)

    def share(self, file_ids, friends):
        """ Shares given files with given friends or all friends. """
        data = {'file_ids': file_ids,
                'friends': friends}
        response = self._call(action='share', data=data, method='POST')
        return response.json()

    def list_shared_files(self):
        """ Returns list of shared files and share information. """
        response = self._call(action='shared')
        return response.json()

    def shared_with(self, file_id):
        """
        Returns list of users file is shared with. Each result item
        contains a share id which can be used for unsharing.
        """
        action = '%s/shared-with' % file_id
        response = self._call(action=action)
        return response.json()

    def unshare(self, file_id, friends):
        """ Unshares given file from given friends or from everyone. """
        action = '%s/unshare' % file_id
        data = {'shares': friends}
        response = self._call(action=action, data=data, method='POST')
        return response.json()

    def list_subtitles(self, file_id):
        """ Lists available subtitles for user's preferred language. """
        action = '%s/subtitles' % file_id
        response = self._call(action=action)
        return response.json()

    def download_subtitle(self, file_id, subtitle_key='default',
                          subtitle_format='srt'):
        """ Downloadss the contents of the subtitle file. """
        action = '%s/subtitles/%s' % (file_id, subtitle_key)
        params = {'format': subtitle_format}
        response = self._call(action=action, params=params)
        self._download_file(response)


class Event(Resource):

    def __init__(self, oauth_token=None, client_id=None):
        self.OAUTH_TOKEN = oauth_token
        self.CLIENT_ID = client_id
        self.base_url = 'events/'
        self.client = self._get_client()

    def list(self):
        """ List of dashboard events. Includes download and share events. """
        response = self._call(action='list')
        return response.json()

    def delete(self):
        """
        Clear all dashboard events. User's home screen (dashboard) which
        uses same data will also be cleared at Put.io website.
        """
        response = self._call(action='delete', method='POST')
        return response.json()


class Transfer(Resource):

    def __init__(self, oauth_token=None, client_id=None):
        self.OAUTH_TOKEN = oauth_token
        self.CLIENT_ID = client_id
        self.BASE_URL = 'transfers/'
        self.client = self._get_client()

    def _call(self, action=None, method=None, transfer_id=None, params=None,
              data=None):
        url = self.BASE_URL
        if transfer_id is not None:
            url += str(transfer_id)
        return self.client.call(url, action=action, params=params, data=data,
                                method=method)

    def add_transfer(self, url, save_parent_id=None, extract=None,
                     callback_url=None):
        """ Adds a new transfer. """
        data = {'url': url,
                'save_parent_id': save_parent_id,
                'extract': extract,
                'callback_url': callback_url}
        response = self._call(action='add', data=data, method='POST')
        return response.json()

    def list(self):
        """
        Lists active transfers. If transfer is completed, it is
        removed from the list.
        """
        response = self._call(action='list')
        return response.json()

    def get_transfer(self, transfer_id):
        """ Returns a transfer's properties. """
        transfer_id = str(transfer_id)
        response = self._call(transfer_id=transfer_id)
        return response.json()

    def retry(self, transfer_id):
        """ Retry previously failed transfer. """
        data = {'id': str(transfer_id)}
        response = self._call(action='retry', data=data, method='POST')
        return response.json()

    def cancel(self, transfer_ids):
        """ Deletes the given transfers. """
        data = {'transfer_ids': transfer_ids}
        response = self._call(action='cancel', data=data, method='POST')
        return response.json()

    def clean(self):
        """ Clean completed transfers from the list. """
        response = self._call(action='clean', method='POST')
        return response.json()


class Friend(Resource):

    def __init__(self, oauth_token=None, client_id=None):
        self.OAUTH_TOKEN = oauth_token
        self.CLIENT_ID = client_id
        self.BASE_URL = 'friends/'
        self.client = self._get_client()

    def list(self):
        """ Lists friends. """
        response = self._call(action='list')
        return response.json()

    def waiting_requests(self):
        """ Lists incoming friend requests. """
        response = self._call(action='waiting-requests')
        return response.json()

    def send_request(self, friend_id):
        """ Sends a friend request to the given username. """
        action = '%s/request' % friend_id
        response = self._call(action=action, method='POST')
        return response.json()

    def approve_request(self, friend_id):
        """ Approves a friend request from the given username. """
        action = '%s/approve' % friend_id
        response = self._call(action=action, method='POST')
        return response.json()

    def deny_request(self, friend_id):
        """ Denies a friend request from the given username. """
        action = '%s/deny' % friend_id
        response = self._call(action=action, method='POST')
        return response.json()

    def unfriend(self, friend_id):
        """ Removes friend from friend list. """
        action = '%s/unfriend' % friend_id
        response = self._call(action=action, method='POST')
        return response.json()


class Account(Resource):

    def __init__(self, oauth_token=None, client_id=None):
        self.OAUTH_TOKEN = oauth_token
        self.CLIENT_ID = client_id
        self.BASE_URL = 'account/'
        self.client = self._get_client()

    def info(self):
        """ Information about user account. """
        response = self._call(action='info')
        return response.json()

    def get_settings(self):
        """ User preferences. """
        response = self._call(action='settings')
        return response.json()

    def set_settings(self, default_folder=None, extraction_default=None,
                     is_invisible=None, subtitle_languages=None):
        """ Updates user preferences. Only sent parameters are updated. """

        data = {'default_download_folder': default_folder,
                'extraction_default': extraction_default,
                'is_invisible': is_invisible,
                'subtitle_languages': subtitle_languages}
        response = self._call(action='settings', data=data, method='POST')
        return response.json()
