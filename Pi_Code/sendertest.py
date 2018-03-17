import requests
url = 'http://127.0.0.1:5000/display'
data = [('line','srv,-.21'),]
requests.post(url, data)
