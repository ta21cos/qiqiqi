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

tag_co = db.tags
article_co = db.articles

num_reqs = 0

for data in tag_co.find().sort("items_count", pymongo.DESCENDING):
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
            for d in obj:
                if article_co.find({"id": d["id"]}).count() == 0:
                    print(d)
                    article_co.insert_one(d)
                    print("new article found!")
                else:
                    print("existing article")
        if num_reqs >= 900:
            num_reqs = 0
            time.sleep(3600)
        else:
            time.sleep(0.1)
    # exit(-1)
print("Completed!")
