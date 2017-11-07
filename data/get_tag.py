import sys
import pymongo
import json
import urllib.request
import time

access_token = "**********"

# access to mongodb
client = pymongo.MongoClient('localhost', 27017)

# create db
db = client.qiita_db

# create collection
try:
    db.tags.drop() # まず削除
except:
    print("tagsというコレクションを作成します．")
collection = db.tags

# page is 1 to 100
for page in range(1, 101):
    req = urllib.request.Request("https://qiita.com/api/v2/tags?page="+str(page)+"&per_page=100&sort=count",
        headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + access_token})
    with urllib.request.urlopen(req) as responce:
        data = responce.read().decode("utf-8")
        obj = json.loads(data)
        if (len(obj) < 10):
            print("illigal object")
            print(obj)
            exit(-1)
        for d in obj:
            print(d)
            collection.insert_one(d)
    time.sleep(0.1)
print("Completed!")
