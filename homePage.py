from flask import Flask, render_template, request, url_for, session, redirect
from flask_pymongo import PyMongo
from pymongo import MongoClient
from classes import *


app = Flask(__name__)
# secret key is used to make the client-side sessions secure
app.config.update(dict(SECRET_KEY='yoursecretkey'))
client = MongoClient('mongodb+srv://myadmin:myadmin@cluster0.5nwxg.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
# DB name
db = client.BeanTherePodThat

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
                # after logged in the user will be forward to dashboard
                return redirect(url_for('dashboard'))
                
            return 'Invalid email and/or password'
    
    # the page template    
    return render_template('login.html')
    
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
    
# when the user is logged, it will be directed to the dashboard page
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():  
    # go to this page only if logged. 
    if 'email' in session:
        return render_template('dashboard.html') 
    
    # if not logged, user will be forward to login page 
    return render_template('login.html')

        
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



if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True) 
    


