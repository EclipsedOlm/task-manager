# Imports: 
from flask import Flask, render_template, request # Flask functionality
import psycopg2 # Database functionality

app = Flask(__name__) # Create the Flask app


# Main homepage
@app.route("/", methods=["GET","POST"])
def index():
  return render_template("newindex.html") # index.html is default naming convention for the landing page


# Run the app
if __name__ == "__main__":
  app.run(port=5000)