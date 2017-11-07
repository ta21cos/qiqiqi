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

collection = db.users

for data in collection.find({"followers_count":{"$gt": 0}}):
    # print(data)
    user = data["id"]
    print(user)
    for page in range(1, 101):
        req = urllib.request.Request("https://qiita.com/api/v2/users/"+user+"/followers?page="+str(page)+"&per_page=100&sort=count",
            headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + access_token})
        with urllib.request.urlopen(req) as responce:
            data = responce.read().decode("utf-8")
            obj = json.loads(data)
            if len(obj) == 0:
                print("no more followers")
                break
            for d in obj:
                print(d)
                if collection.find({"id": d["id"]}).count() == 0:
                    collection.insert_one(d)
                    print("new user found!")
            time.sleep(0.1)
    # exit(-1)
print("Completed!")
