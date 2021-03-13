from flask_wtf import FlaskForm, RecaptchaField
from wtforms import TextField, IntegerField, SubmitField
from wtforms.validators import DataRequired

class CreateUser(FlaskForm):
    firstName = TextField('First Name',validators=[DataRequired()])
    lastName = TextField('Last Email',validators=[DataRequired()])
    email = TextField('Email',validators=[DataRequired()])
    password = TextField('Password',validators=[DataRequired()])
    create = SubmitField('Create')
    
    

# class DeleteTask(FlaskForm):
#     key = TextField('Task ID')
#     title = TextField('Task Title')
#     delete = SubmitField('Delete')

# class UpdateTask(FlaskForm):
#     key = TextField('Task Key',validators=[DataRequired()])
#     shortdesc = TextField('Short Description',validators=[DataRequired()])
#     update = SubmitField('Update')

# class ResetTask(FlaskForm):
#     reset = SubmitField('Reset')
