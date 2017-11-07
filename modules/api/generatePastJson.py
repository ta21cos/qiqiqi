import pymongo
import sys
import json
import time
import numpy as np
import itertools

year = int(sys.argv[1])
print("Year:", year)

# access to mongodb
client = pymongo.MongoClient('localhost', 27017)

# create db
db = client.qiita_db

tag_co = db.tags
article_co = db.articles

tag2id_dict = {}
nitems_dict = {}

num_of_articles = article_co.find({"created_at" :{"$lt": str(year+1)}}).count()
print(num_of_articles)

for i, tag in enumerate(tag_co.find({"items_count":{"$gt":500}})):
    tag2id_dict[tag["id"]] = i
    nitems_dict[tag["id"]] = article_co.find({"created_at": {"$lt": str(year+1)}, "tags": {"$elemMatch": {"name": tag["id"]}}}).count()
    # print(article_co.find({"created_at": {"$lt": str(year)}, "tags": {"$elemMatch": {"name": tag}}}).count())
    # nitems_dict[tag["id"]] = tag["items_count"]
print(nitems_dict)
id2tag = ["" for _ in range(len(tag2id_dict))]
for key, value in tag2id_dict.items():
    id2tag[value] = key

def calcCooccurrence():
    cooccurrence_table = np.zeros((len(tag2id_dict), len(tag2id_dict)))
    threshold = {"2012": 10, "2013": 30, "2014": 90, "2015": 90, "2016": 90, "2017": 90}
    for i, article in enumerate(article_co.find({"user.followers_count": {"$gt": threshold[str(year+1)]}, "created_at" :{"$lt": str(year+1)}}).sort("created_at", -1)):
        for tag1, tag2 in itertools.product(article["tags"], article["tags"]):
            try:
                tag1_id, tag2_id = tag2id_dict[tag1["name"]], tag2id_dict[tag2["name"]]
            except:
                # tagsにないtagがある場合はスキップ
                continue
            cooccurrence_table[tag1_id][tag2_id] += 1

    # normalize
    # cooccurrence_table[np.identity(len(cooccurrence_table)) == 1] = 0
    # normalized_table = cooccurrence_table / np.max(cooccurrence_table)

    # create links
    links = []
    tag_set = set()
    # for y, tags in enumerate(normalized_table):
    for y, tags in enumerate(cooccurrence_table):
        # if y+1 < len(tags) and max(tags[y+1:]) < 20:
        # if max(tags[np.eye(len(tags))[y] == 0]) < 20:
        #     # print(id2tag[y])
        #     links.append({"source": id2tag[y],
        #         "target": id2tag[np.argmax(tags[np.eye(len(tags))[y] == 0])],
        #         "value": max(tags[np.eye(len(tags))[y] == 0])
        #     })
        #     continue
        # elif y+1 == len(tags):
        #     tags[y] = 0
        #     links.append({"source": id2tag[y],
        #         "target": id2tag[np.argmax(tags)],
        #         "value": max(tags)
        #     })
        for x, val in enumerate(tags):
            # if x <= y or val < num_of_articles//150:
            threshold = {"2012": 1, "2013": 15, "2014": 20, "2015": 20, "2016": 20, "2017": 20}
            if x <= y or val < threshold[str(year+1)]:
                continue
            links.append({"source": id2tag[y], "target": id2tag[x], "value": val})
            tag_set.add(id2tag[y])
            tag_set.add(id2tag[x])

    # create nodes
    nodes = []
    for key, value in tag2id_dict.items():
        if key in tag_set:
            nodes.append({"id": key, "value": nitems_dict[key], "group": 0})
        else:
            nodes.append({"id": key, "value": 0, "group": 0})

    maintag_color = {
        "JavaScript": "#FFE74C", 
        "Ruby": "#FFE74C", 
        "HTML": "#FFE74C", 
        "PHP": "#FFE74C", 
        "iOS": "#FF5964", 
        "Android": "#FF5964", 
        "Python": "#6BF178",
        "MachineLearning": "#6BF178",
        "Linux": "#35A7FF",
        "AWS": "#35A7FF",
        "vagrant": "#35A7FF"
    };

    colors = {}
    for key, val in tag2id_dict.items():
        if key in maintag_color:
            colors[key] = maintag_color[key]
        else:
            main_links = []
            for link in links:
                if link["source"] == key and link["target"] in maintag_color:
                    main_links.append((link["target"], link["value"]))
                elif link["target"] == key and link["source"] in maintag_color:
                    main_links.append((link["source"], link["value"]))
                if not main_links:
                    colors[key] = "#DBDBDB"
                else:
                    max_link = max(main_links, key=lambda x: x[1])
                    max_tag = max_link[0]
                    colors[key] = maintag_color[max_tag]

    # for i, link in enumerate(links):
    #     if link["source"] not in colors:
    #         # まだ色が決まっていない
    #         colors[link["target"]] = maintag_color[link["source"]]
    #     elif link["target"] in maintag_color and link["source"] not in maintag_color:
    #         colors[link["source"]] = maintag_color[link["target"]]

    data_json = {"nodes": nodes, "links": links, "colors": colors}

    with open("../../src/lib/data_"+str(year)+".json", "w") as f:
        json.dump(data_json, f, indent=2)

    print("completed!")

if __name__ == "__main__":
    calcCooccurrence()
