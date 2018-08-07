import os
import requests
from threading import Timer

url = 'http://192.168.1.106:5001/upload'
post_fields = {'image': '\@.\/static\/trump-test.jpg', 'token': 'RDRDRD'}

def send_image():
    file = open('static/trump-test.jpg', 'rb')
    image = {'image': file}
    r = requests.post(url, files=image, data=post_fields)
    print(r.text)
    t = Timer(7.0, send_image)
    t.start()

send_image()

#request = Request(url, urlencode(post_fields).encode())

#json = urlopen(request).read().decode()
#print(json)


