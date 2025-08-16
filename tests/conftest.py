# Copied from Flask documentation: https://flask.palletsprojects.com/en/stable/
# testing/
import pytest
from employment_flask_app import create_app
from employment_flask_app import db
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import socket
import subprocess
import time
import pandas as pd
from employment_flask_app.models import EmploymentData
from employment_flask_app.route_functions import insert_employment_data
from io import StringIO

csv_data = """Region,Year,Gender,Occupation Type,Percentage Employed (Relative\
 to Total Employment in the Year),Margin of Error (%),Latitude,Longitude
England,2021,Male,"1: managers, directors and senior officials",7.28000021,\
0.01,53.07497,-1.46618
England,2021,Male,2: professional occupations,12.89000034,0.01,53.07497,
-1.46618
England,2021,Male,3: associate prof & tech occupations,7.070000172,0.01,\
53.07497,-1.46618
England,2021,Male,4: administrative and secretarial occupations,2.640000105,\
0.01,53.07497,-1.46618
England,2021,Male,5: skilled trades occupations,7.920000076,0.01,53.07497,\
-1.46618
England,2021,Male,"6: caring, leisure and other service occupations",\
1.75999999,0,53.07497,-1.46618
England,2021,Male,7: sales and customer service occupations,2.670000076,0.01,\
53.07497,-1.46618
England,2021,Male,"8: process, plant and machine operatives",5.210000038,0.01,\
53.07497,-1.46618
England,2021,Male,9: elementary occupations,4.949999809,0.01,53.07497,-1.46618
England,2021,Female,"1: managers, directors and senior officials",4.28000021,\
0.01,53.07497,-1.46618
England,2021,Female,2: professional occupations,12.64000034,0.01,53.07497,\
-1.46618
England,2021,Female,3: associate prof & tech occupations,6.440000057,0.01,\
53.07497,-1.46618
England,2021,Female,4: administrative and secretarial occupations,7.260000229,\
0.01,53.07497,-1.46618
England,2021,Female,5: skilled trades occupations,1.120000005,0,53.07497,\
-1.46618
England,2021,Female,"6: caring, leisure and other service occupations",\
6.889999866,0.01,53.07497,-1.46618
England,2021,Female,7: sales and customer service occupations,3.920000076,\
0.01,53.07497,-1.46618
England,2021,Female,"8: process, plant and machine operatives",0.829999983,0,\
53.07497,-1.46618
England,2021,Female,9: elementary occupations,4.21999979,0.01,53.07497,-1.46618
England,2022,Male,"1: managers, directors and senior officials",7.130000114,\
0.01,53.07497,-1.46618
England,2022,Male,2: professional occupations,13.30000019,0.01,53.07497,\
-1.46618
England,2022,Male,3: associate prof & tech occupations,7.300000191,0.01,\
53.07497,-1.46618
England,2022,Male,4: administrative and secretarial occupations,2.480000019,\
0.01,53.07497,-1.46618
England,2022,Male,5: skilled trades occupations,7.889999866,0.01,53.07497,\
-1.46618
England,2022,Male,"6: caring, leisure and other service occupations",\
1.860000014,0.01,53.07497,-1.46618
England,2022,Male,7: sales and customer service occupations,2.50999999,0.01,\
53.07497,-1.46618
England,2022,Male,"8: process, plant and machine operatives",5.110000134,0.01,\
53.07497,-1.46618
England,2022,Male,9: elementary occupations,4.829999924,0.01,53.07497,-1.46618
England,2022,Female,"1: managers, directors and senior officials",4.170000076,\
0.01,53.07497,-1.46618
England,2022,Female,2: professional occupations,12.89000034,0.01,53.07497,\
-1.46618
England,2022,Female,3: associate prof & tech occupations,6.769999981,0.01,\
53.07497,-1.46618
England,2022,Female,4: administrative and secretarial occupations,7.289999962,\
0.01,53.07497,-1.46618
England,2022,Female,5: skilled trades occupations,0.99000001,0,53.07497,\
-1.46618
England,2022,Female,"6: caring, leisure and other service occupations",\
6.46999979,0.01,53.07497,-1.46618
England,2022,Female,7: sales and customer service occupations,3.819999933,\
0.01,53.07497,-1.46618
England,2022,Female,"8: process, plant and machine operatives",0.790000021,0,\
53.07497,-1.46618
England,2022,Female,9: elementary occupations,4.389999866,0.01,53.07497,\
-1.46618
England,2023,Male,"1: managers, directors and senior officials",7.059999943,\
0.01,53.07497,-1.46618
England,2023,Male,2: professional occupations,14.14999962,0.01,53.07497,\
-1.46618
England,2023,Male,3: associate prof & tech occupations,7.659999847,0.01,\
53.07497,-1.46618
England,2023,Male,4: administrative and secretarial occupations,2.569999933,\
0.01,53.07497,-1.46618
England,2023,Male,5: skilled trades occupations,7.639999866,0.01,53.07497,\
-1.46618
England,2023,Male,"6: caring, leisure and other service occupations",\
1.620000005,0,53.07497,-1.46618
England,2023,Male,7: sales and customer service occupations,2.450000048,0.01,\
53.07497,-1.46618
England,2023,Male,"8: process, plant and machine operatives",4.670000076,0.01,\
53.07497,-1.46618
England,2023,Male,9: elementary occupations,4.789999962,0.01,53.07497,-1.46618
England,2023,Female,"1: managers, directors and senior officials",4.130000114,\
0.01,53.07497,-1.46618
England,2023,Female,2: professional occupations,12.96000004,0.01,53.07497,\
-1.46618
England,2023,Female,3: associate prof & tech occupations,7.449999809,0.01,\
53.07497,-1.46618
England,2023,Female,4: administrative and secretarial occupations,6.989999771,\
0.01,53.07497,-1.46618
England,2023,Female,5: skilled trades occupations,0.980000019,0,53.07497,\
-1.46618
England,2023,Female,"6: caring, leisure and other service occupations",6.25,\
0.01,53.07497,-1.46618
England,2023,Female,7: sales and customer service occupations,3.650000095,\
0.01,53.07497,-1.46618
England,2023,Female,"8: process, plant and machine operatives",0.680000007,0,\
53.07497,-1.46618
England,2023,Female,9: elementary occupations,4.320000172,0.01,53.07497,\
-1.46618"""

sample_df = pd.read_csv(StringIO(csv_data))


@pytest.fixture(scope='function')
def app():
    """
    Fixture to set up and tear down a Flask application for testing.

    This fixture creates a Flask application instance with a testing
    configuration, including an in-memory SQLite database. It initializes the
    database, inserts sample employment data, and ensures proper cleanup after
    each test.

    Yields
    ------
    Flask : Flask application instance
        The configured Flask application instance for testing.

    Notes
    -----
    - The database is created and populated with sample data before yielding
    the app.
    - After the test, the database session is closed, all tables are dropped,
    and the database engine is disposed to ensure a clean state for subsequent
    tests.
    """
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False
    })

    with app.app_context():
        db.create_all()
        insert_employment_data(sample_df, db, EmploymentData)
    yield app

    with app.app_context():
        db.session.close()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture(scope='function', autouse=True)
def session(app):
    """
    Provides a database session for use in tests within the application
    context.

    This function sets up a nested database session within the application's
    context, yields it for use, and ensures that any changes made during the
    session are rolled back after the test completes.

    Parameters
    ----------
    app : Flask
        The Flask application instance.

    Yields
    ------
    sqlalchemy.orm.Session
        A database session object for use in tests.
    """
    with app.app_context():
        db.session.begin_nested()
        yield db.session
        db.session.rollback()


@pytest.fixture
def runner(app):
    """
    Creates and returns a test CLI runner for the given Flask application.

    Parameters
    ----------
    app : Flask
        The Flask application instance for which the test CLI runner is
        created.

    Returns
    -------
    FlaskCliRunner
        A test CLI runner instance that can be used to invoke CLI commands
        for the provided Flask application.
    """
    return app.test_cli_runner()


@pytest.fixture
def client(app):
    """
    Creates and returns a test client for the given Flask application.

    Parameters
    ----------
    app : Flask
        The Flask application instance for which the test client is created.

    Returns
    -------
    FlaskClient
        A test client instance that can be used to simulate HTTP requests to
        he application.
    """
    return app.test_client()


def pytest_configure(config):
    """
    Configure pytest settings during the initialization phase.

    This function is automatically called by pytest to allow customization
    of the testing environment. In this case, it adds a filter to suppress
    specific warnings during test execution.

    Parameters
    ----------
    config : _pytest.config.Config
        The pytest configuration object that provides access to various
        settings and options for the test session.

    Notes
    -----
    - The `filterwarnings` line is used to ignore warnings of type
      `pytest.PytestUnraisableExceptionWarning`.
    - This customization is useful for reducing noise in the test output
      caused by specific warnings that are not relevant to the test results.
    """
    config.addinivalue_line(
        "filterwarnings",
        "ignore::pytest.PytestUnraisableExceptionWarning"
    )


@pytest.fixture(scope="module")
def chrome_driver():
    """
    chrome_driver
    A pytest fixture that initializes and provides a Chrome WebDriver instance
    for testing purposes.

    The WebDriver is configured differently depending on whether the code is
    running in a GitHub Actions environment or locally.

    The fixture ensures that the WebDriver instance is properly closed after
    use.

    Yields
    ------
    selenium.webdriver.Chrome
        An instance of Chrome WebDriver configured with the appropriate
        options.
    Notes
    -----
    - In a GitHub Actions environment, the WebDriver is configured to run in
    headless mode with additional
    options to disable GPU and sandboxing for compatibility.
    - Locally, the WebDriver is configured to start maximized for better
    visibility during testing.
    """
    options = ChromeOptions()
    if "GITHUB_ACTIONS" in os.environ:
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")
    else:
        options.add_argument("start-maximized")
    driver = Chrome(options=options)
    yield driver
    driver.quit()


@pytest.fixture(scope="session")
def flask_port():
    """
    Gets a free port from the operating system.

    Returns
    -------
    int
        A free port number that can be used for binding a socket.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        addr = s.getsockname()
        port = addr[1]
        return port


@pytest.fixture(scope="session")
def live_server(flask_port):
    """Runs the Flask app as a live server for Selenium tests (Paralympic app).

    Parameters
    ----------
    flask_port : int
        The port number on which the Flask app will run.

    Yields
    ------
    subprocess.Popen
        A subprocess running the Flask app.

    Raises
    ------
    subprocess.CalledProcessError
        If there is an error starting the Flask app.
    """
    # Construct the command string to run flask with formatted dictionary
    command = (
        f"flask --app 'employment_flask_app:create_app("
        f"test_config={{\"TESTING\": True, "
        f"\"WTF_CSRF_ENABLED\": False}})' run "
        f"--port {flask_port}"
    )

    try:
        server = subprocess.Popen(command, shell=True)
        # Allow time for the app to start
        time.sleep(3)
        yield server
        server.terminate()
    except subprocess.CalledProcessError as e:
        print(f"Error starting Flask app: {e}")


@pytest.fixture
def datatable(live_server, flask_port, chrome_driver):
    """
    Fixture to navigate to the datatable page.

    Parameters
    ----------
    live_server : pytest fixture
        The live server instance for testing.
    flask_port : int
        The port number on which the Flask application is running.
    chrome_driver : selenium.webdriver.Chrome
        The Chrome WebDriver instance for browser automation.

    Returns
    -------
    selenium.webdriver.Chrome
        The Chrome WebDriver instance after navigating to the datatable page.
    """
    url = f'http://127.0.0.1:{flask_port}/datatable'
    chrome_driver.get(url)
    return chrome_driver


@pytest.fixture
def pred_emp_page(live_server, flask_port, chrome_driver):
    """
    Fixture to navigate to the predict employment trends page.

    Parameters
    ----------
    live_server : flask.testing.FlaskClient
        The live server instance for testing.
    flask_port : int
        The port number on which the Flask application is running.
    chrome_driver : selenium.webdriver.Chrome
        The Chrome WebDriver instance for browser automation.

    Returns
    -------
    selenium.webdriver.Chrome
        The Chrome WebDriver instance after navigating to the specified URL.
    """
    url = f'http://127.0.0.1:{flask_port}/predict_employment_trends'
    chrome_driver.get(url)
    return chrome_driver


@pytest.fixture
def policy_recommendation_page(live_server, flask_port, chrome_driver):
    """
    Navigate to the policy recommendation page.

    Parameters
    ----------
    live_server : flask.testing.FlaskClient
        The live server instance for testing.
    flask_port : int
        The port number on which the Flask application is running.
    chrome_driver : selenium.webdriver.Chrome
        The Chrome WebDriver instance for browser automation.

    Returns
    -------
    selenium.webdriver.Chrome
        The Chrome WebDriver instance after navigating to the policy
        recommendation page.
    """
    url = f'http://127.0.0.1:{flask_port}/policy_recommendation'
    chrome_driver.get(url)
    return chrome_driver


@pytest.fixture
def policy_feedback_page(live_server, flask_port, chrome_driver):
    """
    Fixture to navigate to the policy feedback page.

    This fixture uses the live server, Flask port, and Chrome WebDriver to
    navigate to the policy feedback page of the application.

    Parameters
    ----------
    live_server : pytest fixture
        A fixture that provides a live server for testing.
    flask_port : int
        The port number on which the Flask application is running.
    chrome_driver : selenium.webdriver.Chrome
        The Chrome WebDriver instance used to interact with the web page.

    Returns
    -------
    selenium.webdriver.Chrome
        The Chrome WebDriver instance after navigating to the policy feedback
        page.
    """
    url = f'http://127.0.0.1:{flask_port}/policy_feedback'
    chrome_driver.get(url)
    return chrome_driver


@pytest.fixture()
def wait_for_visible_element():
    """
    Wait for an element to be visible.

    Returns
    -------
    function
        A function that waits for an element to be visible.
    """
    def _wait_for_visible_element(driver, locator, timeout=10):
        """
        Wait for an element to be visible.

        Parameters
        ----------
        driver : WebDriver
            The Selenium WebDriver.
        locator : tuple
            The locator for the element.
        timeout : int, optional
            The timeout in seconds, by default 10.

        Returns
        -------
        WebElement
            The visible WebElement.
        """
        return WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )
    return _wait_for_visible_element


@pytest.fixture()
def wait_for_clickable_element():
    """
    Wait for an element to be clickable.

    Returns
    -------
    function
        A function that waits for an element to be clickable.
    """
    def _wait_for_clickable_element(driver, locator, timeout=10):
        """
        Wait for an element to be clickable.

        Parameters
        ----------
        driver : WebDriver
            The Selenium WebDriver.
        locator : tuple
            The locator for the element.
        timeout : int, optional
            The timeout in seconds, by default 10.

        Returns
        -------
        WebElement
            The clickable WebElement.
        """
        return WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )
    return _wait_for_clickable_element
