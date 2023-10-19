""" app.py """
from cs50 import SQL
from flask import Flask, flash, redirect, request, render_template, session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session

from auth import login_required

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///app.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    """ Index """
    user_id = session.get("user_id")
    inventory = db.execute("SELECT * FROM inventory WHERE user_id = ?", user_id)
    return render_template("index.html", inventory=inventory)

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
    if request.method == "POST":
        username = request.form.get("username")
        passw = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Check if the username exist
        if username != "" and not db.execute(
            "SELECT 1 FROM users WHERE username = ?", username
        ):
            if passw != "" and confirmation != "" and passw == confirmation:
                db.execute(
                    "INSERT INTO users (username, hash) VALUES (?, ?)",
                    username,
                    generate_password_hash(passw),
                )
                return redirect("/login")
        flash("The user name is in use!", "alert-danger")
        return redirect("/register")
    else:
        return render_template("register.html", hide=lambda:True)

@app.route("/password", methods=["GET", "POST"])
def password():
    """ Password """
    if request.method == "POST":
        old = request.form.get("old")
        new = request.form.get("new")
        confirmation = request.form.get("confirmation")
        if old != "" and new != "" and confirmation != "":
            user_id = session.get("user_id")
            user = db.execute("SELECT * FROM users WHERE id = ?", user_id)
            if check_password_hash(user[0]["hash"], old):
                if new == confirmation:
                    db.execute(
                        "UPDATE users SET hash = ? WHERE id = ?",
                        generate_password_hash(new),
                        user_id,
                    )
                    flash("Password changed!", "alert-success")
                    return redirect("/")
                else:
                    flash("New and Repeat password must be the same!", "alert-danger")
                    return redirect("/password")
            else:
                flash("Old password incorrect!", "alert-danger")
                return redirect("/")
        else:
            flash("All fields are required!", "alert-danger")
            return redirect("/password")

    else:
        return render_template("password.html")


@app.route("/add", methods=["GET", "POST"])
def add():
    """ Add """
    user_id = session.get("user_id")
    if request.method == "POST":
        if request.form.get("title") != "":
            db.execute(
                "INSERT INTO inventory (barcode, name, price, amount, user_id) VALUES (?, ?, ?, ?, ?)",
                request.form.get("barcode"),
                request.form.get("title"),
                request.form.get("price"),
                request.form.get("amount"),
                user_id,
            )
            flash("Item added!", "alert-success")
            return redirect("/")
        else:
            flash("Title field can't be empty", "alert-success")
            return redirect("/add")
    else:
        return render_template("add.html")

@app.route("/edit", methods=["GET", "POST"])
def edit():
    """ Edit """
    user_id = session.get("user_id")
    if request.method == "POST":
        item_id = request.form.get("id")
        title = request.form.get("title")
        barcode = request.form.get("barcode")
        price = request.form.get("price")
        amount = request.form.get("amount")

        if title != "":
            db.execute(
                "UPDATE inventory SET name = ?, barcode = ?, price = ?, amount = ? WHERE id = ? AND user_id = ?",
                title,
                barcode,
                price,
                amount,
                item_id,
                user_id,
            )
            flash("Item edited!", "alert-success")
            return redirect("/")
        else:
            flash("Title field can't be empty", "alert-danger")
            return redirect(f"/edit?id={item_id}")

    if request.args:
        item_id = request.args.get("id")
        if str(item_id).isnumeric():
            data = db.execute("SELECT * FROM inventory WHERE id = ? AND user_id = ?", item_id, user_id)
            if len(data):
                return render_template("edit.html", data=data)
    return "400"
    
@app.route("/delete", methods=["GET"])
def delete():
    """Delete"""
    item_id = request.args.get("id") 
    user_id = session.get("user_id")
    if item_id:
        db.execute("DELETE FROM inventory WHERE id = ? AND user_id = ?", item_id, user_id)
        flash("Item deleted!", "alert-success")
        return redirect("/")