# requests is an http client library for Python
# can be used for dealing with web pages and api's
# can be used for downloading files
# can be used for uploading files
# can be used for sending and receiving data

import requests 
import json 

# to custom headers in the request
headers = {'User-Agent': 'Mozilla/5.0'}
github_request = requests.get('https://api.github.com/users/Motasem20007204978', stream=True, headers=headers)

# use stream=True to get the raw socket response in a stream
print('the raw response: ', github_request.raw)

# to get headers in the request
print('the headers: ', github_request.headers)

print(github_request.status_code)
# if exists, the status is 200

content = github_request.content.decode()
print(type(content))

print('///////////////////////////////////////////////')

print(type(github_request.json()))# convert the content to json object

# get json content and store it in json file
with open("content.json", 'w') as f:
    json.dump(github_request.json(), f, indent=2)

