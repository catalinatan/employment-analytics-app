from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired
from employment_flask_app.models import PolicyRecommendation


class PolicyFeedbackForm(FlaskForm):
    # Dropdown field to select a policy, choices will be populated dynamically
    policy_id = SelectField('Policy', choices=[], coerce=int)

    # Text field for users to provide feedback, with size and character limit
    feedback_field = StringField(
        'Feedback',
        validators=[DataRequired()],
        render_kw={'size': 150, 'maxlength': 600}
    )

    # Integer field for users to provide a rating between 1 and 5
    rating_field = IntegerField(
        'Rating (1-5)',
        validators=[DataRequired()],
        render_kw={'min': 1, 'max': 5}
    )

    # Submit button to post the feedback
    submit_feedback = SubmitField('Post feedback')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate choices AFTER app context exists
        self.policy_id.choices = [
            (p.PolicyID, p.PolicyName)
            for p in PolicyRecommendation.query.all()
        ]

        # Add descriptions as a dictionary for use in the frontend
        self.policy_descriptions = {
            p.PolicyID: p.PolicyDescription
            for p in PolicyRecommendation.query.all()
        }

        # Add descriptions as a dictionary for use in the frontend
        self.employment_disparity_descriptions = {
            p.PolicyID: p.EmploymentDisparity
            for p in PolicyRecommendation.query.all()
        }
