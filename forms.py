from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp
from wtforms import ValidationError

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[Length(0,64)])
    last_name = StringField('Last Name', validators=[Length(0, 64)])
    machine_model = TextAreaField('Machine Model', validators=[Length(0, 64)])
    email = TextAreaField('Email Address', validators=[Length(0, 64)])
    occupation = TextAreaField('Occupation', validators=[Length(0, 64)])
    birthday = TextAreaField('Birthday', validators=[Length(0, 64)])
    submit = SubmitField('submit')

