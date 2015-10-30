import requests
import logging


logger = logging.getLogger(__name__)


class Client:

    def __init__(self, client_id, oauth_token):
        self.BASE_URL = 'https://api.put.io/v2/'
        self.UPLOAD_URL = 'https://upload.put.io/v2/'
        self.OAUTH_TOKEN = oauth_token
        self.CLIENT_ID = client_id

    def call(self, url, action='', params=None, data=None, method=None,
             files=None, stream=False):
        if params is None:
            params = {}
        if method is None:
            method = 'GET'
        params['oauth_token'] = self.OAUTH_TOKEN
        headers = {"Accept": "application/json"}
        if action == 'upload':
            url = self.UPLOAD_URL + url + action
        else:
            url = self.BASE_URL + url + action
        try:
            response = requests.request(method, url, params=params,
                                        headers=headers, data=data,
                                        files=files, stream=True)
            response.raise_for_status()
        except Exception as e:
            logging.error(e, exc_info=True)
            raise
        return response
