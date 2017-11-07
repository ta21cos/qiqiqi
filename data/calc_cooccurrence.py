import sys
import pymongo
import json
import urllib.request
import time
import numpy as np
import itertools
# access to mongodb
client = pymongo.MongoClient('localhost', 27017)

# create db
db = client.qiita_db

tag_co = db.tags
article_co = db.articles

tag_id = {}

for i, tag in enumerate(tag_co.find({"items_count":{"$gt":100}})):
    tag_id[tag["id"]] = i

with open("tag_id.json", "w") as f:
    json.dump(tag_id, f)

cooccurrence_table = [[0 for _ in range(len(tag_id))] for _ in range(len(tag_id))]

article_len = article_co.count()
for i, article in enumerate(article_co.find()):
    print("{0}/{1} {2}".format(i, article_len, article["title"]))
    # print([tag_id[name] for name in tag_names])
    for tag1, tag2 in itertools.product(article["tags"], article["tags"]):
        try:
            tag1_id, tag2_id = tag_id[tag1["name"]], tag_id[tag2["name"]]
        except:
            # tagsにないtagがある場合はスキップ
            continue
        cooccurrence_table[tag1_id][tag2_id] += 1

np_cooccrr_table = np.array(cooccurrence_table)

np.savetxt("cooccurrence.csv", np_cooccrr_table, fmt="%.0f", delimiter=",")

# 対角成分はゼロにする（正規化の際絶対に大きくなる成分があるため）
np_cooccrr_table[np.identity(len(np_cooccrr_table)) == 1] = 0
normalized_table = np_cooccrr_table / np.max(np_cooccrr_table)

np.savetxt("cooccurrence_norm.csv", normalized_table, delimiter=",")

print("Completed!")
