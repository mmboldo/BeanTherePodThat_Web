from flask import Flask, render_template, flash, request, redirect, url_for, Blueprint, g
from werkzeug.utils import secure_filename
from flask_pymongo import PyMongo
from datetime import datetime, timezone

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://admin:admin@cluster0.zhcnd.mongodb.net/BeanTherePodThat?retryWrites=true&w=majority" # replace the URI with your own connection
# image configuration
app.config['SECRET_KEY'] = 'someSecretKey123'
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF"]
app.config["MAX_IMAGE_FILESIZE"] = 0.5 * 1024 * 1024

mongo = PyMongo(app)