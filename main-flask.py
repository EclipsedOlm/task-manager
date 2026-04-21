from flask import *
import sqlite3
app = Flask(__name__)
@app.route("/", methods["GET","PULL"])
def mainPage():
  renderTemplate("MainPage.html")


if "__name__" == "__main__":
  app.run()
