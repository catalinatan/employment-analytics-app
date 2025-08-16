from employment_flask_app import create_app
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask_testing import TestCase


class TestUnauthenticatedAccess(TestCase):
    def create_app(self):
        """
        GIVEN a Flask application configured for testing
        WHEN the application is created
        THEN it should be in testing mode
        """
        app = create_app()
        app.config['TESTING'] = True
        return app

    def test_unauthenticated_access(self):
        """
        GIVEN an unauthenticated user
        WHEN they attempt to access the policy recommendation page
        THEN they should be redirected to the password prompt page
        """
        # ARRANGE: None needed as this is an unauthenticated access test

        # ACT: Make a GET request to the policy recommendation page
        response = self.client.get('/policy_recommendation')

        # ASSERT: Verify the response and template used
        self.assert200(response)
        self.assert_template_used('password_prompt.html')


def test_successful_authentication(client):
    """
    GIVEN a user with the correct password
    WHEN they submit the password to the policy recommendation page
    THEN they should be authenticated and granted access
    """
    # ARRANGE: Define the correct password
    password_data = {'password': 'policyrecommendation'}

    # ACT: Post the password and follow redirects
    response = client.post('/policy_recommendation',
                           data=password_data,
                           follow_redirects=True)

    # ASSERT: Verify access and session authentication
    assert b'Access granted' in response.data
    with client.session_transaction() as sess:
        assert sess['authenticated'] == 'policyrecommendation'


def test_selenium_workflow(
    chrome_driver, policy_recommendation_page, wait_for_visible_element,
        wait_for_clickable_element,
        session):
    """
    GIVEN a user accessing the policy recommendation page
    WHEN they authenticate, fill out the form, and submit it
    THEN the policy should be added successfully
    """
    # ARRANGE: Authenticate with the correct password
    password_input = wait_for_visible_element(chrome_driver,
                                              (By.ID, "password-input"))
    password_input.send_keys("policyrecommendation")
    chrome_driver.find_element(By.ID, "submit-password").click()

    # ARRANGE: Fill out the form fields
    employment_disparity_field = wait_for_clickable_element(
        chrome_driver, (By.ID, "employment-disparity-field"))
    employment_disparity_field.click()
    employment_disparity_field.send_keys(
        "Scotland, 2023, Gender Disparity, 5.5"
    )

    policy_name_field = chrome_driver.find_element(By.ID, "policy-name-field")
    policy_name_field.click()
    policy_name_field.send_keys("Selenium Policy")

    policy_description_field = chrome_driver.find_element(
        By.ID, "policy-description-field")
    policy_description_field.click()
    policy_description_field.send_keys(
        "This policy was created using Selenium for testing purposes.")

    # ACT: Submit the form
    submit_button = chrome_driver.find_element(By.ID, "submit-recommendation")
    submit_button.click()

    # ASSERT: Verify the success message and policy presence
    WebDriverWait(chrome_driver, 10).until(
        EC.text_to_be_present_in_element((By.TAG_NAME, "body"),
                                         "Policy added successfully"))
    assert "Selenium Policy" in chrome_driver.page_source
