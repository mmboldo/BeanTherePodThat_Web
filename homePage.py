from flask import Flask, render_template, request, url_for, session, redirect, flash, jsonify, Blueprint
from flask_pymongo import PyMongo
from pymongo import MongoClient
from classes import *
from flask_socketio import SocketIO, emit
from flask_pymongo import PyMongo
from bson.json_util import dumps, loads 
from datetime import datetime
from datetime import timedelta
from random import sample
from extentsions import mongo


app = Flask(__name__)
app.config['SECRET_KEY'] = 'someSecretKey123'
app.config['DEBUG'] = True
# image configuration
app.config['SECRET_KEY'] = 'someSecretKey123'
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF"]
app.config["MAX_IMAGE_FILESIZE"] = 0.5 * 1024 * 1024

# Former DB used in development. 
# mongodb+srv://danisrdias:CBlossom.31@cluster0.5ahgv.mongodb.net/myFirstDatabase?retryWrites=true&w=majority

# secret key is used to make the client-side sessions secure
app.config.update(dict(SECRET_KEY='yoursecretkey'))

client = MongoClient('mongodb+srv://danisrdias:CBlossom.31@cluster0.5ahgv.mongodb.net/BeanTherePodThat?retryWrites=true&w=majority')
# DB name
db = client.BeanTherePodThat

app.config["MONGO_URI"] = "mongodb+srv://danisrdias:CBlossom.31@cluster0.5ahgv.mongodb.net/BeanTherePodThat?retryWrites=true&w=majority"

# mongo = PyMongo(app)
mongo.init_app(app)

socketio = SocketIO(app)
users = {}


# this method is to open the homePage
@app.route('/homePage')
def homePage():
    # the page template
    return render_template('homePage.html')
    
# this method is to login to the dashboard
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        # store in the variable existing_user the user find in the DB
        existing_user = db.users.find_one({'email': request.form['email']})
    
        # if the user exist, compare the DB password to the password provided
        if existing_user:
            if (request.form['password'] == existing_user['password']):
                session['email'] = request.form['email']
                # get the session firstName and lastName
                session['firstName'] = existing_user['firstName']
                session['lastName'] = existing_user['lastName']
                
                vEmail = existing_user['email']
                vFirstname= existing_user['firstName']
                session[vEmail] = request.form['email']

                # after logged in the user will be forward to dashboard
                return redirect(url_for('dashboard'))
                
            return 'Invalid email and/or password'
    
    # the page template    
    return render_template('login.html')
    
# logout route
@app.route('/logout')
def logout():
	if 'email' in session:
		session.pop('email', None)
	return render_template('logout.html')
	
    
# this method register a new user
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    
    session.pop('email', None)
    if request.method == 'POST':
        
        # if the user already exists, don't register
        existing_user = db.users.find_one({'email': request.form['email']})
        
        # if new user, insert it into DB
        if existing_user is None:
            # hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            db.users.insert_one({'email':request.form['email'], 'password': request.form['password'], 'firstName': request.form['firstName'], 'lastName': request.form['lastName']})
            # session['email'] = request.form['email']

            return redirect(url_for('login'))
        
        return 'Email already register'
        
    # the page template   
    return render_template('registration.html')
    

# add a coffee is a page that the user needs to be logged
@app.route('/addCoffee', methods=['GET', 'POST'])
def addCoffee():  
    # go to this page only if logged. 
    if 'email' in session:
        coffees = db.coffees.find({})
        
        if request.method == 'POST':
            
            db.coffeesComments.insert_one({'firstName':session['firstName'], 'lastName':session['lastName'], 'email':session['email'], 'coffeeName':request.form['coffeeName'], 
            'coffeeOpinion': request.form['coffeeOpinion'], 'rate':request.form['rate'], 'last_modified': datetime.now()}) 
               
               
            db.users.update_one({'email': session['email'], "myCoffees.coffeeName": request.form['coffeeName']},{'$addToSet': { 'myComments': {
                
                    'coffeeName': request.form['coffeeName'],'coffeeOpinion': request.form['coffeeOpinion'], 'rate':request.form['rate'], 'last_modified': datetime.now() }}}, upsert=False)
                    
        return render_template('addCoffee.html', coffees=coffees) 
        

    # if not logged, user will be forward to login page 
    return redirect(url_for('login'))


        
# this method register a new user
@app.route('/registerMachines', methods=['GET', 'POST'])
def registerMachines():
    if request.method == 'POST':
        # if the machine already exists, don't register
        machineExists = db.machines.find_one({'machineModel':request.form['machineModel']})
        
        # if new machine, insert it into DB
        if machineExists is None:
            # hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            db.machines.insert_one({'machineName':request.form['machineName'], 'machineModel':request.form['machineModel']})
            
            return redirect(url_for('registerMachines'))
        
        return 'Machine already register'
        
    # the page template   
    return render_template('registerMachines.html')      
    
# dashboard is a restricted page, can be accessed only logged
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():                            
    # go to this page only if logged. 
    if 'email' in session:
        
        lastOpinions = mongo.db.coffeesComments.find({}).sort('last_modified', -1).limit(-5)
    
        myLastOpinions= mongo.db.coffeesComments.find({'email': session['email']}).sort('last_modified', -1).limit(-5)

        bestRatedCoffees = mongo.db.coffeesComments.distinct( "coffeeName" , { "rate" : "5" })

        myCoffees = mongo.db.users.find({'email': session['email']}, {"myCoffees.coffeeName"})
        
        # getting the count to feed the graph
        ethiopiaCounts = mongo.db.coffeesComments.find({"coffeeName": 'Ethiopia'}).count()
        
        melozioCounts = mongo.db.coffeesComments.find({"coffeeName": 'India'}).count()
        
        altissioCounts = mongo.db.coffeesComments.find({"coffeeName": 'Livanto'}).count()
        
        altodolceCounts = mongo.db.coffeesComments.find({"coffeeName": 'Napoli'}).count()
        
        livantoCounts = mongo.db.coffeesComments.find({"coffeeName": 'Ristretto'}).count()
        
        return render_template('dashboard.html', lastOpinions=lastOpinions, myLastOpinions=myLastOpinions, bestRatedCoffees=bestRatedCoffees, myCoffees=myCoffees,
        ethiopiaCounts=ethiopiaCounts, melozioCounts=melozioCounts, altissioCounts=altissioCounts, altodolceCounts=altodolceCounts, livantoCounts=livantoCounts) 
    
    # if not logged, user will be forward to login page 
    return redirect(url_for('login'))

# this page user will see the pods available
@app.route('/coffeePods', methods=['GET', 'POST'])
def coffeePods():
    if 'email' in session:
        coffees = mongo.db.coffees.find({})
        
        if request.method == 'POST':
            db.myCoffees.insert_one({'firstName':session['firstName'], 'lastName':session['lastName'], 'email':session['email'],'id':request.form['id'],
            'coffeeName':request.form['coffeeName'], 'brand':request.form['brand']})
            
            db.users.update_one({'email': session['email']},{'$addToSet': { 
                'myCoffees': {
                    'id':request.form['id'],
                    'coffeeName':request.form['coffeeName'], 
                    'brand':request.form['brand'],
                    'description':request.form['description'],
                    'intensity':request.form['intensity'],
                    'cupSize':request.form['cupSize'],
                    'roast':request.form['roast'],
                    'acidity':request.form['acidity'],
                    'bitterness':request.form['bitterness'],
                    'body':request.form['body'],
                    'ingredients':request.form['ingredients'],
                    'machine':request.form['machine'] } }}, upsert=False)
            
            return redirect(url_for('coffeePods'))
            
        return render_template('coffeePods.html', coffees=coffees)
    # if not logged, user will be forward to login page 
    return redirect(url_for('login'))
    

## REVIEW - Check if this route is really necessary.
## @Juliana and Travis: Do you use this one for web? Just leave it, so the main page can be redirected to login
## Not useful for Android.
@app.route('/')
def index():
    if 'useremail' in session:
        return 'You are logged in as ' + session['useremail']
        
    return redirect(url_for('login'))
 
#####################################
# This part serves as Android LOGIN #
# url should be with /api/          #
#####################################
@app.route('/api/login', methods=['POST'])
def android_login():
    users = mongo.db.users
    android_user = users.find_one({'email' : request.form['email']})
    password = request.form['password']
    error = None
    if android_user is None:
        error = 'Unknown e-mail. Are you registered?'
    #elif not check_password_hash(android_user['password'], password):
    elif not android_user['password'] == password:
        error = 'Incorrect password'
        
    if error is None:
        session.clear()
        session['email'] = request.form['email']
        return 'You login as ' + session['email']
        #change the message to Hello Marcelo
    
    return error
        
    
############################################
# This part serves as Android REGISTRATION #
# url should be with /api/                 #
############################################
@app.route('/api/register', methods=['POST'])
def android_register():
    users = mongo.db.users
    existing_user = users.find_one({'email' : request.form['email']})
    email = request.form['email']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    password = request.form['password']
    error = None
    
    if not email:
        error = 'Email is required.'
    elif not password:
        error = 'Password is required.'
    elif existing_user:
        error = 'That email already exists!'
        
    if error is None:
        users.insert_one({'email' : request.form['email'], 'firstname' : request.form['firstname'], 'lastname' : request.form['lastname'], 'password' : request.form['password']})
        session['email'] = request.form['email']
        return 'Successfully registered!'
        
    return error

    
###################################################################################################
# This route is responsible for providing the user's data to the Android app service.             #
# It is used by getUserData() in beantherepodthat\retrofitApi.kt                                  #
# Consider removing the password from the find_one query ("password":0} to improve app's security #
###################################################################################################
@app.route('/api/getuserdata', methods=['POST'])
def getuserdata():
    collection = mongo.db.users.find_one({'email':request.form['email']},{"_id":0})
    return jsonify(collection)    


###############################################################################################
# This route is responsible for providing the general coffee list to the Android app service. #
# It is used by getCoffeeList() in beantherepodthat\retrofitApi.kt                            #
###############################################################################################
@app.route('/api/getcoffeelist', methods=['POST'])
def getcoffeelist():
    collection = mongo.db.coffees.find({},{'_id':0})
    print('collection:',collection)
    datalist = list(collection)
    return jsonify(datalist)

# Adding a coffee to my coffee list
@app.route('/api/myCoffees', methods=['POST'])
def android_myCoffees():

    # collection = mongo.db.users.find({'email': request.form['email']})
    
    db.users.update_one({'email':request.form['email']},{'$addToSet': { 
        'myCoffees': {
        'id':request.form['id'],
        'coffeeName':request.form['coffeeName'], 
        'coffeeImg':request.form['coffeeImg'], 
        'brand':request.form['brand'],
        'description':request.form['description'],
        'intensity':request.form['intensity'],
        'cupSize':request.form['cupSize'],
        'roast':request.form['roast'],
        'acidity':request.form['acidity'],
        'bitterness':request.form['bitterness'],
        'body':request.form['body'],
        'ingredients':request.form['ingredients'],
        'machine':request.form['machine'],
        'rate': request.form['rate'],
        'favorite': request.form['favorite']    
        } }}, upsert=False)
    return 'Successfully inserted Coffee!'
    
# This is just a test for Android's interface. Should be removed.
@app.route('/api/coffee', methods=['GET'])
def android_getcoffeelist():
    collection = mongo.db.coffee.find()
    print(collection)
    print('Here is the collection')
    return 'Get Coffees'
    

# profile
import profile
app.register_blueprint(profile.bp)

import machine
app.register_blueprint(machine.bp)

@app.route('/file/<filename>')
def file(filename):
    return mongo.send_file(filename)


if __name__ == '__main__':
    app.secret_key = 'dev'
    socketio.run(app,host = '0.0.0.0' ,debug=True)  # here, we are using socketio instaead of app because it has more features
