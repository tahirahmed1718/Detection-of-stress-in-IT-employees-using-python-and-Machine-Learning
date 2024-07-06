from flask import Flask, render_template, request, url_for, session, redirect, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from werkzeug.utils import secure_filename
import cv2
import tensorflow as tf
import numpy as np

import numpy as np # linear algebra
from sklearn.feature_extraction.text import CountVectorizer

import re
import pickle
from flask import Flask, render_template, request
import tensorflow as tf
from tensorflow.keras.models import model_from_json
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.metrics import AUC
import numpy as np
from Graphical_Visualisation import Emotion_Analysis
import os
import cv2
import urllib
import numpy as np
from werkzeug.utils import secure_filename
from urllib.request import Request, urlopen
from flask import Flask, render_template, Response, request, redirect, flash, url_for

# Importing the required Classes/Functions from Modules defined.
 
from Graphical_Visualisation import Emotion_Analysis
face_haar_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

 

cap=cv2.VideoCapture(0)
app = Flask(__name__)
# read object TfidfVectorizer and model from disk
 
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER 

# Select model
 
model = model_from_json(open("models.json", "r").read())
model.load_weights('model_weight.h5')
def allowed_file(filename):
    """ Checks the file format when file is uploaded"""
    return ('.' in filename and
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS) 
def mood(result):
    if result=="Happy":
        return 'Happy'
    elif result=="Sad":
        return 'Sad'
    elif result=="Disgust":
        return 'Disgust'
    elif result=="Neutral":
         return 'Neutral'
    elif result=="Fear":
        return 'Fear'
    elif result=="Angry":
        return 'Angry'
    elif result=="Surprise":
        return 'Surprise'
        
     


 
  
    
def gen_frames():

    while True:
        ret,frame=cap.read()
        if not ret:
            break
        else:
            gray_img= cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces_detected = face_haar_cascade.detectMultiScale(gray_img, 1.32, 5)


            for (x,y,w,h) in faces_detected:
                cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),thickness=7)
                roi_gray=gray_img[y:y+w,x:x+h]
                roi_gray=cv2.resize(roi_gray,(48,48))
                img_pixels = image.img_to_array(roi_gray)
                img_pixels = np.expand_dims(img_pixels, axis = 0)
                img_pixels /= 255

                predictions = model.predict(img_pixels)

                #find max indexed array
                max_index = np.argmax(predictions[0])

                emotions = ('angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral')
                predicted_emotion = emotions[max_index]

                cv2.putText(frame, predicted_emotion, (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

            resized_img = cv2.resize(frame, (1000, 700))

            ret, buffer = cv2.imencode('.jpg', frame)

            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')



app.secret_key = 'neha'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'stress'
mysql = MySQL(app)


@app.route('/',methods = ['GET','POST'])
def first():
    return render_template('first.html')
 
 
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/camera')
def camera():
    return render_template('camera.html')     
 

@app.route('/login', methods = ['GET',"POST"])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM people WHERE username = %s AND password = %s AND status="Approved"' , (username, password))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            global Id
            session['Id'] = account['Id']
              
            Id = session['Id']
            global Username
            session['username'] = account['username']
            Username = session['username']
            # Redirect to home page
            return redirect(url_for('index'))
        else:
            # Account doesnt exist or username/password incorrect
            flash('Incorrect username/password! Please login with correct credentials')
            return redirect(url_for('login'))
    # Show the login form with message (if any)

    return render_template('login.html', msg=msg)

@app.route('/register',methods= ['GET',"POST"])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'mobile' in request.form and'loginid' in request.form and 'address' in request.form and 'company' in request.form and 'state' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        mobile = request.form['mobile']
        loginid = request.form['loginid']
        address = request.form['address']
        company = request.form['company']
        state = request.form['state']
        
        
        reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,10}$"
        pattern = re.compile(reg)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Check if account exists using MySQL)
        cursor.execute('SELECT * FROM people WHERE Username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not re.search(pattern,password):
            msg = 'Password should contain atleast one number, one lower case character, one uppercase character,one special symbol and must be between 6 to 10 characters long'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into employee table
            cursor.execute('INSERT INTO people VALUES (NULL, %s, %s, %s, %s,%s, %s, %s, %s,"waiting")', (username, password, email, mobile,loginid,address,company,state))
            mysql.connection.commit()
            flash('You have successfully registered! Please proceed for login!')
            return redirect(url_for('login'))
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
        return msg
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)



@app.route("/index", methods=['GET', 'POST'])
def index():
	return render_template("index.html")


@app.route('/uploadimage', methods=['POST'])
def uploadimage():
    """ Loads Image from System, does Emotion Analysis & renders."""

    if request.method == 'POST':

        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']

        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        # If user uploads the correct Image File
        if file and allowed_file(file.filename):

            # Pass it a filename and it will return a secure version of it.
            # The filename returned is an ASCII only string for maximum portability.
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print(filename) 
            result = Emotion_Analysis(filename)
            if len(result) == 1:
                return render_template('NoDetection.html', orig=result[0])
                
            sentence = mood(result[3]) 
            # When Classifier could not detect any Face.
            cur = mysql.connection.cursor()    
            cur.execute("INSERT INTO review(sentence,filename,userid) VALUES ( %s, %s,%s) ", (sentence,filename,Id))
            mysql.connection.commit()
            cur.close()
            return redirect('/index')
    return render_template('index.html')         

 

         
  
 
@app.route('/userdetail')
def userdetail():  
    cur = mysql.connection.cursor()
    resultValue = cur.execute(" SELECT * from people INNER JOIN review ON people.ID = review.USERID;")
     
    if resultValue > 0:
        useradmin = cur.fetchall()
       
        return render_template('userdetail.html',useradmin=useradmin)  
   
@app.route('/admin')
def admin():
    cur = mysql.connection.cursor()
    resultValue = cur.execute(" SELECT * from people")
     
    if resultValue > 0:
        userDetails = cur.fetchall()
         
        return render_template('admin.html',userDetails=userDetails)    

@app.route('/blockUser',methods=['GET','POST'])
def blockUser():
    if request.method == 'POST' and 'fid' in request.form:
       f1 = request.form['fid']
        
       con=mysql.connection.cursor()
       con.execute("UPDATE people SET status='Approved' WHERE Id=%s " , (f1,))
       mysql.connection.commit()
            
       con.close()
     
        
       return redirect(url_for('admin'))   
@app.route("/loginadmin", methods=['GET', 'POST'])
def loginadmin():
	return render_template("loginadmin.html") 
    
    
@app.route("/performance", methods=['GET', 'POST'])
def performance():
	return render_template("performance.html") 

@app.route('/chart3')
def chart3():
    legend = "review by sentence"
    cursor = mysql.connection.cursor()
    
    try:
        cursor.execute("SELECT sentence from review GROUP BY sentence")
        # data = cursor.fetchone()
        rows = cursor.fetchall()
        labels = list()
        i = 0
        for row in rows:
            labels.append(row[i])
        
        cursor.execute("SELECT COUNT(id) from review GROUP BY sentence")
        rows = cursor.fetchall()
        # Convert query to objects of key-value pairs
        values = list()
        i = 0
        for row in rows:
            values.append(row[i])
        cursor.close()
         
        
    except:
        print ("Error: unable to fetch items")    

    return render_template('chart3.html', values=values, labels = labels, legend=legend)

    
if __name__ == '__main__':
    app.run()