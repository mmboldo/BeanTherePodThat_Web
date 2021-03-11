from flask import Flask, render_template, request
from pymongo import MongoClient
from classes import *

app = Flask(__name__)
# secret key is used to make the client-side sessions secure
app.config.update(dict(SECRET_KEY='yoursecretkey'))
client = MongoClient('mongodb+srv://myadmin:myadmin@cluster0.5nwxg.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
# DB name
db = client.BeanTherePodThat

# db points to the database. db.settings points to the collection name "settings" inside the database collection
# it inserts 1 document if 'userId' is not found
if db.settings.find({'name': 'userId'}).count() <= 0:
    print("userId Not found, creating....")
    db.settings.insert_one({'name':'userId', 'value':0})
    
def createUser(form):
    firstName = form.firstName.data
    lastName = form.lastName.data
    email = form.email.data
    password = form.password.data
    userId = db.settings.find_one()['value']
    
    user = {'id':userId, 'firstName':firstName, 'lastName':lastName, 'email':email, 'password':password}

    db.users.insert_one(user)
    # updateTaskID(1)
    return render_template('homePage.html')



@app.route('/homePage')                         # default method is GET
def init():                            # this is a comment. You can create your own function name
    return render_template('homePage.html')
    #return '<h1>Welcome to Flask! </h1>'


@app.route('/registration', methods=['GET','POST','PUT'])
def main():
    # create form
    cform = CreateUser(prefix='createUser')
    
     # response
    if cform.validate_on_submit():
        return createUser(cform)  
    
     # cform (This would be the variable used in sampleClasses.py) = cform (This refers to the form that was created. cform = CreateTask(prefix='createform'))
    return render_template('registration.html', cform = cform)

# def your_url():
#     if request.method == 'GET':
#         return render_template('registration.html', name=request.form.get('dname', 'No data passed'))

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)   # host='0.0.0.0' means whatever your public ip assigned will be used
    