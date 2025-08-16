from selenium.webdriver.common.by import By
from datetime import datetime


def test_add_button_exists(datatable):
    """
    Given a datatable fixture that loads the page,
    When the 'Add Row' button is located by its ID,
    Then verify that the button is visible and has the correct text.
    """
    # ARRANGE: The datatable fixture already loaded the page

    # ACT: Locate the 'Add Row' button by its ID
    btn = datatable.find_element(By.ID, 'add-row')

    # ASSERT: Verify button properties
    assert btn.is_displayed(), "Add button should be visible"
    assert btn.text == 'Add Row', "Button text should match expected"


def test_add_row_endpoint(client, session):
    """
    GIVEN a test client and a database session,
    WHEN a POST request is sent to the '/datatable/add' endpoint with
    valid data,
    THEN verify that the response status is 200 and the operation is
    successful.
    """
    # ARRANGE: Prepare test data and timestamp
    timestamp = datetime.now().isoformat(timespec='milliseconds') + 'Z'
    test_data = {
        "RegionName": f"New Region {timestamp}",
        "Year": 2025,
        "Gender": "Female",
        "OccupationType": "New Occupation",
        "EmploymentPercentage": 0.00,
        "MarginofErrorPercentage": 0.00,
        "Longitude": 0.00,
        "Latitude": 0.00
    }

    # ACT: Send POST request to the '/datatable/add' endpoint
    response = client.post('/datatable/add', json=test_data)

    # ASSERT: Verify response status and success message
    assert response.status_code == 200, "Response status should be 200"
    assert response.json['status'] == 'success', \
        "Response status should indicate success"
