from employment_flask_app import create_app, db
from employment_flask_app.models import PolicyRecommendation
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask_testing import TestCase
import pandas as pd
from selenium.webdriver.support.ui import Select


class TestUnauthenticatedAccess(TestCase):
    """
    GIVEN an unauthenticated user
    WHEN they access the policy feedback page
    THEN they should see the password prompt page
    """
    def create_app(self):
        app = create_app()
        app.config['TESTING'] = True
        return app

    def test_unauthenticated_access(self):
        # ARRANGE: None needed for this test

        # ACT: Access the policy feedback page
        response = self.client.get('/policy_feedback')

        # ASSERT: Verify the correct response and template
        self.assert200(response)
        self.assert_template_used('password_prompt.html')


def test_selenium_workflow(
    chrome_driver, policy_feedback_page, wait_for_visible_element,
    wait_for_clickable_element, session, app
):
    """
    GIVEN a set of policy recommendations in the database
    WHEN a user submits feedback for a policy via the UI
    THEN the feedback should be submitted successfully
    """
    # ARRANGE: Prepare sample policy recommendation data
    pol_rec_data = {
        "EmploymentDisparity": [
            "Employment Disparity Description A",
            "Employment Disparity Description B",
            "Employment Disparity Description C"
        ],
        "PolicyName": [
            "Policy A",
            "Policy B",
            "Policy C"
        ],
        "PolicyDescription": [
            "Description of Policy A",
            "Description of Policy B",
            "Description of Policy C"
        ]
    }
    df = pd.DataFrame(pol_rec_data)

    # Insert data into the database
    with app.app_context():
        for _, row in df.iterrows():
            recommendation = PolicyRecommendation(
                EmploymentDisparity=row["EmploymentDisparity"],
                PolicyName=row["PolicyName"],
                PolicyDescription=row["PolicyDescription"]
            )
            db.session.add(recommendation)
        db.session.commit()

    # ACT: Perform UI interactions using Selenium
    # Enter password and submit
    wait_for_visible_element(chrome_driver, (By.ID, "password-input"))\
        .send_keys("policyfeedback")
    chrome_driver.find_element(By.ID, "submit-password").click()

    # Wait for policy dropdown to load and select a policy
    policy_dropdown = wait_for_clickable_element(chrome_driver,
                                                 (By.ID, "policy-dropdown"))
    policy_dropdown = Select(policy_dropdown)

    # ASSERT: Verify the dropdown contains the correct number of options
    policy_options = policy_dropdown.options
    assert len(policy_options) == 3, "Expected 3 policy options"

    # Select Policy A
    policy_dropdown.select_by_visible_text("Policy A")

    # Fill out feedback field
    feedback_field = chrome_driver.find_element(By.XPATH,
                                                '//*[@id="feedback-field"]')
    feedback_field.click()
    feedback_field.send_keys(
        "This policy could be improved by considering D and C."
    )

    # Fill out rating field
    rating_field = chrome_driver.find_element(By.XPATH,
                                              '//*[@id="rating-field"]')
    rating_field.click()
    rating_field.send_keys("1")

    # Submit the form
    submit_button = chrome_driver.find_element(By.ID, "submit-feedback")
    submit_button.click()

    # ASSERT: Verify feedback confirmation message
    WebDriverWait(chrome_driver, 10).until(
        EC.text_to_be_present_in_element((By.TAG_NAME, "body"),
                                         "Feedback submitted")
    )
    body_text = chrome_driver.find_element(By.TAG_NAME, "body").text
    assert "Feedback submitted" in body_text
