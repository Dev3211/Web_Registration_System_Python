from flask import Flask, render_template, request
from flask.ext.bcrypt import Bcrypt
from flask_recaptcha import ReCaptcha

import MySQLdb
import re

MySQLdb.escape_string("'")  

db = MySQLdb.connect(host='localhost', user='root',
                     passwd='pass', db='DB')  

cur = db.cursor()

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.config.update(dict(
    RECAPTCHA_ENABLED = True,
    RECAPTCHA_SITE_KEY = "SITE KEY",
    RECAPTCHA_SECRET_KEY = "Secret KEY",
))

recaptcha = ReCaptcha()
recaptcha.init_app(app)

@app.route("/", methods=['POST'])
def main():
 invalid_chars = '^<>/"|\{}[]~`$'
 if request.method=='POST':
  if recaptcha.verify():
   username = request.form['username']
   password = request.form['password']
   sql = "SELECT COUNT(*) FROM %s WHERE username = '%s'" % ('Tablename', username)
   cur.execute(sql)
   result = cur.fetchone()
   found = result[0]
   if not username or not password:
    return '<h1>Your username/password field seems to be blank</h1>'
   elif len(username) < 3 or len(password) < 3:
    return '<h1>Your username/password field seems to short</h1>'
   elif set(invalid_chars).intersection(username) or set(invalid_chars).intersection(password):
    return '<h1>Either one of the fields contain illegal chars</h1>'
   elif not re.search('[a-z]', password):
    return '<h1>The password field must contain at least one lower case letter</h1>'
   elif not re.search('[A-Z]', password): 
    return '<h1>The password field must contain at least one upper case letter</h1>' 
   elif not re.search('[0-9]', password):
    return '<h1>The password field must contain at least one number</h1>' 
   elif found == 1:
    return '<h1>Username exists</h1>' 
   elif username and password and found == 0:
    hashed = bcrypt.generate_password_hash(password) 
    cur.execute('INSERT INTO Tablename (username, password) VALUES (%s, %s)', (username, hashed)) 
    db.commit()
    return '<h1>You have successfully registered</h1>'
   else:
    return '<h1>An error occured</h1>'
  else:
   return '<h1>Complete the recaptcha?</h1>'
 return render_template('index.html')
 
if __name__ == "__main__":
  app.run(host='0.0.0.0', port=5000)
