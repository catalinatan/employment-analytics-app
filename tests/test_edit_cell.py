from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_edit_cell_and_verify_update(chrome_driver, flask_port, datatable,
                                     wait_for_visible_element, session):
    """
    GIVEN a loaded datatable with editable cells,
    WHEN a cell is edited and the table is searched,
    THEN the updated value should be reflected in the search results.
    """
    # ARRANGE: Wait for the table to load
    table = wait_for_visible_element(chrome_driver, (By.ID, 'employment-data'))

    # ARRANGE: Initialize ActionChains
    actions = ActionChains(chrome_driver)

    # ACT: Double-click the first cell to enable editing
    first_cell = table.find_element(
        By.CSS_SELECTOR, 'tbody tr:first-child td:first-child'
    )
    actions.double_click(first_cell).perform()

    # ACT: Edit the input field with the new value
    input_field = wait_for_visible_element(
        chrome_driver, (By.CSS_SELECTOR, '.edit-input')
    )
    (actions
     .click(input_field)  # Ensure focus
     .key_down(Keys.CONTROL)  # Use Command for Mac
     .send_keys('a')  # Select all text (Ctrl+A)
     .key_up(Keys.CONTROL)  # Use Command for Mac
     .send_keys(Keys.DELETE)  # Clear field
     .send_keys("Updated Region")  # Enter new value
     .send_keys(Keys.RETURN)  # Commit edit
     .pause(0.5)  # Wait for update propagation
     .perform())

    # ARRANGE: Wait for the search input to load
    search_input = WebDriverWait(chrome_driver, 10).until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, 'div.dataTables_filter input[type="search"]')
        )
    )

    # ACT: Search for the updated value
    search_query = "Updated Region"
    (actions
     .click(search_input)
     .send_keys(search_query)
     .pause(0.5)  # Wait for search results
     .perform())

    # ASSERT: Verify the table updates with search results
    WebDriverWait(chrome_driver, 10).until(
        EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, 'tbody tr:first-child td:first-child'),
            search_query
        )
    )
    first_cell_text = chrome_driver.find_element(
        By.CSS_SELECTOR, 'tbody tr:first-child td:first-child'
    ).text
    assert search_query in first_cell_text, (
        f"Search results do not match query '{search_query}'."
    )
