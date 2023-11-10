from flask import current_app
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SubmitField, SelectField, DateTimeField, TextAreaField, FileField
from wtforms.validators import DataRequired, Length
from wtforms.widgets import DateTimeInput

class CreateFundingForm(FlaskForm):
    fundraiserTitle = StringField(
        label='Fundraiser title', 
        validators=[DataRequired(), Length(10,50)],
        description='Add the title of your page.'
    )
    fundTypeSelect = SelectField(
        label='Fund Type',
        description='Select the funding type.'
    )
    currencySelect = SelectField(
        label='Currency',
        description='Currency used for this fundraising.',
        choices=[
            ('USD', 'USD'),
            ('IDR', 'IDR'),
            ('EUR', 'EUR'),
            ('GBP', 'GBP')
        ]
    )
    countryText = StringField(
        label='Country',
        description='Coutry where this fundraising take place',
        validators=[DataRequired(), Length(5,15)]
    )
    finishedDate = DateTimeField(
        label='End date',
        description='Date where the fundraising finishes.',
        format='%Y-%m-%d %H:%M:%S',
        validators=[DataRequired()],
        widget=DateTimeInput(),
        id='finishedDateTxt'
    )
    fundingDescription = TextAreaField(
        label='Fundraising description',
        validators=[DataRequired()]
    )
    fundingImageThumbnail = FileField(
        label='Upload fundraising thumbnail'
    )
    submit = SubmitField('Submit')