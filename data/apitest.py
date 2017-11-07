import pymongo
import json
import urllib.request

access_token = "**********"

# access to mongodb
client = pymongo.MongoClient('localhost', 27017)

# create db
db = client.qiita_db

# create collection
co = db.qiita_co

# max page is 100
for page in range(1, 100):
    try:
        with urllib.request.urlopen("https://qiita.com/api/v2/tags?page="+str(page)+"&per_page=100&sort=count HTTP/1.1 Host: api.example.com Authorization: "+access_token) as responce:
            data = responce.read().decode("utf-8")
            obj = json.loads(data)
            if (len(obj) < 10):
                print("illigal object")
                print(obj)
                break
            for d in obj:
                print(d)
                co.insert_one(d)
    except:
        print("error")
        break

for data in co.find():
    print(data)
