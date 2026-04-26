# Imports: 
from flask import Flask, render_template, request, redirect, url_for, session # Flask functionality
from db_funcs import * # Database functionality

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

        user_data = retrieveUser(username)
        if(len(user_data) == 0):
            # Logic for user not found
            pass
        else:
            # There should only be 1 record since usernames are unique in the db
            if(password == dict(user_data[0])["password"]):
                # Logic for correct password and username
                session["logged_in"] = True
                session["username"] = username
                return redirect(url_for("index"))
            else:
                # Logic for wrong password
                pass
    
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