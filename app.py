from flask import Flask, url_for, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError	
from flask_migrate import Migrate
import ignoramus

# TODO: Use pyMongo to use MongoDB (JSON-esque) instead of SQL.
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fullsite.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):

	__tablename__ = 'Users'

	id = db.Column(db.Integer, primary_key=True, unique=True)
	username = db.Column(db.String(50), unique=True)
	password = db.Column(db.String(50))

	def __init__(self, username, password):
		self.username = username
		self.password = password

class Full_Med(db.Model):

	__tablename__ = 'Medications'

	owner = db.Column(db.String(100))
	brand_name = db.Column(db.String(100))
	generic_name = db.Column(db.String(100))
	dose_type = db.Column(db.String(50))
	quantity = db.Column(db.String(50))
	# Will be structured as a dropdown ('Daily', 'Every Other Day', 'Twice Daily,' 'As Needed,' etc.)
	frequency = db.Column(db.String(100))
	notes = db.Column(db.String(1000))

	# TODO: Incorporate pill descriptions.
	# TODO: Incorporate side effects and warnings as a list. MongoDB might make it easier.

	def __init__(self, brand_name, generic_name, dose_type, quantity, frequency, notes, owner):
		self.brand_name = brand_name
		self.generic_name = generic_name
		self.dose_type = dose_type
		self.quantity = quantity
		self.frequency = frequency
		self.notes = notes
		self.owner = owner	

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
	errmess=None
	succmess=None
	# If login was done, then session[logged_in] should be true.
	if session.get('logged_in'):
		return redirect(url_for('view_dash'))
	return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	errmess=None
	succmess=None
	if session.get('logged_in'):
		return redirect(url_for('view_dash'))
	if request.method == 'GET':
		return render_template('login.html')
	else:
		username = request.form['username']
		password = request.form['password']

	try:
		data = User.query.filter_by(username=username, password=password).first()
		if data is not None:
			session['logged_in'] = True
			session['active_user'] = username
			return redirect(url_for('view_dash'))
		else:
			return render_template('login.html', errmess='Username and/or password incorrect. Please try again.')
	except:
		return render_template('login.html', errmess='There was an error when trying to sign you in. Please try again.')

# TODO: Add areas on pages to show success or error messages.

@app.route('/register', methods=['GET', 'POST'])
def register():
	errmess=None
	succmess=None
	if session.get('logged_in'):
		return redirect(url_for('view_dash'))
	if request.method == 'POST':
		user_to_add = User(username=request.form['username'], password=request.form['password'])
		try:
			db.session.add(user_to_add)
			db.session.commit()
		except IntegrityError:
			db.session.rollback()
			return render_template('register.html', errmess="Username must not already be taken.")
		return render_template('login.html', succmess="Account created successfully!")
	return render_template('register.html', errmess="Cannot register you with that information. Please try again.")


@app.route('/new', methods=['GET', 'POST'])
def new_med():
	errmess=None
	succmess=None
	if not session.get('logged_in'):
		return redirect(url_for('landing'))
	if request.method == 'POST':
		med_to_add = Full_Med(brand_name=request.form['brand'], generic_name=request.form['generic'],
					 dose_type=request.form['dtype'], quantity=request.form['quant'],
					 frequency=request.form['freq'], notes=request.form['notes'], owner=session['active_user'])
		db.session.add(med_to_add)
		db.session.commit()
		return redirect(url_for('view_dash'))
	return render_template('new.html', errmess="There was an error while processing your request. Please try again.")

@app.route('/dashboard')
def view_dash():
	errmess=None
	succmess=None
	if not session.get('logged_in'):
		return redirect(url_for('landing'))
	allmeds = Full_Med.query.filter_by(owner=session['active_user']).all()
	return render_template('dashboard.html', allmeds=allmeds)


@app.route("/logout")
def logout():
	session['logged_in'] = False
	session['active_user'] = None
	return redirect(url_for('landing'))

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
    app.run(debug=True, use_reloader=False)	
