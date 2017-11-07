import json
import numpy as np

cooccur_table = np.loadtxt("cooccurrence.csv", delimiter=",")
with open("tag_id.json", "r") as js:
    tag_id = json.load(js)

print(type(cooccur_table[0][0]))
print(tag_id)

id2tag = ["" for _ in range(len(tag_id))]
for key, value in tag_id.items():
    id2tag[value] = key

"""
"nodes" : [
    {"id": ***, "group": ***},
    ],
"links": [
    {"source": ***, "target": ***, "value": ***}
    ]
"""

# create nodes
nodes = []
for key, value in tag_id.items():
    nodes.append({"id": key, "group": 0})

# create links
links = []
for y, tags in enumerate(cooccur_table):
    for x, val in enumerate(tags):
        if x < y:
            continue
        if val > 50:
            links.append({"source": id2tag[y], "target": id2tag[x], "value": val})

data_json = {"nodes": nodes, "links": links}

with open("../src/lib/data.json", "w") as f:
    json.dump(data_json, f, indent=2)