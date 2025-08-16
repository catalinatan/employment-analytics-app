from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    jsonify
)
from employment_flask_app.forms.upload_file import UploadFileForm
from employment_flask_app.forms.policy_recommendation import (
    PolicyRecommendationForm
)
from employment_flask_app.forms.policy_feedback import PolicyFeedbackForm
from employment_flask_app.forms.data_prediction import DataPredictForm
from employment_flask_app.models import (
    EmploymentData,
    PolicyRecommendation,
    PolicyFeedback
)
from employment_flask_app import db
from pathlib import Path
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import selectinload
import plotly.io as pio
import pandas as pd
from employment_flask_app.route_functions import (
    insert_employment_data,
    predict_employment_data,
    create_predicted_bar_chart,
    password_protected
)
from flask import send_file
from io import BytesIO

bp = Blueprint('starter', __name__)

data_path = Path(__file__).parent / 'data' / 'employment_prepared.xlsx'
ori_df = pd.read_excel(data_path)


@bp.route('/')
def index():
    # Insert initial employment data into the database from the prepared Excel
    # file
    insert_employment_data(ori_df, db, EmploymentData)
    # Render the index page with a welcome message
    return render_template('home.html')


@bp.route('/error')
def error():
    # Render the error page
    return render_template('error.html')


@bp.route('/datatable', methods=['GET', 'POST'])
def datatable():
    # Create an instance of the file upload form
    form = UploadFileForm()
    if form.validate_on_submit():
        # If the form is submitted and validated, process the uploaded file
        file = form.file.data
        if file:
            # Check the file extension and read the data accordingly
            if file.filename.endswith('.xlsx'):
                df = pd.read_excel(file)
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            # Insert the uploaded data into the EmploymentData table
            insert_employment_data(df, db, EmploymentData, msg=True)
    # Fetch all employment data from the database and convert it to an array
    # format
    # Handle export requests
    export_type = request.args.get('export')
    if export_type in ['csv', 'xlsx']:
        # Query all rows from EmploymentData table
        query = db.session.query(EmploymentData)

        # Convert SQLAlchemy query to pandas DataFrame
        df = pd.read_sql(
            sql=query.statement,
            con=db.engine  # Use the SQLAlchemy engine
        )

        # Create an in-memory file for export
        output = BytesIO()
        if export_type == 'csv':
            df.to_csv(output, index=False)
            mimetype = 'text/csv'
            filename = 'employment_data.csv'
        elif export_type == 'xlsx':
            with pd.ExcelWriter(output) as writer:
                df.to_excel(writer, index=False)
            mimetype = (
                'application/vnd.openxmlformats-officedocument.'
                'spreadsheetml.sheet'
            )
            filename = 'employment_data.xlsx'

        output.seek(0)
        return send_file(
            output,
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )

    employment_data = [data.to_array() for data in EmploymentData.query.all()]
    # Render the datatable page with the form and employment data
    return render_template('datatable.html',
                           form=form,
                           employment_data=employment_data)


@bp.route('/datatable/add', methods=['POST'])
def add_row():
    # Get the JSON data from the request
    data = request.get_json()

    # Create a new EmploymentData entry using the provided data
    new_entry = EmploymentData(
        RegionName=data.get('RegionName'),
        Year=data.get('Year'),
        Gender=data.get('Gender'),
        OccupationType=data.get('OccupationType'),
        EmploymentPercentage=data.get('EmploymentPercentage'),
        MarginofErrorPercentage=data.get('MarginofErrorPercentage'),
        Longitude=data.get('Longitude'),
        Latitude=data.get('Latitude')
    )

    # Add the new entry to the database session
    db.session.add(new_entry)

    # Commit the session to save the new entry in the database
    db.session.commit()

    # Return a success response with a redirect URL to the datatable page
    return jsonify({
        'status': 'success',
        'redirect_url': url_for('starter.datatable')
    })


@bp.route('/datatable/edit', methods=['PATCH'])
def edit_row():
    data = request.get_json()

    # Validate required fields
    if not all(key in data for key in ['lookupFields', 'updatedRowData']):
        return jsonify({'error': 'Missing required fields'}), 400

    lookup_fields = data['lookupFields']

    # Query record using lookup fields
    entry = EmploymentData.query.filter_by(**lookup_fields).first()

    if not entry:
        return jsonify({'error': 'Record not found'}), 404

    try:
        # Update all fields in updatedRowData dynamically
        for field, value in data['updatedRowData'].items():
            setattr(entry, field, value)

        db.session.commit()

        return jsonify({
            'status': 'success',
            'redirect_url': url_for('starter.datatable')
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/datatable/delete', methods=['POST'])
def delete_row():
    data = request.get_json()

    # Find the existing entry in the database
    entry_to_delete = EmploymentData.query.filter_by(
        RegionName=data.get('RegionName'),
        Year=data.get('Year'),
        Gender=data.get('Gender'),
        OccupationType=data.get('OccupationType'),
        EmploymentPercentage=data.get('EmploymentPercentage'),
        MarginofErrorPercentage=data.get('MarginofErrorPercentage'),
        Longitude=data.get('Longitude'),
        Latitude=data.get('Latitude')
    ).first()  # Get the first matching record

    if not entry_to_delete:
        return jsonify({'status': 'error', 'message': 'Entry not found'}), 404

    # Delete the existing entry
    db.session.delete(entry_to_delete)
    db.session.commit()

    return jsonify({
        'status': 'success',
        'redirect_url': url_for('starter.datatable')
    })


@bp.route('/policy_recommendation', methods=['GET', 'POST'])
@password_protected('policyrecommendation')
def policy_recommendation():
    # Create an instance of the policy recommendation form
    recommendation_form = PolicyRecommendationForm()

    # Check if the form is submitted and validated
    if recommendation_form.validate_on_submit():
        # Debug log to print form data
        print("Form data received:",
              recommendation_form.policy_name_field.data,
              recommendation_form.policy_description_field.data,
              recommendation_form.employment_disparity_field.data)
        try:
            # Create a new policy recommendation object
            policy = PolicyRecommendation(
                PolicyName=recommendation_form.policy_name_field.data,
                PolicyDescription=(
                    recommendation_form.policy_description_field.data
                ),
                EmploymentDisparity=(
                    recommendation_form.employment_disparity_field.data
                )
            )
            # Add the new policy to the database session and commit
            db.session.add(policy)
            db.session.commit()
            # Refresh the form choices after adding the new policy
            recommendation_form.refresh_choices()
            # Flash a success message
            flash("Policy added successfully", "success")
            # Redirect to the same page to display updated data
            return redirect(url_for('starter.policy_recommendation'))
        except IntegrityError as e:
            # Handle unique constraint violation for policy name
            db.session.rollback()
            flash(f"Policy name must be unique: {str(e)}", "danger")
        except SQLAlchemyError as e:
            # Handle other database errors
            db.session.rollback()
            flash(f"Database error: {str(e)}", "danger")
            # return redirect(url_for('starter.error'))
    else:
        # If form validation fails, flash the validation errors
        if recommendation_form.errors:
            flash(f"Form validation errors: {recommendation_form.errors}",
                  "danger")

    # Fetch all policies from the database, including their feedback, and
    # order them by ID in descending order
    policies = PolicyRecommendation.query.options(
        selectinload(PolicyRecommendation.PolicyFeedback)
    ).order_by(PolicyRecommendation.PolicyID.desc()).all()

    # Debug log to print fetched policies
    print("Policies fetched:", [p.to_array() for p in policies])

    # Render the policy recommendation page with the form and policies
    return render_template(
        'policy_rec.html',
        recommendation_form=recommendation_form,
        policies=[p.to_array() for p in policies]
    )


@bp.route('/policy_feedback', methods=['GET', 'POST'])
@password_protected('policyfeedback')
def policy_feedback():
    # Create an instance of the policy feedback form
    feedback_form = PolicyFeedbackForm()

    # Populate the policy_id choices dynamically from the database
    feedback_form.policy_id.choices = [
        (p.PolicyID, p.PolicyName) for p in PolicyRecommendation.query.all()
    ]

    # Check if the form is submitted and validated
    if feedback_form.validate_on_submit():
        try:
            # Create a new policy feedback object
            feedback = PolicyFeedback(
                PolicyID=feedback_form.policy_id.data,
                PolicyRating=feedback_form.rating_field.data,
                PolicyFeedback=feedback_form.feedback_field.data
            )
            # Add the new feedback to the database session and commit
            db.session.add(feedback)
            db.session.commit()
            # Flash a success message
            flash("Feedback submitted", "success")
            # Redirect to the same page to display updated feedback
            return redirect(url_for('starter.policy_feedback'))
        except SQLAlchemyError as e:
            # Handle database errors
            db.session.rollback()
            flash(f"Error: {str(e)}", "danger")
            # return redirect(url_for('starter.error'))

    # Fetch the latest 50 feedback entries from the database, ordered by ID in
    # descending order
    feedbacks = PolicyFeedback.query.order_by(
        PolicyFeedback.FeedbackID.desc()
    ).limit(50).all()

    # Render the policy feedback page with the form and feedback entries
    return render_template('policy_feedback.html',
                           feedback_form=feedback_form,
                           feedbacks=[f.to_array() for f in feedbacks])


@bp.route('/predict_employment_trends', methods=['GET', 'POST'])
def predict_employment_trends():
    # Create an instance of the data prediction form
    form = DataPredictForm()
    prediction_result = None  # Initialize the prediction result
    graph_html = None  # Initialize the HTML for the graph
    forecast_data = None  # Initialize the forecast data

    # Check if the form is submitted and validated
    if form.validate_on_submit():
        # Extract form data
        region = form.region.data
        no_of_years = form.no_of_years.data
        occupation_type = form.occupation_type.data
        additional_info = form.additional_info.data

        # Predict employment data with or without additional information
        prediction_result, forecast_data, starting_year, end_year = (
            predict_employment_data(
                region,
                no_of_years,
                occupation_type,
                additional_info if additional_info else None
            )
        )

        # If forecast data is not empty, create a bar chart
        graph_html = ""
        if not forecast_data.empty:
            fig = create_predicted_bar_chart(
                forecast_data, region, starting_year, end_year
            )
            graph_html = pio.to_html(fig, full_html=False)

    # Render the data prediction page with the form, prediction result, graph,
    # and forecast data
    return render_template(
        'data_prediction.html',
        form=form,
        prediction_result=prediction_result,
        graph_html=graph_html,
        forecast_data=forecast_data
    )
