# putio
Simple Python client for put.io API v2


This is simple Python client for put.io API v2. Here is a simple example;

from putio import Putio

putio = Putio(client_id='1111', oauth_token='XXXXXX')
putio.File.list_files()
putio.Transfer.list()
putio.Friend.list()
putio.Account.info()
putio.Event.list()

All of the methods return raw json data instead processing on that.

You can look at the [put.io API documentation](https://put.io/v2/docs/index.html) for other methods and more details.

The client's architecture is so simple as well:

![alt text](https://docs.google.com/uc?authuser=0&id=0B1jyp5tOC743VWI5UlliTXF2YWM&export=download)