from flask import Flask, render_template, flash, request, redirect, url_for, Blueprint
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
bp = Blueprint('profile', __name__, url_prefix='/profile')

# @app.route('/user/<username>')
# def profile():
#     return render_template('profile.html')

# @app.route("/edit-profile", methods=['GET','POST'])
# def edit_profile():
#     form = EditProfileForm()
#     if form.validate_on_submit():
#         current_user.name = form.name.data
#         current_user.location = form.location.data
#         current_user.about_me =  form.about_me.data
#         flash('Your profile has been updated.')
#         return redirect(url_for('.user', username=current_user.username))
#     form.name.data = current_user.name
#     form.location.data = current_user.location
#     form.about_me.data = current_user.about_me
#     return render_template('edit_profile.html', form=form)

@bp.route("/", methods=['GET'])
def display_profile():
        # if request.method == "POST":
        #     update_profile(request)
        #     mongo.db.profile.update_one(current_email,)
        #     return
    profile = mongo.db.profile.find_one({"email": "admin@admin.com"})
        # dt = datetime(1994,12,4,0,0, tzinfo=timezone.utc)
    return render_template("profile/profile.html", profile=profile)

    
@bp.route("/edit-profile", methods=['GET', 'POST'])
def edit_profile():
    profile = mongo.db.profile.find_one({"email": "admin@admin.com"})
    

    if request.method == "POST":
        username = request.form["username"]
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        machine = request.form["machine"]
        email = request.form["email"]
        occupation = request.form["occupation"]
        birthday = datetime.strptime(request.form['birthday'], "%Y-%m-%d")
        #updatge database
        mongo.db.profile.update_one({
            'email': profile['email']
        },{
            '$set': {
                'username':username,
                'firstname':firstname,
                'lastname':lastname,
                'machine':machine,
                'email':email,
                'occupation':occupation,
                'birthday':birthday
            }
        }, upsert=False)
        return redirect('/profile')
    
    return render_template("profile/edit_profile.html", profile=profile)

# profile image
@bp.route('/upload-profile', methods=['POST'])
def upload():
    profile = mongo.db.profile.find_one({"email": "admin@admin.com"})
    error = None
    if 'profile_image' in request.files:
        # if "filesize" in request.cookies:
        #     if not allowed_image_filesize(request.cookies["filesize"]):
        #         error = 'Filesize exceeded maximum limit'
        profile_image = request.files['profile_image']
        if profile_image.filename == '':
            error = 'No Filename'                 
        elif not allowed_image(profile_image.filename):
            error = 'That file extension is not allowed'                
            
        if error is None:
            filename = secure_filename(profile_image.filename)
            mongo.save_file(profile_image.filename, profile_image)
            #updatge database
            mongo.db.profile.update_one({
                'email': profile['email']
            },{
                '$set': {
                    'profile_image_name':profile_image.filename
                }
            }, upsert=False)
            return redirect('/profile/edit-profile')

    flash(error)
                
    return render_template("profile/edit_profile.html", profile=profile)




# testing use only
@app.route("/insert_profile", methods=['GET', 'POST'])
def insert_profile():
   
    if request.method == "POST":
        user_birthday = datetime.strptime(request.form['birthday'], "%Y-%m-%d")
        mongo.db.profile.insert_one({
            'username':request.form['username'],
            'firstname':request.form['firstname'],
            'lastname': request.form['lastname'],
            'machine':request.form['machine'],
            'email':request.form['email'],
            'occupation':request.form['occupation'],
            'birthday':user_birthday})
        return render_template("profile.html")
    return render_template("insert_profile.html")


def update_profile(request):
    current_profile = mongo.db.profile.find_one({"email": "testaccount1@gmail.com"})
    current_profile['username'] = request.form['username']
    current_profile['firstname'] = request.form['firstname']
    current_profile['lastname'] =  request.form['lastname']
    current_profile['machine'] = request.form['machine']
    current_profile['email'] = request.form['email']
    current_profile['occupation'] = request.form['occupation']
    current_profile['birthday'] = datetime.strptime(request.form['birthday'], "%Y-%m-%d")




# image limitation
def allowed_image(filename):

    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False


def allowed_image_filesize(filesize):

    if int(filesize) <= app.config["MAX_IMAGE_FILESIZE"]:
        return True
    else:
        return False


if __name__ == '__main__':
    app.run(host = '0.0.0.0' ,debug=True) 