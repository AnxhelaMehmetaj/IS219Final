from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, validators


class create_product_form(FlaskForm):


    submit = SubmitField()
