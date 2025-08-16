from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait


# Test GET Requests
def test_predict_employment_trends_get(client, session):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/predict_employment_trends' page is requested via GET
    THEN the response contains the form with the correct fields
    """
    # ARRANGE: None needed for this test

    # ACT: Send GET request to the endpoint
    response = client.get('/predict_employment_trends')

    # ASSERT: Verify the response status and form fields
    assert response.status_code == 200
    assert b'<form' in response.data
    assert b'Region' in response.data
    assert b'Number of Years' in response.data
    assert b'Occupation Type' in response.data
    assert b'Additional Information' in response.data


# Test POST Requests
def test_predict_employment_trends_post_invalid(client, session):
    """
    GIVEN a Flask application configured for testing
    WHEN the form is submitted with missing required fields
    THEN the response shows validation errors
    """
    # ARRANGE: Prepare invalid form data
    invalid_data = {
        'no_of_years': 5,  # Missing required 'region' field
        'occupation_type': '1: managers, directors and senior officials'
    }

    # ACT: Send POST request with invalid data
    response = client.post('/predict_employment_trends', data=invalid_data)

    # ASSERT: Verify the response status and error messages
    assert response.status_code == 200
    assert b'This field is required' in response.data


def test_predict_employment_trends_invalid_years(client, session):
    """
    GIVEN a Flask application configured for testing
    WHEN the form is submitted with an invalid year range
    THEN the response shows validation errors
    """
    # ARRANGE: Prepare form data with invalid year range
    invalid_data = {
        'region': 'Wales',
        'no_of_years': 0,  # Invalid value
        'occupation_type': '1: managers, directors and senior officials'
    }

    # ACT: Send POST request with invalid data
    response = client.post('/predict_employment_trends', data=invalid_data)

    # ASSERT: Verify the response status and error messages
    assert response.status_code == 200
    assert b'Number must be at least 1' in response.data


# Test Valid Predictions
def test_predict_employment_trends(pred_emp_page, chrome_driver,
                                   wait_for_clickable_element,
                                   wait_for_visible_element, session):
    """
    GIVEN a user is on the prediction page
    WHEN they fill out the form with valid data and submit it
    THEN the prediction results and graph are displayed
    """
    # ARRANGE: Define CSS selectors for result elements
    pred_result_css = 'div.prediction-table'
    pred_graph_css = 'div.row h2.custom-location-header-style'

    # Wait for the form to be visible
    year_input = wait_for_visible_element(
        chrome_driver, (By.XPATH, '//input[@id="no_of_years"]')
    )

    actions = ActionChains(chrome_driver)

    # ACT: Fill out the form and submit it
    # Clear existing input and enter new value
    (actions.click(year_input)
            .send_keys('5')
            .perform())

    # Wait for input value update
    WebDriverWait(chrome_driver, 5).until(
        lambda d: year_input.get_attribute('value') == '5'
    )

    # Click submit button
    submit_button = wait_for_clickable_element(
        chrome_driver, (By.XPATH, '/html/body/div/div/div[1]/div/form/button')
    )
    submit_button.click()

    # ASSERT: Verify the results are displayed
    result_table = wait_for_visible_element(
        chrome_driver, (By.CSS_SELECTOR, pred_result_css)
    )
    result_graph = wait_for_visible_element(
        chrome_driver, (By.CSS_SELECTOR, pred_graph_css)
    )

    assert result_table.is_displayed()
    assert result_graph.is_displayed()
