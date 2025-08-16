from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_delete_row_via_context_menu(chrome_driver, flask_port, datatable,
                                     wait_for_visible_element, session):
    """
    GIVEN a table with employment data displayed in the web application,
    WHEN the user deletes a row using the context menu,
    THEN the row is removed, and a success alert is displayed.
    """
    # ARRANGE: Wait for the table to load
    table = wait_for_visible_element(chrome_driver, (By.ID, 'employment-data'))

    # ARRANGE: Initialize ActionChains
    actions = ActionChains(chrome_driver)

    # ACT: Right-click the first cell to open the context menu
    first_cell = table.find_element(By.CSS_SELECTOR,
                                    'tbody tr:first-child td:first-child')
    actions.context_click(first_cell).perform()

    # ACT: Click "Remove" in the context menu
    remove_option = WebDriverWait(chrome_driver, 10).until(
        EC.element_to_be_clickable((
            By.XPATH,
            (
                "//li[contains(@class,'context-menu-item') and "
                "contains(.,'Remove')]"
            )
        ))
    )
    remove_option.click()

    # ACT: Handle confirmation alert
    WebDriverWait(chrome_driver, 10).until(EC.alert_is_present())
    confirm_alert = chrome_driver.switch_to.alert
    confirm_alert.accept()

    # ASSERT: Handle success alert and verify its text
    success_alert = WebDriverWait(chrome_driver, 10).until(
        EC.alert_is_present()
    )
    expected_message = "Row deleted successfully!"
    assert success_alert.text == expected_message, (
        f"Expected alert text '{expected_message}', "
        f"but got '{success_alert.text}'"
    )
    success_alert.accept()
