import functools
from flask import Flask, render_template, flash, request, redirect, url_for, Blueprint, current_app, session
from werkzeug.utils import secure_filename
from flask_pymongo import PyMongo
from datetime import datetime, timezone
from extentsions import mongo
from bson import json_util


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://admin:admin@cluster0.zhcnd.mongodb.net/BeanTherePodThat?retryWrites=true&w=majority" # replace the URI with your own connection

# db = mongo.db
# bp = Blueprint('profile', __name__, url_prefix='/profile')
# collection = mongo

mongo = PyMongo(app)


@app.route('/')
def myMachine():
    return "Hello My Machine"


# testing use only
@app.route("/insert-machine", methods=['GET', 'POST'])
def insert_machine():
   
    if request.method == "POST":
        db.machine.insert_one({
            'machineName':request.form['machineName'],
            'machineType':request.form['machineType'],
            'brand': request.form['brand'],
            'image':request.form['machine'],
            'email':request.form['email']})
        return "done!"
    return render_template("insert_machine.html")


@app.route('/file/<filename>')
def file(filename):
    return mongo.send_file(filename)

if __name__ == '__main__':
    app.run(host = '0.0.0.0' ,debug=True) 