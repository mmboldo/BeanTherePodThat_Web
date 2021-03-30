from flask_pymongo import PyMongo, MongoClient


class DB(object):

    URI = "mongodb+srv://admin:admin@cluster0.zhcnd.mongodb.net/BeanTherePodThat?retryWrites=true&w=majority"

    @staticmethod
    def init():
       cluster = MongoClient(DB.URI)
       
       
       return cluster
    