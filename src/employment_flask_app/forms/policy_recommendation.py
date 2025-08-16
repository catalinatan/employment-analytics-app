from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, ValidationError
from employment_flask_app.models import PolicyRecommendation


class PolicyRecommendationForm(FlaskForm):
    # Field for employment disparity with validation and rendering options
    employment_disparity_field = StringField(
        'Employment Disparity',
        validators=[
            DataRequired(),
            Length(max=300)
        ],
        render_kw={'size': 150, 'maxlength': 300}
    )

    # Field for policy name with validation and rendering options
    policy_name_field = StringField(
        'Policy Name',
        validators=[
            DataRequired(),
            Length(max=50)
        ],
        render_kw={'size': 150, 'maxlength': 50}
    )

    # Field for policy description with validation and rendering options
    policy_description_field = StringField(
        'Policy Description',
        validators=[
            DataRequired(),
            Length(max=300)
        ],
        render_kw={'size': 150, 'maxlength': 300}
    )

    # Submit button for posting recommendations
    submit_recommendation = SubmitField('Post recommendation')

    # Dropdown for selecting a policy
    policy_id = SelectField('Policy', choices=[], coerce=int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.refresh_choices()  # Initial refresh

    def refresh_choices(self):
        """Refresh choices from database"""
        # Add default empty option
        self.policy_id.choices = [(-1, '-- Select Policy --')]

        # Query fresh from database
        policies = PolicyRecommendation.query.all()
        self.policy_id.choices += [
            (p.PolicyID, p.PolicyName) for p in policies
        ]

        # Update descriptions and feedback
        self.policy_descriptions = {
            p.PolicyID: p.PolicyDescription for p in policies
        }
        self.employment_disparity = {
            p.PolicyID: p.EmploymentDisparity for p in policies
        }
        self.policy_feedback = {
            p.PolicyID: [fb.PolicyFeedback for fb in p.PolicyFeedback]
            for p in policies
        }

    def validate_policy_id(self, field):
        """Custom validation for policy selection"""
        self.refresh_choices()  # Refresh choices before validation

        # -1 is our default empty value
        if field.data and field.data != -1:
            valid_ids = [choice[0] for choice in self.policy_id.choices]
            if field.data not in valid_ids:
                raise ValidationError(
                    'Please select a valid policy from the list'
                )
