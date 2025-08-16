from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, IntegerField
from wtforms.validators import InputRequired, NumberRange


# Defining a form class for predicting employment data
class DataPredictForm(FlaskForm):
    # Dropdown field for selecting a region
    region = SelectField(
        'Region',  # Label for the field
        choices=[  # List of options for the dropdown
            ('England', 'England'),
            ('Northern Ireland', 'Northern Ireland'),
            ('Wales', 'Wales'),
            ('Scotland', 'Scotland')
        ],
        validators=[InputRequired(message="This field is required")]  # Ensures the field is not left empty
    )

    # Integer field for specifying the number of years
    no_of_years = IntegerField(
        'Number of Years',  # Label for the field
        validators=[
            InputRequired(message="This field is required"), # Ensures the field is not left empty
            NumberRange(
                min=1,
                message='Number must be at least 1'
            )  # Ensures the value is at least 1
        ],
        render_kw={'min': 1, 'max': 10}  # HTML attributes for the input field
    )

    # Dropdown field for selecting an occupation type
    occupation_type = SelectField(
        'Occupation Type',  # Label for the field
        choices=[  # List of options for the dropdown
            ('1: managers, directors and senior officials',
             '1: Managers, directors and senior officials'),
            ('2: professional occupations',
             '2: Professional occupations'),
            ('3: associate prof & tech occupations',
             '3: Associate prof and tech occupations'),
            ('4: administrative and secretarial occupations',
             '4: Administrative and secretarial occupations'),
            ('5: skilled trades occupations',
             '5: Skilled trades occupations'),
            ('6: caring, leisure and other service occupations',
             '6: Caring, leisure and other service occupations'),
            ('7: sales and customer service occupations',
             '7: Sales and customer service occupations'),
            ('8: process, plant and machine operatives',
             '8: Process, plant and machine operatives')
        ],
        validators=[InputRequired(message="This field is required")]  # Ensures the field is not left empty
    )

    # Text field for providing additional information
    additional_info = StringField(
        'Additional Information',  # Label for the field
        # HTML attributes for the input field
        render_kw={'size': 150, 'maxlength': 600}
    )

    # Submit button for the form
    submit = SubmitField('Predict Employment Data')  # Label for the button
