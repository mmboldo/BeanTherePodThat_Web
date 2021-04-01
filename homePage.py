from flask import Flask, render_template, request, url_for, session, redirect, flash, jsonify
from flask_pymongo import PyMongo
from pymongo import MongoClient
from classes import *
from flask_socketio import SocketIO, emit
from flask_pymongo import PyMongo
from bson.json_util import dumps, loads 
from datetime import datetime
from datetime import timedelta
from random import sample

app = Flask(__name__)
app.config['SECRET_KEY'] = 'someSecretKey123'
app.config['DEBUG'] = True

# mongodb+srv://danisrdias:CBlossom.31@cluster0.5ahgv.mongodb.net/myFirstDatabase?retryWrites=true&w=majority

# secret key is used to make the client-side sessions secure
app.config.update(dict(SECRET_KEY='yoursecretkey'))
client = MongoClient('mongodb+srv://danisrdias:CBlossom.31@cluster0.5ahgv.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
# DB name
db = client.myFirstDatabase

app.config["MONGO_URI"] = "mongodb+srv://danisrdias:CBlossom.31@cluster0.5ahgv.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"

mongo = PyMongo(app)

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
        coffees = db.coffee.find({})
        
        if request.method == 'POST':
            # db.coffees.insert_one({'name':session['firstName'] , 'coffeeName':request.form['coffeeName'], 'coffeeOpinion': request.form['coffeeOpinion'], 'rate':request.form['rate']})
            db.coffeesComments.insert_one({'firstName':session['firstName'], 'lastName':session['lastName'], 'email':session['email'], 'coffeeName':request.form['coffeeName'], 
            'coffeeOpinion': request.form['coffeeOpinion'], 'rate':request.form['rate'], 'last_modified': datetime.now()}) 
               
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
        
        bestRatedCoffees = mongo.db.coffeesComments.distinct( "coffeeName" , { "rate" : "5" } )

        myCoffees = mongo.db.myCoffees.find({'email': session['email']})
        
        # getting the count to feed the graph
        ethiopiaCounts = mongo.db.coffeesComments.find({"coffeeName": 'Ethiopia'}).count()
        
        melozioCounts = mongo.db.coffeesComments.find({"coffeeName": 'Melozio'}).count()
        
        altissioCounts = mongo.db.coffeesComments.find({"coffeeName": 'Altissio'}).count()
        
        altodolceCounts = mongo.db.coffeesComments.find({"coffeeName": 'Alto Dolce'}).count()
        
        livantoCounts = mongo.db.coffeesComments.find({"coffeeName": 'Livanto'}).count()
        
        return render_template('dashboard.html', lastOpinions=lastOpinions, myLastOpinions=myLastOpinions, bestRatedCoffees=bestRatedCoffees, myCoffees=myCoffees,
        ethiopiaCounts=ethiopiaCounts, melozioCounts=melozioCounts, altissioCounts=altissioCounts, altodolceCounts=altodolceCounts, livantoCounts=livantoCounts) 
    
    # if not logged, user will be forward to login page 
    return redirect(url_for('login'))

# this page user will see the pods available
@app.route('/coffeePods', methods=['GET', 'POST'])
def coffeePods():
    if 'email' in session:
        coffees = mongo.db.coffee.find({})
        
        if request.method == 'POST':
            db.myCoffees.insert_one({'firstName':session['firstName'], 'lastName':session['lastName'], 'email':session['email'],'coffeeID':request.form['coffeeID'],
            'coffeeName':request.form['coffeeName'], 'brand':request.form['brand']})
            
            return redirect(url_for('coffeePods'))
            
        return render_template('coffeePods.html', coffees=coffees)
    # if not logged, user will be forward to login page 
    return redirect(url_for('login'))
    
# route for the chat
@app.route('/chat')
def chat():
    
    if 'email' in session:
        return render_template('chat.html')
    else:
        return redirect(url_for('login'))
    
    
# # this block of routes are for the chat. 
# @socketio.on('username')
# def receive_username_from_client(data):
#     data = session['email']
#     print(data) # this is just to verify/see the data received from the client
#     users[data] = request.sid; # the session id is "saved"
#     send_broadcast_message('{} your message has been sent '.format(data))
  
# @socketio.on('messages')
# def receive_messages(msg):
#     send_broadcast_message('{} -- sent by someone'.format(msg))
    
# @socketio.on('private_msg')
# def receive_private_from_client(data):
#     # data = session['email']
#     print(data) # the data was sent in json format
#     person = data['to']
#     message = data['message']
#     if person in users.keys():
#         emit('notification', message, room = users[person]) # the session id is used as individual "room"
#     else: 
#         emit('notification', '{} does not exists'.format(person))

# # this would send a message to ALL clients
# def send_broadcast_message(msg):
#     emit('notification', msg, broadcast=True)



@app.route('/')
def index():
    if 'useremail' in session:
        return 'You are logged in as ' + session['useremail']
        
    return render_template('login.html')
 
#
# This part serves as Android auth
# url should be with /api/
#
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
        
    
#
# This part serves as Android registration
# url should be with /api/
#    
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
    
    # This part serves as Android registration
    # url should be with /api/
    #
    @app.route('/api/coffeelist', methods=['POST'])
    def android_coffeelist():
        coffeelist = mongo.db.coffee
        existing_coffee = coffeelist.find_one({'coffeeID' : request.form['coffeeID']})
        coffeeID = request.form['coffeeID']
        coffeeName = request.form['coffeeName']
        brand = request.form['brand']
        description = request.form['description']
        intensity = request.form['intensity']
        cupSize = request.form['cupSize']
        roast = request.form['roast']
        acidity = request.form['acidity']
        bitterness = request.form['bitterness']
        body = request.form['body']
        ingredients = request.form['ingredients']
        machine = request.form['machine']

        error = None

        if not coffeeID:
            error = 'ID is required.'
        elif existing_coffee:
            error = 'That coffee already exists!'

        if error is None:
            coffeelist.insert_one({'coffeeID' : request.form['coffeeID'], 'coffeeName' : request.form['coffeeName'], 'brand' : request.form['brand'],
            'description' : request.form['description'], 'intensity' : request.form['intensity'], 'cupSize' : request.form['cupSize'],
            'roast' : request.form['roast'], 'acidity' : request.form['acidity'], 'bitterness' : request.form['bitterness'], 'body' : request.form['body'],
            'ingredients' : request.form['ingredients'], 'machine' : request.form['machine']
            })
            return 'Successfully inserted Coffee!'

        return error


    @app.route('/api/coffee', methods=['GET'])
    def android_getcoffeelist():
        collection = mongo.db.coffee.find()
        print(collection)
        print('Here is the collection')
        return 'Get Coffees'


if __name__ == '__main__':
    app.secret_key = 'dev'
    socketio.run(app,host = '0.0.0.0' ,debug=True)  # here, we are using socketio instaead of app because it has more features
