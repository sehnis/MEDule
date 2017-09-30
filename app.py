from flask import Flask, url_for, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import ignoramus

# TODO: Use pyMongo to use MongoDB (JSON-esque) instead of SQL.
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fullsite.db'
db = SQLAlchemy(app)

class User(db.Model):

	__tablename__ = 'Users'

	id = db.Column(db.Integer, primary_key=True, unique=True)
	username = db.Column(db.String(50), unique=True)
	password = db.Column(db.String(50))

	def __init__(self, uname, pword):
		self.username = uname
		self.password = pword

class Full_Med(db.Model):

	__tablename__ = 'Medications'

	id = db.Column(db.Integer, primary_key=True)
	brand_name = db.Column(db.String(100))
	generic_name = db.Column(db.String(100))
	dose_num = db.Column(db.Integer)
	dose_type = db.Column(db.String(25))
	quantity = db.Column(db.Integer)
	# Will be structured as a dropdown ('Daily', 'Every Other Day', 'Twice Daily,' 'As Needed,' etc.)
	frequency = db.Column(db.String(100))
	notes = db.Column(db.String(1000))

	# TODO: Incorporate pill descriptions.
	# TODO: Incorporate side effects and warnings as a list. MongoDB might make it easier.

	def __init__(self, brand, generic, dnum, dtype, quant, freq, notes):
		self.brand_name = brand
		self.generic_name = generic
		self.dose_num = dnum
		self.dose_type = dtype
		self.quantity = quant
		self.frequency = freq
		self.notes = notes

class Known_Med(db.Model):

	__tablename__ = 'Library'

	id = db.Column(db.Integer, primary_key=True)
	brand_name = db.Column(db.String(100))
	generic_name = db.Column(db.String(100))

	# TODO: Incorporate side effects and warnings as a list. MongoDB might make it easier.

	def __init__(self, brand, generic, dnum, dtype, quant, freq, notes):
		self.brand_name = brand
		self.generic_name = generic
		self.dose_num = dnum
		self.dose_type = dtype
		self.quantity = quant
		self.frequency = freq
		self.notes = notes

# --------------------- ROUTES --------------------- #

# BASE (HOME OR DASH)
@app.route('/')
def landing():
    # If login was done, then session[logged_in] should be true.
    return render_template('home.html')
'''
@app.route('/login')

@app.route('/register')

@app.route('/dashboard')

@app.route('/med')

@app.route('/med/<med_id>')

@app.route('/new')

@app.route('/delete')

@app.route('/profile')

@app.route('/profile/update')
'''

# --------------------- END ROUTES --------------------- #


if __name__ == '__main__':
    app.debug = True
    db.create_all()
    app.secret_key = ignoramus.appsecret
    app.run()