# Finance-Tracker

### This is a Flask web application for personal finance management, allowing users to track their income and expenses, as well as their total balance. It uses SQLite database to store user data.



#### Features


- Register
- Login
- Add income transaction
- Add expense transaction
- Delete income transaction
- Delete expense transaction
- View transaction history
- View total balance
- Supports multiple currencies

#### Updates

- The home page has sortable table headers.
- Online currency conversion is available.
- Future updates may include:
1. Fixing rounding errors and adjusting the display of decimal places.
2. Creating a separate table for currency exchange rates with an update feature.
3. Turning expense type and income type into tables with add/edit/delete functionality.

#### Files
- finance.db: SQLite database file.
- helpers.py: Python script containing helper functions.
- application.py: Main Python script containing the Flask application code.
- templates/: Directory containing the HTML templates for the web pages.
- static/: Directory containing the static files for the web pages

#### Routes
- /: Home page, displaying the user's transaction history and total balance.
- /register: Registration page.
- /login: Login page.
- /logout: Logout page.
- /income: Income page, allowing the user to add and view income transactions.
- /expense: Expense page, allowing the user to add and view expense transactions.
- /deleteincome/<id>: Endpoint for deleting an income transaction with the given id.
- /deleteexpense/<id>: Endpoint for deleting an expense transaction with the given id.

#### Dependencies
- cachelib==0.1.1
- certifi==2020.11.8
- chardet==3.0.4
- click==7.1.2
- cs50==6.0.1
- Flask==1.1.2
- Flask-Session==0.3.2
- gunicorn==20.0.4
- idna==2.10
- itsdangerous==1.1.0
- Jinja2==2.11.2
- MarkupSafe==1.1.1
- redis==3.5.3
- requests==2.25.0
- SQLAlchemy==1.3.20
- sqlparse==0.4.1
- termcolor==1.1.0
- urllib3==1.26.2
- Werkzeug==1.0.1

#### Getting Started
- Clone this repository
- Create a virtual environment: python3 -m venv venv
- Activate the virtual environment: source - venv/bin/activate
- Install the dependencies: pip install -r requirements.txt
- Create a database named finance.db: touch finance.db
- Run the Flask application: flask run

#### How to run

> ##### To run this application, please make sure you have Python 3.7 or higher installed on your machine.

1. Clone the repository to your local machine
2. Install the required packages by running pip install -r requirements.txt in your terminal or command prompt
3. Set the environment variable FLASK_APP to application.py by running export FLASK_APP=application.py on Linux or set FLASK_APP=application.py on Windows
4. Set the environment variable FLASK_ENV to development by running export FLASK_ENV=development on Linux or set FLASK_ENV=development on Windows
5. Run flask run to start the server
6. Open your web browser and go to http://localhost:5000/ to view the application.

#### Running the App with Docker Compose

- To run the app with Docker Compose, follow these steps:

1. Clone the repository to your local machine.
2. Install Docker and Docker Compose if you haven't already.
3. Open a terminal or command prompt and navigate to the root directory of the cloned repository.
4. Run the command docker-compose up.
5. The app should now be running at http://localhost:5000



