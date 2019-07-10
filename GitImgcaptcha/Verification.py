import requests
import json

url = "http://192.168.199.208:5000/b"
files = {'image_file': ('xxx', open('img/14.jpg', 'rb'), 'application')}
r = requests.post(url=url, files=files)
print(json.loads(r.text))
