[![Open in Codespaces](https://classroom.github.com/assets/launch-codespace-2972f46106e565e64193e422d61a12cf1da4916b45550586e14ef0a7c637dd04.svg)](https://classroom.github.com/open-in-codespaces?assignment_repo_id=18592104)
# COMP0035 Coursework 02 Starter Repository

## Project Setup Instructions

### 1. Clone the Repository
Clone the project in your preferred IDE (e.g., VS Code, PyCharm) from GitHub.

### 2. Project Structure
The coursework code has the following structure:

```text
my_project/
├── .gitignore             # Git ignore file
├── README.md              # Project description and instructions
├── requirements.txt       # List of dependencies
├── pyproject.toml         # Installation and package details
├── src/                   # Main code directory
│   ├── employment_flask_app/  # App package directory
│      ├── __init__.py     # Code to configure the Flask app
│      ├── static/         # Static files (e.g., CSS, JS)
│      ├── templates/      # Jinja page templates saved as .html files
│          ├── index.html  # Home page template
│      ├── routes.py       # Route definitions for the app
│      ├── run.py          # Entry point for running the Flask app
│   ├── dash_app/          # Dash app integration
│      ├── init_dash_app.py  # Dash app initialization
│      ├── layout.py       # Dash app layout
│      ├── callbacks.py    # Dash app callbacks
├── tests/                 # Test suite
│   ├── conftest.py        # Test fixtures
│   ├── test_app.py        # Example test cases
└── ...                    # Additional modules for your tests
```

### 3. Create and Activate a Virtual Environment
Create a virtual environment (e.g., `.venv`) and activate it.

### 4. Install Dependencies
Install the project dependencies using:
```bash
pip install -e .
```
Then do: 
```bash
pip install -r requirements.txt
```
Then upgrade selenium:
```bash
pip install --upgrade selenium urllib3
```

### 5. Run Tests
Run the tests in the `tests/` directory to ensure the setup is correct:
```bash
pytest
```

Note on pytest:
If you encounter a problem with installing the 'markdown' module, 
simply deactivate your virtual environment and repeat steps 3-4 
as the markdown module has been included in the requirements.txt 
file.

### 6. Run the Flask App
Run the Flask app using the following command:
```bash
flask --app employment_flask_app run --debug
```
You should see output similar to:
```text
 * Serving Flask app "employment_flask_app"
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: nnn-nnn-nnn
```
Visit [http://127.0.0.1:5000/](http://127.0.0.1:5000/) in your browser to view the app.

If port 5000 is in use, specify a different port:
```bash
flask --app employment_flask_app run --debug --port 5001
```

Alternatively, you can run the app using `run.py`:
```bash
python src/employment_flask_app/run.py
```

### 7. Rename the App
Rename the app from `employment_flask_app` to your desired name. Use your IDE's refactor feature to ensure all imports and references are updated.

---

## Additional Notes
- The project integrates a Dash app within the Flask app. The Dash app is accessible at `/dashboard/`.
- Ensure the `instance` folder exists for SQLite database storage.
- Modify the `SECRET_KEY` in `__init__.py` for production use.

Happy coding!
