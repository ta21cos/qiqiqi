import flask
import pymongo
import sys
import json
import time
import numpy as np
import itertools
from flask_cors import CORS, cross_origin

# use Flask as API
api = flask.Flask(__name__)
CORS(api)

# access to mongodb
client = pymongo.MongoClient('localhost', 27017)

# create db
db = client.qiita_db

tag_co = db.tags
article_co = db.articles

tag2id_dict = {}
nitems_dict = {}

for i, tag in enumerate(tag_co.find({"items_count":{"$gt":500}})):
    tag2id_dict[tag["id"]] = i
    nitems_dict[tag["id"]] = tag["items_count"]

id2tag = ["" for _ in range(len(tag2id_dict))]
for key, value in tag2id_dict.items():
    id2tag[value] = key

@api.route("/")
def hello():
    return flask.render_template("../../src/html/first.html", title="Flaski")

@api.route("/tags", methods=["GET"])
def getTags():
    responce = flask.jsonify(tag2id_dict)
    responce.status_code = 200
    return responce

@api.route("/cooccurrence", methods=["GET"])
def calcCooccurrence():
    cooccurrence_table = np.zeros((len(tag2id_dict), len(tag2id_dict)))
    for i, article in enumerate(article_co.find({"user.followers_count": {"$gt": 100}})):
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

    # create nodes
    nodes = []
    for key, value in tag2id_dict.items():
        nodes.append({"id": key, "value": nitems_dict[key], "group": 0})

    # create links
    links = []
    # for y, tags in enumerate(normalized_table):
    for y, tags in enumerate(cooccurrence_table):
        if max(tags) < 20:
            links.append({"source": id2tag[y], "target": id2tag[np.argmax(tags)], "value": max(tags)})
            continue
        for x, val in enumerate(tags):
            if x <= y or val < 20:
                continue
            links.append({"source": id2tag[y], "target": id2tag[x], "value": val})

    maintag_color = {"JavaScript": 1, "Ruby": 1, "HTML": 1, "PHP": 1, "iOS": 2, "Android": 2, "Python": 3, "MachineLearning": 3};

    colors = {}
    for key, val in tag2id_dict.items():
        if key in maintag_color:
            colors[key] = maintag_color[key]
        else:
            colors[key] = 0
    for i, link in enumerate(links):
        if link["source"] in maintag_color and link["target"] not in maintag_color:
            colors[link["target"]] = maintag_color[link["source"]]
        elif link["target"] in maintag_color and link["source"] not in maintag_color:
            colors[link["source"]] = maintag_color[link["target"]]

    data_json = {"nodes": nodes, "links": links, "colors": colors}

    # with open("~/Desktop/php.json", "w") as f:
    #     json.dump(data_json, f, indent=2)

    # return data_json
    responce = flask.jsonify(data_json)
    responce.status_code = 200
    return responce

@api.errorhandler(404)
def not_found(error):
    print("error")
    return flask.make_responce(flask.jsonify({"error": "Not found"}), 404)

if __name__ == "__main__":
    api.run(port=3000)
