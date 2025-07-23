from flask import Flask, render_template, request
from pymysql import connections
import os
import random
import argparse

app = Flask(__name__)

# Database config from secrets or fallback
DBHOST = os.environ.get("DBHOST", "localhost")
DBUSER = os.environ.get("DBUSER", "root")
DBPWD = os.environ.get("DBPWD", "password")
DATABASE = os.environ.get("DATABASE", "employees")
DBPORT = int(os.environ.get("DBPORT", 3306))

# Customizations from ConfigMap
COLOR_FROM_ENV = os.environ.get("APP_COLOR", "lime")
BG_IMAGE_URL = os.environ.get("BG_IMAGE_URL", "/static/default.jpg")
MY_NAME = os.environ.get("MY_NAME", "Your Name")

# Print background image to logs (required)
print(f"Background image URL: {BG_IMAGE_URL}")

# Create MySQL connection
db_conn = connections.Connection(
    host=DBHOST,
    port=DBPORT,
    user=DBUSER,
    password=DBPWD,
    db=DATABASE
)

# Supported color codes
color_codes = {
    "red": "#e74c3c",
    "green": "#16a085",
    "blue": "#89CFF0",
    "blue2": "#30336b",
    "pink": "#f4c2c2",
    "darkblue": "#130f40",
    "lime": "#C1FF9C",
}

SUPPORTED_COLORS = ",".join(color_codes.keys())
COLOR = COLOR_FROM_ENV if COLOR_FROM_ENV in color_codes else random.choice(list(color_codes.keys()))

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template("addemp.html", color=color_codes[COLOR], background=BG_IMAGE_URL, name=MY_NAME)

@app.route("/about", methods=['GET', 'POST'])
def about():
    return render_template("about.html", color=color_codes[COLOR], background=BG_IMAGE_URL, name=MY_NAME)

@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    primary_skill = request.form['primary_skill']
    location = request.form['location']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()
    try:
        cursor.execute(insert_sql, (emp_id, first_name, last_name, primary_skill, location))
        db_conn.commit()
        emp_name = f"{first_name} {last_name}"
    finally:
        cursor.close()

    return render_template("addempoutput.html", name=emp_name, color=color_codes[COLOR], background=BG_IMAGE_URL, name_header=MY_NAME)

@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    return render_template("getemp.html", color=color_codes[COLOR], background=BG_IMAGE_URL, name=MY_NAME)

@app.route("/fetchdata", methods=['GET', 'POST'])
def FetchData():
    emp_id = request.form['emp_id']
    output = {}
    select_sql = "SELECT emp_id, first_name, last_name, primary_skill, location FROM employee WHERE emp_id=%s"
    cursor = db_conn.cursor()
    try:
        cursor.execute(select_sql, (emp_id))
        result = cursor.fetchone()
        if result:
            output["emp_id"] = result[0]
            output["first_name"] = result[1]
            output["last_name"] = result[2]
            output["primary_skills"] = result[3]
            output["location"] = result[4]
    except Exception as e:
        print(e)
    finally:
        cursor.close()

    return render_template("getempoutput.html",
                           id=output.get("emp_id", ""),
                           fname=output.get("first_name", ""),
                           lname=output.get("last_name", ""),
                           interest=output.get("primary_skills", ""),
                           location=output.get("location", ""),
                           color=color_codes[COLOR],
                           background=BG_IMAGE_URL,
                           name=MY_NAME)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=81, debug=True)
