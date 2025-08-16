from selenium.webdriver.common.by import By
import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import ElementClickInterceptedException


def test_datatable_initialisation(
    live_server, flask_port, chrome_driver, wait_for_visible_element, session
):
    """
    GIVEN a live server is running
    WHEN a GET HTTP request is made to the datatable page
    THEN the HTTP response should have a status code of 200 and the table
    headers should match the expected values.
    """
    # ARRANGE: Set up the URL for the datatable page
    url = f'http://127.0.0.1:{flask_port}/datatable'

    # ACT: Send a GET request to the server and verify the response
    response = requests.get(url)
    assert response.status_code == 200

    # ACT: Open the datatable page in the browser
    chrome_driver.get(url)

    # ARRANGE: Wait until all header elements are visible
    headers_elements = wait_for_visible_element(
        chrome_driver, (By.CSS_SELECTOR, '#employment-data thead th')
    )

    # ACT: Extract headers after waiting
    headers_elements = chrome_driver.find_elements(
        By.CSS_SELECTOR, '#employment-data thead th'
    )
    headers = [header.text for header in headers_elements]

    # ASSERT: Verify that the headers match the expected values
    expected_headers = [
        "Region Name", "Year", "Gender", "Occupation Type",
        "Employment Percentage", "Margin of Error Percentage",
        "Longitude", "Latitude"
    ]
    assert headers == expected_headers


def test_table_pagination(
    chrome_driver, flask_port, datatable, wait_for_visible_element,
    wait_for_clickable_element, session
):
    """
    GIVEN a datatable with pagination is displayed
    WHEN the next page button is clicked
    THEN the table should display the next set of rows and update the status
    text accordingly.
    """
    # ARRANGE: Wait for pagination controls to load
    pagination_controls = wait_for_visible_element(
        chrome_driver, (By.CSS_SELECTOR, 'div.dataTables_paginate')
    )
    assert pagination_controls is not None, "Pagination controls did not load."

    # ARRANGE: Verify initial status text
    status_text = chrome_driver.find_element(
        By.CSS_SELECTOR, '#employment-data_info'
    ).text
    assert "Showing 1 to 10 of" in status_text, (
        f"Initial status text is incorrect: {status_text}"
    )

    # ARRANGE: Ensure the next page button is visible and scroll into view
    next_page_button = wait_for_visible_element(
        chrome_driver, (By.CSS_SELECTOR, 'a.paginate_button.next')
    )
    chrome_driver.execute_script(
        "arguments[0].scrollIntoView(true);", next_page_button
    )

    # ACT: Wait for the button to be clickable
    next_page_button = wait_for_clickable_element(
        chrome_driver, (By.CSS_SELECTOR, 'a.paginate_button.next')
    )

    # ACT: Retry clicking if intercepted
    try:
        next_page_button.click()
    except ElementClickInterceptedException:
        # Handle overlay or blocking element
        chrome_driver.execute_script("arguments[0].click();", next_page_button)

    # ACT: Wait for the status text to update
    WebDriverWait(chrome_driver, 10).until(
        lambda d: "Showing 11 to 20 of" in d.find_element(
            By.CSS_SELECTOR, '#employment-data_info'
        ).text
    )

    # ASSERT: Verify updated status text
    updated_status_text = chrome_driver.find_element(
        By.CSS_SELECTOR, '#employment-data_info'
    ).text
    assert "Showing 11 to 20 of" in updated_status_text, (
        f"Updated status text is incorrect: {updated_status_text}"
    )


def test_table_sorting(
    chrome_driver, flask_port, datatable, wait_for_visible_element
):
    """
    GIVEN a datatable is displayed
    WHEN the header of the first column is clicked
    THEN the table should be sorted based on the values in that column.
    """
    # ARRANGE: Wait for the table to load
    table = wait_for_visible_element(chrome_driver, (By.ID, 'employment-data'))

    # ARRANGE: Locate the header of the first column
    header = table.find_element(By.CSS_SELECTOR, 'thead th:first-child')

    # ACT: Click on the header to sort the table
    header.click()

    # ACT: Wait for DataTable sorting to complete
    WebDriverWait(chrome_driver, 10).until(
        lambda d: d.execute_script(
            "return $.fn.dataTable.isDataTable('#employment-data') && "
            "$('#employment-data').DataTable().rows().count() > 0"
        )
    )

    # ASSERT: Verify that the table is sorted correctly
    sorted_cells = chrome_driver.find_elements(
        By.CSS_SELECTOR, 'tbody tr td:first-child'
    )
    assert sorted_cells == sorted(
        sorted_cells, key=lambda x: x.text
    ), "Table is not sorted correctly."
