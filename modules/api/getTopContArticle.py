from bs4 import BeautifulSoup
import urllib.request
import pymongo
import re
import json
# access to mongodb
client = pymongo.MongoClient('localhost', 27017)

# create db
db = client.qiita_db

tag_co = db.tags

tag_tops = {}
tag_len = tag_co.find({"items_count":{"$gt":500}}).count()
for i, tag in enumerate(tag_co.find({"items_count":{"$gt":500}})):
    print("tag: ", tag["id"])
    print("{0}, {1}".format(i, tag_len))
    url = "https://qiita.com/tags/"+tag["id"]
    regex = r'[^\x00-\x7F]'
    matchedList = re.findall(regex,url)
    for m in matchedList:
        url = url.replace(m, urllib.parse.quote_plus(m, encoding="utf-8"))
    with urllib.request.urlopen(url) as responce:
        data = responce.read().decode("utf-8")
        soup = BeautifulSoup(data)

        top_cont_list = []
        top_cont = soup.find_all(class_="tagShowTopList_targetName")
        for cont in top_cont[:3]:
            top_cont_list.append(cont.a.text)

        top_tag_articles = []
        for cont in top_cont_list:
            with urllib.request.urlopen("https://qiita.com/" + cont) as responce:
                data = responce.read().decode("utf-8")
                soup = BeautifulSoup(data)

                top_articles = soup.find_all(class_="userPopularItems_body")
                # print(top_articles)
                # exit(-1)
                top_tag_article = ""
                _exit = 0
                for article in top_articles:
                    for i, a in enumerate(article):
                        if i == 0:
                            article_html = "<a href=http://qiita.com"+str(a.get("href"))+">"+a.text+"</a>";
                        else:
                            for _a in a.find_all("a"):
                                # print(_a.text)
                                if _a.text == tag["id"]:
                                    top_tag_article = article_html
                                    _exit = 1
                                    break
                        if _exit == 1:
                            break
                    if _exit == 1:
                        break
            # print("tops: ", top_tag_article)
            top_tag_articles.append({"user": cont, "article": top_tag_article})

        # print(top_tag_articles)
    tag_tops[tag["id"]] = top_tag_articles

with open("../../src/lib/tops.json", "w") as f:
    json.dump(tag_tops, f, indent=2)

