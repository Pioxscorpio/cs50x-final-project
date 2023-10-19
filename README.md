# CS50 Inventory
## Video Demo: https://youtu.be/aKq0a-U_riw>
## Description
Effortlessly manage your inventory with our user-friendly web application built using Flask, SQLite, and Bootstrap. This application provides a seamless experience for tracking your inventory items, ensuring you always have a clear overview of your stock levels.

Create an account to access your personalized inventory dashboard, where you can add, edit, or remove items with ease. Our intuitive interface makes managing your inventory a breeze, even for those with no prior experience.

Additionally, our robust security measures ensure your data remains protected. Create a strong password and modify it whenever necessary to maintain the integrity of your account.

Streamline your inventory management process with our comprehensive web application and experience the benefits of organized stock control

## Technology Stack

- Frontend: Bootstrap 5
- Backend: Flask (Python)
- Database: SQLite3

## Installation

Download and Install [Python](https://www.python.org/downloads/) (3.12.0)

1. Clone the repository:
````bash
git clone https://github.com/me50/Pioxscorpio.git
````
2. Install dependencies:
````bash
pip install Flask
pip install Flask-Session
pip install cs50
pip install request
````
3. Start the application:
````bash
flask run
The application will be running on http://localhost:5000
````

## Code Overview
### app.db
Database structure
````sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    username TEXT NOT NULL,
    hash TEXT NOT NULL,
    cash NUMERIC NOT NULL DEFAULT 10000.00,
    );

CREATE TABLE inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name TEXT NOT NULL,
    barcode TEXT,
    price NUMERIC NOT NULL DEFAULT 0.00,
    amount INTEGER NOT NULL DEFAULT 0,
    user_id INTEGER,
    );
````
### app.py
1. Loads the requiered libraries
````python
# Used for database management
from cs50 import SQL

# Main Flask libraries
from flask import Flask, flash, redirect, request, render_template, session

# Used for encrypt and decrypt password
from werkzeug.security import check_password_hash, generate_password_hash

# Used for session management
from flask_session import Session

# Loads authentication fuction from external file
from auth import login_required
````
2. Initialize
````python
# Initialize Flask app
app = Flask(__name__)
# Set the session so that it does not close when time passes
app.config["SESSION_PERMANENT"] = False
# Set session type to filesytem
app.config["SESSION_TYPE"] = "filesystem"
# Initialize Session
Session(app)
# Initilize db as the database
db = SQL("sqlite:///app.db")
````
3. Deactivate cache
````python
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response
````

4. Route/Index
````python
@app.route("/")
@login_required
def index():
    """ Index"""

    # Gets the user id
    user_id = session.get("user_id")

    # Execute query to get all inventory items from this user
    inventory = db.execute("SELECT * FROM inventory WHERE user_id = ?", user_id)

    # Render index.html template along with inventory data
    return render_template("index.html", inventory=inventory)
````
5. Route/Login
````python
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return redirect("/login")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return redirect("/login")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            flash("Username or password are incorrect!", "alert-danger")
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html", hide=lambda:True)
````
6. Route/Logout
````python
@app.route("/logout")
def logout():
    """Log user out"""

    # Clear any user_id
    session.clear()

    # Redirect user to login
    return redirect("/")
````

7. Route/Register
````python
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # save form data into variables
        username = request.form.get("username")
        passw = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Check if the username exist
        if username != "" and not db.execute(
            "SELECT 1 FROM users WHERE username = ?", username
        ):
            # Checks if data from password input aren't empty and is equal to confirmation
            if passw != "" and confirmation != "" and passw == confirmation:
                # Insert into database
                db.execute(
                    "INSERT INTO users (username, hash) VALUES (?, ?)",
                    username,
                    generate_password_hash(passw),
                )
                # Redirects to login screen
                return redirect("/login")
        # If username is in use, redirect and show alert
        flash("The user name is in use!", "alert-danger")
        return redirect("/register")
    else:
        # If request is get show register view
        # hide=lambda:true is used to hide the navbar
        return render_template("register.html", hide=lambda:True)
````

**Contributing**

Please feel free to contribute to this project by submitting pull requests or opening issues.

**License**

This project is licensed under the MIT License.