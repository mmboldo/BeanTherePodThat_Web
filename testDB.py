
import pymongo

from pymongo import MongoClient

URI = "mongodb+srv://admin:admin@cluster0.zhcnd.mongodb.net/BeanTherePodThat?retryWrites=true&w=majority"
cluster = MongoClient(URI)
db = cluster["test"]
collection = db["testCollection"]

post = {"name":"tim", "score": 5}
post1 = {"_id":5, "name": "user1"}
post2 = {"_id":6, "name": "user2"}

results = collection.find({})

for e in results:
    print(e)