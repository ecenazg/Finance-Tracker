import datetime
import re
import json
import requests

from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology,  usd

# Configure application
app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

# Ensure templates are auto-reloaded
# app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
# @app.after_request
# def after_request(response):
#     response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#     response.headers["Expires"] = 0
#     response.headers["Pragma"] = "no-cache"
#     return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
# app.config["SESSION_FILE_DIR"] = mkdtemp()
# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

@app.route("/")
def index():
    if session.get("user_id") is None:
        return redirect("/login")

    totalAmount = get_user_total_balance()

    historyList = []

    # Retrieve income of transactions for the current user
    income = get_user_incomes()
    expense = get_user_expenses()

    # Iterate over each row from the database and extract the required information for our table
    for row in income:
        historyList.append({
            "type": "Income",
            "subType": row['income_type'],
            "amount": row['amount'],
            "currency": row['currency'],
            "dateTime": row['date']
        })

    # Retrieve income of transactions for the current user

    # Iterate over each row from the database and extract the required information for our table
    for row in expense:
        historyList.append({
            "type": "Expense",
            "subType": row['expense_category'],
            "amount": row['amount'],
            "currency": row['currency'],
            "dateTime": row['date']
        })

    # Render the index.html template with the historyList
    return render_template("index.html", historyList=historyList, totalAmount=totalAmount)

@app.route("/income", methods=["GET", "POST"])
def income():
    if session.get("user_id") is None:
        return redirect("/login")

    if request.method == "POST":
        amount = request.form.get("amount")
        currency = request.form.get("currency")
        income_type = request.form.get("income_type")

        # Insert transaction into the database
        db.execute("INSERT INTO income (user_id, amount, currency, income_type, date) VALUES (:user_id, :amount, :currency, :income_type, datetime('now', 'localtime'))",
                   user_id=session["user_id"], amount=amount, currency=currency, income_type=income_type)
        increase_user_balance(currency, float(amount))
        return redirect("/income")

    # Retrieve income of transactions for the current user
    income = get_user_incomes()

    # Declare a list for storing transaction info
    incomeList = []

    # Iterate over each row from the database and extract the required information for our table
    for row in income:
        incomeList.append({
            "id":row['id'],
            "amount": row['amount'],
            "currency": row['currency'],
            "income_type": row['income_type'],
            "date": row['date']
        })


    # Render the income.html template with the incomeList and income types
    income_types = ["Salary", "Investment", "Gift", "Rental", "Other"]
    currencies = ["USD","EUR","TRY","GBP","CNY","CHF","BRL"];
    return render_template("income.html", currencies=currencies, incomeList=incomeList, income_types=income_types)

@app.route("/deleteincome/<id>", methods=["DELETE"])
def deleteincome(id):
    if session.get("user_id") is None:
        return redirect("/login")
    income = db.execute("SELECT amount, currency FROM income WHERE id =:id", id=id)
    amount = income[0]["amount"]
    currency = income[0]["currency"]
    decrease_user_balance(currency,float(amount))
    db.execute("DELETE FROM income where id = :id", id=id)

@app.route("/deleteexpense/<id>", methods=["DELETE"])
def deleteexpense(id):
    if session.get("user_id") is None:
        return redirect("/login")
    expense = db.execute("SELECT amount, currency FROM expense WHERE id =:id", id=id)
    amount = expense[0]["amount"]
    currency = expense[0]["currency"]
    increase_user_balance(currency,float(amount))
    db.execute("DELETE FROM expense where id = :id", id=id)


@app.route("/expense", methods=["GET", "POST"])
def expense():

    if session.get("user_id") is None:
        return redirect("/login")

    if request.method == "POST":
        amount = request.form.get("amount")
        currency = request.form.get("currency")
        expense_category = request.form.get("expense_category")

        # Insert transaction into the database
        db.execute("INSERT INTO expense (user_id, amount, currency, expense_category, date) VALUES (:user_id, :amount, :currency, :expense_category, datetime('now', 'localtime'))",
                   user_id=session["user_id"], amount=amount, currency=currency, expense_category=expense_category)
        decrease_user_balance(currency, float(amount))
        return redirect("/expense")

    # Retrieve income of transactions for the current user
    expense = get_user_expenses()

    # Declare a list for storing transaction info
    expenseList = []

    # Iterate over each row from the database and extract the required information for our table
    for row in expense:
        expenseList.append({
            "id":row['id'],
            "amount": row['amount'],
            "currency": row['currency'],
            "expense_category": row['expense_category'],
            "date": row['date']
        })

    # Render the income.html template with the incomeList and income types
    expense_categories = ["Entertainment", "School", "Food", "Other"]
    currencies = ["USD","EUR","TRY","GBP","CNY","CHF","BRL"];
    return render_template("expense.html", currencies=currencies, expenseList=expenseList, expense_categories=expense_categories)

def get_user_expenses():
    expense = db.execute("SELECT id, amount, currency, expense_category, date FROM expense WHERE user_id = :user_id order by date", user_id=session["user_id"])
    return expense

def get_user_incomes():
    income = db.execute("SELECT id, amount, currency, income_type, date FROM income WHERE user_id = :user_id order by date", user_id=session["user_id"])
    return income

def get_user_total_balance():
    totalAmount = db.execute("SELECT cash FROM users WHERE id = :id", id=session["user_id"])
    return totalAmount[0]["cash"]

def increase_user_balance(currency, amount):
    converter = RealTimeCurrencyConverter()
    convertedAmount = converter.convert(currency,'USD',float(amount))
    totalAmount = get_user_total_balance()
    totalAmount+=convertedAmount
    db.execute("UPDATE users set cash =:cash where id =:id ", cash=totalAmount, id=session["user_id"]);

def decrease_user_balance(currency, amount):
    converter = RealTimeCurrencyConverter()
    convertedAmount = converter.convert(currency,'USD',float(amount))
    totalAmount = get_user_total_balance()
    totalAmount-=convertedAmount
    db.execute("UPDATE users set cash =:cash where id =:id ", cash=totalAmount, id=session["user_id"]);

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Source (https://www.geeksforgeeks.org/password-validation-in-python/)
    reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&-_])[A-Za-z\d@$!#%*?&-_]{6,20}$"
    if request.method == "POST":
        username=request.form.get("username")
        # Compile Regex
        pat = re.compile(reg)
        # Search Regex
        mat = re.search(pat, request.form.get("password"))
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Ensure the passwords match
        elif request.form.get("password") != request.form.get("passwordConfirm"):
            return apology("passwords must match", 403)

        # Ensure the password meets requirements
        elif not mat:
            return apology("passwords must meet requirements", 403)

        # Ensure username doesn't exist already
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))
        if len(rows) == 1:
            return apology("username unavailable", 403)
        # Hash the password
        hashed = generate_password_hash(request.form.get("password"))
        # Insert user info into users
        db.execute("INSERT INTO users (username, hash) VALUES (:username, :hashed)", username=username,hashed=hashed)
        return redirect("/")
    else:
        return render_template("register.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

class RealTimeCurrencyConverter():
    def __init__(self):
        url = 'https://api.exchangerate-api.com/v4/latest/USD'
        self.data= requests.get(url).json()
        self.currencies = self.data['rates']

    def convert(self, from_currency, to_currency, amount):
        initial_amount = amount
        #first convert it into USD if it is not in USD.
        # because our base currency is USD
        if from_currency != 'USD' :
            amount = amount / self.currencies[from_currency]

            # limiting the precision to 4 decimal places
        amount = round(amount * self.currencies[to_currency], 4)
        return amount

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)