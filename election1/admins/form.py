from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, BooleanField
from wtforms.validators import Length, Email, InputRequired, DataRequired, EqualTo
from election1.models import Admin_roles
from wtforms_alchemy.fields import QuerySelectField


def admin_roles_query():
    return Admin_roles.query


class UserForm(FlaskForm):
    user_firstname = StringField(label='firstname', validators=[Length(min=2, max=30), InputRequired()])
    user_lastname = StringField(label='lastname', validators=[Length(min=2, max=30), InputRequired()])
    user_so_name = StringField(label='user name', validators=[Length(min=2, max=30), InputRequired()])
    user_pass = PasswordField('Password', validators=[InputRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[
        InputRequired()])
    # user_role = StringField(label='role',  validators=[Length(min=1, max=1), InputRequired()])
    id_admin_role = QuerySelectField(query_factory=admin_roles_query, label='admin role', get_label='admin_role_name')

    user_email = EmailField(label='email', validators=[Email()])
    submit = SubmitField(label='submit')


class LoginForm(FlaskForm):
    login_so_name = StringField(label='username', validators=[Length(min=2, max=30), InputRequired()])
    login_pass = PasswordField(label='password', validators=[Length(min=2, max=30), InputRequired()])
    remember = BooleanField(label='remember me')
    submit = SubmitField(label='submit')
