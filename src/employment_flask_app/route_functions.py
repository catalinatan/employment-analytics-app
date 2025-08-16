from employment_flask_app.models import EmploymentData
from flask import redirect, url_for, flash
from sqlalchemy.exc import IntegrityError
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
import pandas as pd
import plotly.express as px
import markdown
import json
import re
from functools import wraps
from flask import (
    request, session, render_template
)


def password_protected(required_password):
    """
    This decorator ensures that a specific route is protected by requiring
    users to provide a password before accessing it. If the user is already
    authenticated for the route, they are allowed access. Otherwise, they
    are prompted to enter the password via a form.

    Parameters
    ----------
    required_password : str
        The password required to access the protected route.

    Returns
    -------
    function
        A decorated function that enforces password protection.

    Notes
    -----
    - The decorator uses Flask's `session` to store authentication status.
    - If the user provides the correct password, they are authenticated
        for the session and redirected to the same page.
    - If the password is incorrect, an error message is flashed, and the
        user remains on the login page.
    - The login form is rendered using the `password_prompt.html` template.

    Examples
    --------
    @app.route('/protected')
    @password_protected('my_secure_password')
    def protected_route():
        return "This is a password-protected route."
        """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if the user is already authenticated for this route
            if session.get('authenticated') == required_password:
                return func(*args, **kwargs)

            # Prompt for password if not authenticated
            if request.method == 'POST':
                provided_password = request.form.get('password')
                if provided_password == required_password:
                    session['authenticated'] = required_password
                    flash('Access granted!', 'success')
                    return redirect(request.url)  # Reload the page after login
                else:
                    flash('Invalid password. Access denied.', 'danger')

            # Render the login form if not authenticated
            return render_template('password_prompt.html')
        return wrapper
    return decorator


def insert_employment_data(df, db, EmploymentData, msg=None):
    """
    Inserts employment data from a DataFrame into the database.
    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing employment data to be inserted.
    db : SQLAlchemy
        The database instance for managing database operations.
    EmploymentData : SQLAlchemy.Model
        The database model representing the employment data table.
    msg : str, optional
        A message to display upon successful data upload (default is None).
    Returns
    -------
    flask.Response or None
        Redirects to an error page if an IntegrityError occurs, otherwise None.
    Notes
    -----
    - Rounds numerical values to specified precision before insertion.
    - Handles duplicate data gracefully by rolling back the transaction."""
    # Iterate through each row in the DataFrame
    for index, row in df.iterrows():
        # Create an EmploymentData object for each row with rounded values
        employment_data = EmploymentData(
            RegionName=row['Region'],
            Year=row['Year'],
            Gender=row['Gender'],
            OccupationType=row['Occupation Type'],
            EmploymentPercentage=round(
                row[
                    (
                        'Percentage Employed '
                        '(Relative to Total Employment in the Year)'
                    )
                    ], 2
                ),  # Round employment percentage to 2 decimal places
            # Round margin of error to 2 decimal places
            MarginofErrorPercentage=round(row['Margin of Error (%)'], 2),
            # Round longitude to 6 decimal places
            Longitude=round(row['Longitude'], 6),
            # Round latitude to 6 decimal places
            Latitude=round(row['Latitude'], 6)
        )

        try:
            # Add the employment data to the database session
            db.session.add(employment_data)
            # Commit the transaction to save the data
            db.session.commit()
            # Display a success message if a custom message is provided
            if msg:
                flash("Data uploaded successfully", "success")
        except IntegrityError:
            # Rollback the transaction in case of a database integrity error
            db.session.rollback()
            # Display an error message indicating duplicate data
            if msg:
                flash("Data already exists in the database.", "danger")
                # Redirect to the error page
                return redirect(url_for('starter.error'))


def process_prediction_response(response):
    """Processes the raw response from the AI model to extract and format
    prediction data.
    Parameters
    ----------
    response : requests.Response
        The raw response object from the AI model.
    Returns
    -------
    tuple
        A tuple containing:
        - prediction_result (str): The markdown-formatted prediction result.
        - forecast_data (pandas.DataFrame): The extracted forecast data as a
        DataFrame.
    Raises
    ------
    JSONDecodeError
        If the JSON parsing fails.
    Notes
    -----
    - Extracts JSON data from the response text using regex.
    - Converts the JSON data into a pandas DataFrame for further processing."""
    # Use raw response text for extraction
    # Remove "json" keyword and leading whitespace
    raw_text = response.text.replace("json", "").lstrip()

    # Search for JSON array pattern in the raw text
    json_match = re.search(r'\[(\s*\{.*?\}\s*,?)*\s*\]', raw_text, re.DOTALL)

    # If no valid JSON array is found, return an error message
    if not json_match:
        return "No valid JSON found"

    # Extract the matched JSON string
    json_str = json_match.group(0)

    try:
        # Convert the JSON string into a Python list of dictionaries
        data_list = json.loads(json_str)
        # Convert the list of dictionaries into a pandas DataFrame
        forecast_data = pd.DataFrame(data_list)
    except json.JSONDecodeError as e:
        # Handle JSON parsing errors and return the error message
        return f"JSON parsing error: {e}"

    # Convert the raw response text to markdown format for display
    prediction_result = markdown.markdown(raw_text)

    # Return the markdown-formatted prediction result and the
    # forecast DataFrame
    return prediction_result, forecast_data


def predict_employment_data(
    region,
    no_of_years,
    occupation_type,
    additional_info=None
        ):
    """Predicts employment data trends for a specified region and occupation
    type.
    Parameters
    ----------
    region : str
    The name of the region for which predictions are to be made.
    no_of_years : int
    The number of years to predict into the future.
    occupation_type : str
    The type of occupation for which predictions are to be made.
    additional_info : str, optional
    Additional information to include in the prediction prompt
    (default is None).
    Returns
    -------
    tuple
    A tuple containing:
    - prediction_result (str): The markdown-formatted prediction result.
    - forecast_data (pandas.DataFrame): The forecast data as a DataFrame.
    - starting_year (int): The first year of the prediction.
    - end_year (int): The last year of the prediction.
    Notes
    -----
    - Uses an AI model to generate predictions based on historical data.
    - Applies data preprocessing and error-aware forecasting techniques."""

    # Query the database for historical employment data for the specified
    # region and occupation type
    employment_data = EmploymentData.query.filter_by(
        RegionName=region,
        OccupationType=occupation_type
        ).all()

    # Convert the queried data into a list of dictionaries for easier
    # processing
    employment_data_list = [
        {
            "RegionName": data.RegionName,
            "Year": data.Year,
            "Gender": data.Gender,
            "OccupationType": data.OccupationType,
            "EmploymentPercentage": round(data.EmploymentPercentage, 2),
            "MarginofErrorPercentage": round(data.MarginofErrorPercentage, 2),
            "Longitude": round(data.Longitude, 6),
            "Latitude": round(data.Latitude, 6)
        }
        for data in employment_data
    ]

    # Determine the most recent year in the historical data, defaulting to
    # 2023 if no data exists
    most_recent_year = max([d.Year for d in employment_data], default=2023)
    # Calculate the starting year for predictions
    starting_year = most_recent_year + 1
    # Generate a list of years for the prediction range
    predicted_years = [starting_year + i for i in range(no_of_years)]
    # Calculate the ending year for predictions
    end_year = starting_year + no_of_years - 1

    # Initialize the AI client with the API key
    client = genai.Client(api_key="AIzaSyAg3clzL5xTIDHqbOSzLD2FlLLg0LMsllw")
    # Specify the AI model to use for predictions
    model_id = "gemini-2.0-flash"

    # Define a Google Search tool to assist with generating content
    google_search_tool = Tool(
        google_search=GoogleSearch()
    )

    # Construct the prompt for the AI model with detailed instructions and
    # historical data
    contents_prompt = f"""
    Analyze employment data with columns [RegionName, Year, Gender,
    OccupationType, EmploymentPercentage, MarginofErrorPercentage,
    Longitude, Latitude] to predict employment trends for {no_of_years} years
    starting from {starting_year}.

    Historical data for {region} ({occupation_type}):
    {employment_data_list}

    Follow this protocol:
    1. Generate one prediction per year for {predicted_years}.

    2. **Data Preprocessing**
    - Apply symmetric rounding (Round-Half-to-Even) for all values.
    - Handle missing values via seasonal-trend decomposition.
    - Enforce precision constraints:
    - EmploymentPercentage: 2 decimal places.
    - MarginofErrorPercentage: 2 decimal places.
    - Geocoordinates: 6 decimal places (~0.11m precision).

    3. **Error-Aware Forecasting**
    - Estimate the margin of error percentage as the average of past values:
    - Avg Margin of Error = ∑(Previous Margin of Errors) / Number of Years.

    Final output must follow these constraints:
    - Employment% rounded using bank rounding.
    - Margin% displayed with 2 decimal precision.
    - Fixed 6-decimal geocoordinates.
    - Gender must be Male or Female.

    Ensure the output always follows this structured format:
    "I will analyze the provided employment data for {region}
     ({occupation_type}) and generate a {no_of_years}-year forecast
     ({starting_year}-{starting_year + no_of_years - 1}) following the
     specified protocol."

    The forecast should include the following sections:
    The section headings must be exactly the same as the instructions provided.
    1. **Data Preprocessing Details** (symmetric rounding, missing value
    handling, precision constraints).
    2. **Error-Aware Forecasting** (margin of error calculations).
    3. **Trend Analysis & Forecasting Method** (linear trend analysis with
    yearly changes computed separately for males and females).
    4. **Final Forecast Table** (strictly matching a Markdown table format:
    this section should only contain a table with the following headings with
    the entries for each row
    Headings: RegionName, Year, Gender, OccupationType, Employment Percentage,
    MarginofErrorPercentage, Longitude, Latitude
    Columns separated by pipes (|) and rows separated by new lines.
    The first row and second row should be separated by a line of dashes ---
    (|-------|------|------|--------|-----------|-----------|-----|-----|)
    No other text should be included in this "Final Forecast Table" section.
    5. **DataFrame Output:**
    The "DataFrame Output" section must contain ONLY a JSON array of objects
    (list of dictionaries) for the "Final Forecast Table" data in the
    following format:
    {employment_data_list}
    No other text, headers, or formatting symbols are allowed in this section.

    Additionally, highlight key considerations:
    - **Data Limitations**: Forecast accuracy depends on available
    historical data.
    - **Linearity Assumption**: Trends may be influenced by external
    factors.
    - **Occupation & Region Specificity**: Results should not be
    generalized.
    - **Margin of Error Interpretation**: The constant margin of error
    assumption should be used cautiously.
    """
    # Append additional information to the prompt if provided
    if additional_info:
        contents_prompt += f"""
        Use the following additional information:
        {additional_info}
        """

    # Generate predictions using the AI model
    response = client.models.generate_content(
        model=model_id,
        contents=contents_prompt,
        config=GenerateContentConfig(
            tools=[google_search_tool],
            response_modalities=["TEXT"]
        )
    )
    # Process the AI model's response to extract prediction results and
    # forecast data
    prediction_result, forecast_data = process_prediction_response(response)

    # Return the prediction result, forecast data, and prediction range
    return prediction_result, forecast_data, starting_year, end_year


def create_predicted_bar_chart(forecast_data, region, starting_year, end_year):
    """Creates a bar chart visualization for predicted employment data.
    Parameters
    ----------
    forecast_data : pandas.DataFrame
        The DataFrame containing the forecasted employment data.
    region : str
        The name of the region for which the chart is created.
    starting_year : int
        The first year of the prediction range.
    end_year : int
        The last year of the prediction range.
    Returns
    -------
    plotly.graph_objects.Figure
        A Plotly bar chart figure visualizing the employment trends.
    Notes
    -----
    - Displays employment percentages by gender for each year.
    - Customizes the chart's appearance, including colors and axis labels."""

    # Create a stacked bar chart using Plotly Express
    fig = px.bar(
        forecast_data,
        x='Year',  # Set the x-axis to represent years
        # Set the y-axis to represent employment percentages
        y='EmploymentPercentage',
        color="Gender",  # Use gender to differentiate bars by color
        barmode="stack",  # Stack bars for each year
        title=(
            f"Employment Trends for {region} from "
            f"{starting_year} to {end_year}"
        ),  # Chart title
        # Define custom colors for genders
        color_discrete_map={'Female': '#B1172C', 'Male': '#4292C3'},
        hover_data={
            'Gender': True,  # Include gender information in hover tooltips
        },
    )

    # Update the layout of the chart
    fig.update_layout(
        title=dict(
            x=0.5,  # Center the title horizontally
            y=0.95,  # Move the title higher vertically (default is around 0.9)
            xanchor='center',  # Anchor the title at its center
            yanchor='top'  # Anchor the title at its top
        ),
        xaxis_title='Year',  # Label for the x-axis
        # Label for the y-axis
        yaxis_title=(
            'Percentage Employed (Relative to Total Employment in the Year)'
        ),
        yaxis=dict(
            title_font=dict(size=12)  # Set font size for the y-axis title
        ),
        xaxis=dict(
            tickmode='linear',  # Ensure ticks are linear
            dtick=1  # Set x-axis to show whole numbers only
        ),
        font=dict(color='#000000')  # Set font color for the chart
    )

    # Return the generated bar chart figure
    return fig
