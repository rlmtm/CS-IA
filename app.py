import os.path
import requests
import sqlite3

from cs50 import SQL
from sqlite3 import Error
from flask import Flask, flash, redirect, render_template, session, request, current_app, jsonify, url_for
from flask_session import Session

from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, before_first_request, run_sql, check_for_sql, clear_session


# From CS50 Module - (Configure application)
app = Flask(__name__)


# From CS50 Module - (Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# From CS50 Module - (Configure CS50 Library to use SQLite database)
db = SQL("sqlite:///storage.db")


# From CS50 Module
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.before_request
@before_first_request
def before_request():
    """Clear Session"""

    # Checks if college list is populated
    check_for_sql(app)

    # Calls function to redirect to login page only on app start
    clear_session(app)

    return


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Clear any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Variable for storing error message
        error = None

        # Ensure username was submitted
        if not request.form.get("username"):
            error = "Must provide username!"
            return render_template("login.html", error=error)

        # Ensure password was submitted
        elif not request.form.get("password"):
            error = "Must provide password!"
            return render_template("login.html", error=error)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            error = "Invalid username and/or password!"
            return render_template("login.html", error=error)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        print("success")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        existing_email = db.execute("SELECT * FROM users WHERE email = ?", request.form.get("email"))
        existing_username = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Variable for storing error message
        error = None

        # Ensure email was submitted
        if not request.form.get("email"):
            error = "Must provide email!"
            return render_template("register.html", error=error)
        
        # Ensure email is not already registered to an account
        elif len(existing_email) != 0:
            error = "Account already exists with specified email!"
            return render_template("register.html", error=error)

        # Ensure username is provided
        elif not request.form.get("username"):
            error = "Must provide username!"
            return render_template("register.html", error=error)

        # Ensure username is unique
        elif len(existing_username) != 0:
            error = "Username not available!"
            return render_template("register.html", error=error)

        # Ensure password was submitted
        elif not request.form.get("password"):
            error = "Missing password!"
            return render_template("register.html", error=error)

        # Ensure passwords match
        elif request.form.get("password") != request.form.get("confirmation"):
            error = "Passwords don't match!"
            return render_template("register.html", error=error)

        # Ensure password is between 4 and 15 characters
        elif len(request.form.get("password")) < 4 or len(request.form.get("password")) > 15:
            error = "Password must be between 4 and 15 characters long!"
            return render_template("register.html", error=error)

        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")

        # Hashes password when before inserting into users table
        hash = generate_password_hash(password, method='pbkdf2', salt_length=16)

        db.execute("INSERT INTO USERS (email, username, hash) VALUES(?, ?, ?)", email, username, hash)

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        session["user_id"] = rows[0]["id"]

        flash("Registered!")
        return redirect("/")

    else:

        return render_template("register.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


@app.route("/")
@login_required
def home():
    """Home Page"""

    user_id = session["user_id"]
    scrollable = False

    if request.method == "POST":

        return 1

    else:

        return render_template("home.html", scrollable=scrollable)


@app.route("/about")
@login_required
def about():
    """About Page"""

    user_id = session["user_id"]
    scrollable = False

    return render_template("about.html")

@app.route("/menu")
@login_required
def menu():
    """Sample Page"""

    return render_template("menu.html")


@app.route("/settings")
@login_required
def settings():
    """Settings Page"""

    user_id = session["user_id"]

    return render_template("settings.html")

if __name__ == "__main__":
    app.run(debug=True)
