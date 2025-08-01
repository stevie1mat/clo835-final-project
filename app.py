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
DBUSER = os.environ.get("MYSQL_USER") or "root"  # Read from Secret
DBPWD = os.environ.get("MYSQL_PASSWORD") or "password"  # Read from Secret
DATABASE = os.environ.get("DATABASE") or "employees"
BG_IMAGE_URL = os.environ.get("BG_IMAGE_URL") or "https://clo835-bucket.s3.us-east-1.amazonaws.com/magic.jpg"
MY_NAME = os.environ.get("MY_NAME") or "Steven Mathew"
COLOR_FROM_ENV = os.environ.get('APP_COLOR') or "lime"
DBPORT = int(os.environ.get("DBPORT", 3306))

logger.info(f"Background image URL: {BG_IMAGE_URL}")
# Create a connection to the MySQL database
# Create a connection to the MySQL database
try:
    db_conn = connections.Connection(
        host= DBHOST,
        port=DBPORT,
        user= DBUSER,
        password= DBPWD, 
        db= DATABASE
    )
    logger.info("Successfully connected to MySQL database")
except Exception as e:
    logger.error(f"Failed to connect to MySQL: {e}")
    db_conn = None
output = {}
table = 'employee';

# Define the supported color codes
color_codes = {
    "red": "#e74c3c",
    "green": "#16a085",
    "blue": "#89CFF0",
    "blue2": "#30336b",
    "pink": "#f4c2c2",
    "darkblue": "#130f40",
    "lime": "#C1FF9C",
}

def get_s3_image_url():
    """Get image URL from S3 bucket"""
    try:
        # Parse the S3 URL from ConfigMap
        if BG_IMAGE_URL.startswith("https://"):
            # Extract bucket and key from URL
            url_parts = BG_IMAGE_URL.replace("https://", "").split("/")
            bucket_name = url_parts[0].split(".")[0]  # Remove .s3.amazonaws.com
            key = "/".join(url_parts[1:])
            
            # Create S3 client
            s3_client = boto3.client('s3')
            
            # Generate presigned URL for private bucket access
            presigned_url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': key},
                ExpiresIn=3600  # URL expires in 1 hour
            )
            
            logger.info(f"Generated presigned URL for S3 image: {presigned_url}")
            return presigned_url
        else:
            logger.warning(f"Invalid S3 URL format: {BG_IMAGE_URL}")
            return BG_IMAGE_URL
    except Exception as e:
        logger.error(f"Error accessing S3: {e}")
        return BG_IMAGE_URL
# Create a string of supported colors
SUPPORTED_COLORS = ",".join(color_codes.keys())

# Generate a random color
COLOR = random.choice(["red", "green", "blue", "blue2", "darkblue", "pink", "lime"])


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('addemp.html', color=color_codes[COLOR], 
                        background_image=background_image, my_name=MY_NAME)

@app.route("/about", methods=['GET','POST'])
def about():
    return render_template('about.html', color=color_codes[COLOR])
    
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
        
        cursor.execute(insert_sql,(emp_id, first_name, last_name, primary_skill, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('addempoutput.html', name=emp_name, color=color_codes[COLOR])

@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    return render_template("getemp.html", color=color_codes[COLOR])


@app.route("/fetchdata", methods=['GET','POST'])
def FetchData():
    emp_id = request.form['emp_id']

    output = {}
    select_sql = "SELECT emp_id, first_name, last_name, primary_skill, location from employee where emp_id=%s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql,(emp_id))
        result = cursor.fetchone()
        
        # Add No Employee found form
        output["emp_id"] = result[0]
        output["first_name"] = result[1]
        output["last_name"] = result[2]
        output["primary_skills"] = result[3]
        output["location"] = result[4]
        
    except Exception as e:
        print(e)

    finally:
        cursor.close()

    return render_template("getempoutput.html", id=output["emp_id"], fname=output["first_name"],
                           lname=output["last_name"], interest=output["primary_skills"], location=output["location"], color=color_codes[COLOR])

if __name__ == '__main__':
    
    # Check for Command Line Parameters for color
    parser = argparse.ArgumentParser()
    parser.add_argument('--color', required=False)
    args = parser.parse_args()

    if args.color:
        print("Color from command line argument =" + args.color)
        COLOR = args.color
        if COLOR_FROM_ENV:
            print("A color was set through environment variable -" + COLOR_FROM_ENV + ". However, color from command line argument takes precendence.")
    elif COLOR_FROM_ENV:
        print("No Command line argument. Color from environment variable =" + COLOR_FROM_ENV)
        COLOR = COLOR_FROM_ENV
    else:
        print("No command line argument or environment variable. Picking a Random Color =" + COLOR)

    # Check if input color is a supported one
    if COLOR not in color_codes:
        print("Color not supported. Received '" + COLOR + "' expected one of " + SUPPORTED_COLORS)
        exit(1)

    app.run(host='0.0.0.0',port=8080,debug=True)
