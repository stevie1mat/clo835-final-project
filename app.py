from flask import Flask, render_template, request
from pymysql import connections
import logging
import boto3
from botocore.exceptions import ClientError
import os
import random
import argparse

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DBHOST = os.environ.get("DBHOST") or "localhost"
DBUSER = os.environ.get("MYSQL_USER") or "root"
DBPWD = os.environ.get("MYSQL_PASSWORD") or "password"
DATABASE = os.environ.get("DATABASE") or "employees"
BG_IMAGE_URL = os.environ.get("BG_IMAGE_URL") or "https://clo835-bucket.s3.us-east-1.amazonaws.com/final+clo835.jpg"
MY_NAME = os.environ.get("MY_NAME") or "Steven Mathew"
COLOR_FROM_ENV = os.environ.get('APP_COLOR') or "lime"
DBPORT = int(os.environ.get("DBPORT", 3306))

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
COLOR = random.choice(list(color_codes.keys()))

def get_db_connection():
    try:
        conn = connections.Connection(
            host=DBHOST,
            port=DBPORT,
            user=DBUSER,
            password=DBPWD,
            db=DATABASE
        )
        logger.info("MySQL connection successful")
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to MySQL: {e}")
        return None

def get_s3_image_url():
    try:
        if BG_IMAGE_URL.startswith("https://"):
            url_parts = BG_IMAGE_URL.replace("https://", "").split("/")
            bucket_name = url_parts[0].split(".")[0]
            key = "/".join(url_parts[1:])
            s3_client = boto3.client('s3')
            presigned_url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': key},
                ExpiresIn=3600
            )
            return presigned_url
        return BG_IMAGE_URL
    except Exception as e:
        logger.error(f"Error accessing S3: {e}")
        return BG_IMAGE_URL

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('addemp.html', color=color_codes[COLOR],
                           background_image=get_s3_image_url(), my_name=MY_NAME)

@app.route("/about", methods=['GET', 'POST'])
def about():
    return render_template('about.html', color=color_codes[COLOR],
                           background_image=get_s3_image_url(), my_name=MY_NAME)

@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    primary_skill = request.form['primary_skill']
    location = request.form['location']

    db_conn = get_db_connection()
    if not db_conn:
        return "Database connection failed", 500

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:
        cursor.execute(insert_sql, (emp_id, first_name, last_name, primary_skill, location))
        db_conn.commit()
        emp_name = first_name + " " + last_name
        logger.info(f"Employee {emp_name} added successfully")
    except Exception as e:
        logger.error(f"Insert failed: {e}")
        return "Insert failed", 500
    finally:
        cursor.close()
        db_conn.close()

    return render_template('addempoutput.html', name=emp_name, color=color_codes[COLOR],
                           background_image=get_s3_image_url(), my_name=MY_NAME)

@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    return render_template("getemp.html", color=color_codes[COLOR],
                           background_image=get_s3_image_url(), my_name=MY_NAME)

@app.route("/fetchdata", methods=['GET', 'POST'])
def FetchData():
    emp_id = request.form['emp_id']

    db_conn = get_db_connection()
    if not db_conn:
        return "Database connection failed", 500

    output = {}
    select_sql = "SELECT emp_id, first_name, last_name, primary_skill, location FROM employee WHERE emp_id=%s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql, (emp_id,))
        result = cursor.fetchone()
        if not result:
            return "No employee found", 404

        output["emp_id"] = result[0]
        output["first_name"] = result[1]
        output["last_name"] = result[2]
        output["primary_skills"] = result[3]
        output["location"] = result[4]

        logger.info(f"Employee {emp_id} fetched successfully")
    except Exception as e:
        logger.error(f"Error fetching employee: {e}")
        return "Query failed", 500
    finally:
        cursor.close()
        db_conn.close()

    return render_template("getempoutput.html", id=output["emp_id"], fname=output["first_name"],
                           lname=output["last_name"], interest=output["primary_skills"],
                           location=output["location"], color=color_codes[COLOR],
                           background_image=get_s3_image_url(), my_name=MY_NAME)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--color', required=False)
    args = parser.parse_args()

    if args.color:
        COLOR = args.color
        if COLOR_FROM_ENV:
            print(f"Color from env ignored, using arg: {COLOR}")
    elif COLOR_FROM_ENV:
        COLOR = COLOR_FROM_ENV

    if COLOR not in color_codes:
        print(f"Unsupported color: {COLOR}")
        exit(1)

    app.run(host='0.0.0.0', port=81, debug=True)
