from flask import Flask, render_template, request, url_for, session, redirect, flash
from flask_pymongo import PyMongo
from pymongo import MongoClient
from classes import *
from flask_socketio import SocketIO, emit
from flask_pymongo import PyMongo
from bson.json_util import dumps, loads 
from datetime import datetime
from datetime import timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'someSecretKey123'
app.config['DEBUG'] = True



# secret key is used to make the client-side sessions secure
app.config.update(dict(SECRET_KEY='yoursecretkey'))
client = MongoClient('mongodb+srv://myadmin:myadmin@cluster0.5nwxg.mongodb.net/BeanTherePodThat?retryWrites=true&w=majority')
# DB name
db = client.BeanTherePodThat

app.config["MONGO_URI"] = "mongodb+srv://myadmin:myadmin@cluster0.5nwxg.mongodb.net/BeanTherePodThat?retryWrites=true&w=majority"

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
                return redirect(url_for('init'))
                
            return 'Invalid email and/or password'
    
    # the page template    
    return render_template('login.html')
    
@app.route('/logout')
def logout():
	if 'email' in session:
		session.pop('email', None)
	return render_template('logout.html')
	
    
# this method register a new user
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        # if the user already exists, don't register
        existing_user = db.users.find_one({'email': request.form['email']})
        
        # if new user, insert it into DB
        if existing_user is None:
            # hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            db.users.insert_one({'email':request.form['email'], 'password': request.form['password'], 'firstName': request.form['firstName'], 'lastName': request.form['lastName']})
            session['email'] = request.form['email']
            return redirect(url_for('homePage'))
        
        return 'Email already register'
        
    # the page template   
    return render_template('registration.html')
    

# add a coffee is a page that the user needs to be logged
@app.route('/addCoffee', methods=['GET', 'POST'])
def addCoffee():  
    # go to this page only if logged. 
    if 'email' in session:
        if request.method == 'POST':
            # db.coffees.insert_one({'name':session['firstName'] , 'coffeeName':request.form['coffeeName'], 'coffeeOpinion': request.form['coffeeOpinion'], 'rate':request.form['rate']})
            db.coffees.insert_one({'firstName':session['firstName'], 'lastName':session['lastName'], 'email':session['email'], 'coffeeName':request.form['coffeeName'], 
            'coffeeOpinion': request.form['coffeeOpinion'], 'rate':request.form['rate'], 'last_modified': datetime.now()}) 
               
        return render_template('addCoffee.html') 
        

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
    

@app.route('/', methods=['GET', 'POST'])
def init():                            # this is a comment. You can create your own function name
# go to this page only if logged. 
    if 'email' in session:
        
        lastOpinions = mongo.db.coffees.find({}).sort('last_modified', -1).limit(-5)
    
        myLastOpinions= mongo.db.coffees.find({'email': session['email']}).sort('last_modified', -1).limit(-5)
        
        las
        
        return render_template('dashboard.html', lastOpinions=lastOpinions, myLastOpinions=myLastOpinions) 
    
    # if not logged, user will be forward to login page 
    return redirect(url_for('login'))
    
    
@socketio.on('username')
def receive_username_from_client(data):
    data = session['email']
    print(data) # this is just to verify/see the data received from the client
    users[data] = request.sid; # the session id is "saved"
    send_broadcast_message('{} your message has been sent '.format(data))
  
@socketio.on('messages')
def receive_messages(msg):
    send_broadcast_message('{} -- sent by someone'.format(msg))
    
@socketio.on('private_msg')
def receive_private_from_client(data):
    # data = session['email']
    print(data) # the data was sent in json format
    person = data['to']
    message = data['message']
    if person in users.keys():
        emit('notification', message, room = users[person]) # the session id is used as individual "room"
    else: 
        emit('notification', '{} does not exists'.format(person))


# this would send a message to ALL clients
def send_broadcast_message(msg):
    emit('notification', msg, broadcast=True)


if __name__ == '__main__':
    socketio.run(app,host = '0.0.0.0' ,debug=True)  # here, we are using socketio instaead of app because it has more features
