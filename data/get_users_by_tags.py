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

user_co = db.users
tag_co = db.tags
article_co = db.articles

if user_co.count() > 0 or article_co.count() > 0:
    print("users or articles collection already exists. Remove first.")
    exit(-1)

num_reqs = 0

user_ids = []
len_tags = tag_co.find({"items_count":{"$gt":100}}).count()

for i, data in enumerate(tag_co.find({"items_count":{"$gt":100}}).sort("items_count", pymongo.DESCENDING))[17:]:
    # print(data)
    tag = data["id"]
    print(tag)
    for page in range(1, 101):
        req = urllib.request.Request("https://qiita.com/api/v2/tags/"+tag+"/items?page="+str(page)+"&per_page=100",
            headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + access_token})
        num_reqs += 1
        with urllib.request.urlopen(req) as responce:
            data = responce.read().decode("utf-8")
            obj = json.loads(data)
            if len(obj) == 0:
                print("no more articles")
                break
            for j, d in enumerate(obj):
                print("tag: {0} {1}/{2}, page: {3}, obj:{4}/{5}, ".format(tag, i, len_tags, page, j, len(obj)), end=" ")

                if d["user"]["permanent_id"] not in user_ids:
                    user_ids.append(d["user"]["permanent_id"])
                    user_co.insert_one(d["user"])
                    print("new user!", len(user_ids))
                else:
                    print("existing user", len(user_ids))
        if num_reqs >= 900:
            num_reqs = 0
            time.sleep(3600)
print("Completed!")
