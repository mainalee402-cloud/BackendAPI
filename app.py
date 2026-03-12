from multiprocessing import connection
from flask import *
import pymysql
import pymysql.cursors
# Step 8 - add product
import os.path

#create a flask app
app=Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/images'
#create the route of the API/ endpoint
@app.route("/api/signup", methods=["POST"])

# CREATE A FUNCTION TO HANDLE THE SIGN UP PROCESS
def signup(): 
    if request.method =="POST":
        username = request.form["username"]
        email = request.form["email"]
        passwd = request.form["passwd"]
        phone = request.form["phone_number"]

      
        # connect to the database
        connection= pymysql.connect(host='localhost', user='root', password='', database='SokoGarden')

        # insert the data in the database
        # cursor - allows us to run SQL queries in python
        cursor = connection.cursor()
        cursor.execute('insert into users(username,email,passwd,phone_number) values(%s,%s,%s,%s)', (username, email, passwd,phone))
        
        # cursor saves or commits the changes to the database
        connection.commit()
        return jsonify({

            "success" : "Thank you for joining"

        })


# create a function to handle signin process
# step 1 - Define the route
@app.route("/api/signin", methods=["POST"])
# step 2 - Create a function
def signin():
     # step 3 - Extra post data
    email = request.form['email']
    passwd=request.form['passwd']

    # step 4 - connect with dartabase
    connection= pymysql.connect(host='localhost', user= 'root',password='', database='SokoGarden')

    # step 5 - create a cursor to return results a dictionary , initialize connection
    cursor= connection.cursor(pymysql.cursors.DictCursor)

    # step 6 - sql query to select from the users table email password
    sql = "select * from users where email = %s and passwd = %s"
    # step 7 - prepare the data to replace the placeholders %s
    data = (email, passwd, )
    # step 8 - use tyhe cursor to execute the sql providing the to replace the placeholders
    cursor.execute(sql, data)
    # step 9 - check how many rows are found in the database
    count= cursor.rowcount
    # step 10 - count if rows are found, Invalid credentials - no user found
    if count == 0:
        return jsonify({
            "message": "login failed"
        })
    
    else: 
    # else there is a user, return a message to say login success and all user details, fetchnone to get all user login details
        user = cursor. fetchone() 
    # step 11 - return the login success message with user details as a dictionary
        return jsonify ({
            'message' : 'Login Success',
            'user': user
        })

# Add products function
# step 1 - Define the route
@app.route("/api/add_product", methods=["POST"])
# step 2 - Create a function to handle the add product process
def add_product():
    if request.method == "POST":
        # step 3 - Extract post data
        product_name = request.form["product_name"]
        product_description = request.form["product_description"]
        product_cost = request.form["product_cost"]
        

          # product_photo = request.form['product_photo]
        # extract the import data
        photo =request.files ['product_photo']    
        # Getting the image file name
        file_name = photo.filename
        # specify where the image will be saved (in a static folder)- image path
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)

        # save the image
        photo.save(photo_path)
        
        #Step 4 - Connect to the database
        connection= pymysql.connect(host='localhost', user='root', password='', database='SokoGarden')

        # insert the data in the database
        # cursor - allows us to run SQL queries in python
        # step 5- prepare and execute query to insert the data into our database
        cursor = connection.cursor()
        cursor.execute('insert into product_details(product_name, product_cost, product_description, product_photo) values(%s,%s,%s,%s)', (product_name, product_cost, product_description, file_name))
        
        #Step 6 - cursor saves or commits the changes to the database
        connection.commit()

        return jsonify ({

            "success" : "Product added successfully"

        })


# get product function

# define the route
@app.route("/api/get_products_details", methods=["GET"])
def get_product_details():

    # connect the database with Dictcursor for direct dictionary results
    connection = pymysql.connect(host='', user='', password='', database='SokoGarden')

    # create the cursor object and fetch all the data from the products details table
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute('SELECT * from products_details')
    product_details = cursor.fetchall()

    # close the database connection
    connection.close()

    # return the fetched products 
    return product_details


# mpesa stk push payment

import datetime
import base64
import requests
from requests.auth import HTTPBasicAuth

# define route
@app.route('/api/mpesa_payment', methods=['POST'])
def mpesa_payment():
    if request.method == "POST":
        amount = request.form['amount']
        phone = request.form['phone']

        # credentials from daraga
        consumer_key = "GTWADFxIpUfDoNikNGqq1C3023evM6UH"
        consumer_secret = "amFbAoUByPV2rM5A"

        # access token url 
        api_url = "http://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

        # request access token
        r = requests.get(api_url, auth=HTTPBasicAuth(consumer_key, consumer_secret))

        data = r.json()
        access_token = "Bearer" + "" + data

        # generate the time stamp for the transaction
        timestamp = datetime.datetime.today().strftime("%Y%m%d%H%M")
        # 20260311125610

        # the pass key FROM SAFARICOM
        passkey = "bfb279f9aa9dbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1sd2c919"

        # bussibess short code 
        business_short_code = "174379"

        # create the password
        data = business_short_code + passkey + timestamp

        # encode the passcode
        encoded = base64.b64decode(data.encode())

        # convert the encoded passcode to a string 
        password = encoded.decode('utf-8')
        # this transforms the password to a readable text

        # create payment payload
        payload = {
            'business_short_code' : '174379', 'password' : "{}".format(password),
            'transactionType' : "CustomerPaybillOnline",
            'amount' : amount,
            'partyA' : phone,
            'partyB' : '174379',
            'phonenumber' : phone,
            'accountreference' : "account",
            'transactiondesc' : "account"
        }

        # HTTP Headers
        headers = {
            "Authorization" : access_token,
            "content-type" : "application/json"
        }

        # stk push API Endpoint
        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

        # send the request to safaricom
        Response = request.post(url, json = payload, headers= headers)

        # print the Response
        print(response.text)

        # return response to the client
        return jsonify({
            'message' : 'please complete payment in your phone and we will deliver in minutes'
        })








# run the app
if __name__== '__main__':
    app.run(debug=True)






