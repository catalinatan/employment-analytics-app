from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import ValidationError, InputRequired


# Custom validator to check the file extension
def check_file_extension(form, file_field):
    file_name = file_field.data.filename
    # Allow only .xlsx or .csv file extensions
    if file_name.endswith('.xlsx') or file_name.endswith('.csv'):
        return True
    else:
        # Raise a validation error if the file extension is not allowed
        raise ValidationError("File must be in .xlsx or .csv format")


# Form class for file upload
class UploadFileForm(FlaskForm):
    # File field with input required and custom file extension validator
    file = FileField("File", [InputRequired(), check_file_extension])
    # Submit button for the form
    submit = SubmitField("Upload File")
