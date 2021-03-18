
# sudo pip3 install Flask-PyMongo
# sudo pip3 install pymongo[srv]
# sudo pip3 install flask-socketio
# sudo pip3 install eventlet


from flask import Flask, render_template,  request, escape
from flask_socketio import SocketIO, emit
from flask_pymongo import PyMongo
from bson.json_util import dumps, loads 


app = Flask(__name__)
app.config['SECRET_KEY'] = 'someSecretKey123'
app.config['DEBUG'] = True

socketio = SocketIO(app)
users = {}

app.config["MONGO_URI"] = "mongodb+srv://myadmin:myadmin@cluster0.5nwxg.mongodb.net/myFirstDatabase?retryWrites=true&w=majority" # replace the URI with your own connection
mongo = PyMongo(app)


@app.route('/')
def init():                            # this is a comment. You can create your own function name
    return render_template('dashboard.html')


@socketio.on('username')
def receive_username_from_client(data):
    print(data) # this is just to verify/see the data received from the client
    users[data] = request.sid ; # the session id is "saved"
    send_broadcast_message('{} just registered '.format(data))
  
@socketio.on('messages')
def receive_messages(msg):
    send_broadcast_message('{} -- sent by someone'.format(msg))
    
@socketio.on('private_msg')
def receive_private_from_client(data):
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