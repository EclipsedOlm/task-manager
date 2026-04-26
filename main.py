# Imports: 
from flask import Flask, render_template, request, redirect, url_for, session # Flask functionality
#import psycopg2 # Database functionality

app = Flask(__name__) # Create the Flask app
app.secret_key = "temporary_secret_key"

# Main homepage
@app.route("/", methods=["GET", "POST"])
def index():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    return render_template("newindex.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Temporary login logic:
        # Any username/password is accepted for now.
        session["logged_in"] = True
        session["username"] = username

        return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Temporary register logic:
        # Do nothing with the account for now.
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
  app.run(port=5000)