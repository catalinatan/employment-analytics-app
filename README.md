# Employment Analytics App

## Project Setup Instructions

### 1. Clone the Repository
Clone the project in your preferred IDE (e.g., VS Code, PyCharm) from GitHub.

### 2. Project Structure
The coursework code has the following structure:

```text
.
├── .gitignore                   # Git ignore file
├── README.md                    # Project description and instructions
├── requirements.txt             # List of dependencies
├── pyproject.toml               # Installation and package details
├── src/                         # Main code directory
│   ├── employment_flask_app/    # App package directory
│   │   ├── __init__.py          # Code to configure the Flask app
│   │   ├── db.py                # Database utilities
│   │   ├── models.py            # Database models
│   │   └── ...                  # Other app modules
│   └── instance/                # SQLite database storage
├── tests/                       # Test suite
│   ├── conftest.py              # Test fixtures
│   ├── test_add_row.py
│   ├── test_datatable.py
│   ├── test_delete_row.py
│   ├── test_edit_cell.py
│   ├── test_home_page.py
│   ├── test_import_export.py
│   ├── test_pol_feedback.py
│   ├── test_predict_trend.py
│   └── test_rec_policy.py
├── .github/
│   └── workflows/
│       └── python-app.yml       # GitHub Actions workflow for CI
└── .vscode/
    └── settings.json            # VS Code settings
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


## Additional Notes
- The project integrates a Dash app within the Flask app. The Dash app is accessible at `/dashboard/`.
- Ensure the `instance` folder exists for SQLite database storage.
- Modify the `SECRET_KEY` in `__init__.py` for production use.

