from flask import current_app
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SubmitField, SelectField, DateTimeField, TextAreaField, FileField, DecimalField
from wtforms.validators import DataRequired, Length, InputRequired
from wtforms.widgets import DateTimeInput

class CreateFundingForm(FlaskForm):
    currencyChoices=[
            ('USD', 'USD'),
            ('IDR', 'IDR'),
            ('EUR', 'EUR'),
            ('GBP', 'GBP')
        ]
    fundraiserTitle = StringField(
        label='Fundraiser title', 
        validators=[DataRequired(), Length(10,50)],
        description='Add the title of your page.'
    )
    fundTypeSelect = SelectField(
        validate_choice=False,
        label='Fund Type',
        description='Select the funding type.'
    )
    currencySelect = SelectField(
        validate_choice=False,
        label='Currency',
        description='Currency used for this fundraising.',
        choices=currencyChoices
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
    targetAmount = DecimalField(
        label='Target Amount',
        description='Desired total amount of the fundraising.',
        validators=[InputRequired()]
    )
    fundingDescription = TextAreaField(
        label='Fundraising description',
        validators=[DataRequired()]
    )
    fundingImageThumbnail = FileField(
        label='Upload fundraising thumbnail'
    )
    submit = SubmitField('Submit')

    # def validate(self):
    #     # call the default validation method first from parent
    #     if not super(CreateFundingForm, self).validate():
    #         return False

    #     # if default validation has passed then start the custom validator

    def validate_finishedDate(self, field):
        input_date = field.data
        current_date = datetime.now()
        if input_date <= current_date + timedelta(days=3):
            raise ValidationError('Date should be at least more than 3 days later from current date')

