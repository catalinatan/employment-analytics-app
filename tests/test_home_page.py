import requests
from selenium.webdriver.common.by import By


def test_home_page_links(
    live_server, flask_port, chrome_driver, wait_for_visible_element
):
    """
    GIVEN a live server is running
    WHEN the home page is accessed
    THEN all href links should be accessible with status code 200 or 403
    """
    # ARRANGE: Set up the base URL and verify server availability
    base_url = f'http://127.0.0.1:{flask_port}'
    response = requests.get(base_url)
    assert response.status_code == 200

    # ACT: Load the home page in the browser and find all links
    chrome_driver.get(base_url)
    links = chrome_driver.find_elements(By.TAG_NAME, 'a')  # Find all <a> tags
    assert len(links) == 15  # Adjust expected count as needed

    # ASSERT: Verify each link is accessible
    for link in links:
        href = link.get_attribute('href')
        if href and not href.startswith('javascript'):
            response = requests.get(href)
            assert response.status_code in [200, 403], (
                f"Broken link: {href} (Status {response.status_code})"
            )
