from flask import Flask, url_for, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError	
from flask_migrate import Migrate
import ignoramus

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fullsite.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):

	__tablename__ = 'Users'

	id = db.Column(db.Integer, primary_key=True, unique=True)
	username = db.Column(db.String(50), unique=True)
	password = db.Column(db.String(50))
	d_email = db.Column(db.String(100))
	d_phone = db.Column(db.String(25))
	ph_email = db.Column(db.String(100))
	ph_phone = db.Column(db.String(25))

	def __init__(self, username, password):
		self.username = username
		self.password = password
		self.d_email = ''
		self.d_phone = ''
		self.ph_phone = ''
		self.ph_email = ''

	def get_contacts(self, d_email, d_phone, ph_email, ph_phone):
		self.d_email = d_email
		self.d_phone = d_phone
		self.ph_phone = ph_phone
		self.ph_email = ph_email

class Full_Med(db.Model):

	__tablename__ = 'Medications'

	id = db.Column(db.Integer, primary_key=True, unique=True)
	owner = db.Column(db.String(100))
	brand_name = db.Column(db.String(100))
	generic_name = db.Column(db.String(100))
	dose_type = db.Column(db.String(50))
	quantity = db.Column(db.String(50))

	frequency = db.Column(db.String(100))
	notes = db.Column(db.String(1000))

	p_color = db.Column(db.String(100))
	p_type = db.Column(db.String(100))
	p_shape = db.Column(db.String(100))
	p_text = db.Column(db.String(100))

	def __init__(self, brand_name, generic_name, dose_type, quantity, frequency, notes, owner, p_color, p_type, p_shape, p_text):
		self.brand_name = brand_name
		self.generic_name = generic_name
		self.dose_type = dose_type
		self.quantity = quantity
		self.frequency = frequency
		self.notes = notes
		self.owner = owner
		self.p_color = p_color
		self.p_type = p_type
		self.p_shape = p_shape
		self.p_text = p_text

class Known_Med(db.Model):

	__tablename__ = 'Library'

	id = db.Column(db.Integer, primary_key=True)
	brand_name = db.Column(db.String(100))
	generic_name = db.Column(db.String(100))

	def __init__(self, brand, generic, dnum, dtype, quant, freq, notes):
		self.brand_name = brand
		self.generic_name = generic
		self.dose_num = dnum
		self.dose_type = dtype
		self.quantity = quant
		self.frequency = freq
		self.notes = notes

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

@app.route('/register', methods=['GET', 'POST'])
def register():
	errmess=None
	succmess=None
	if session.get('logged_in'):
		return redirect(url_for('view_dash'))
	if request.method == 'POST':
		user_to_add = User(username=request.form['username'], password=request.form['password'])
		db.session.add(user_to_add)
		db.session.commit()
		return render_template('login.html', succmess="Account created successfully!")
	return render_template('register.html')


@app.route('/new', methods=['GET', 'POST'])
def new_med():
	errmess=None
	succmess=None
	if not session.get('logged_in'):
		return redirect(url_for('landing'))
	if request.method == 'POST':
		med_to_add = Full_Med(brand_name=request.form['brand'], generic_name=request.form['generic'],
					 dose_type=request.form['dtype'], quantity=request.form['quant'],
					 frequency=request.form['freq'], p_color=request.form['pcol'],
					 p_type=request.form['ptype'], p_shape=request.form['pshape'],
					 p_text=request.form['ptext'], notes=request.form['notes'], owner=session['active_user'])
		db.session.add(med_to_add)
		db.session.commit()
		return redirect(url_for('view_dash'))
	return render_template('new.html')

@app.route('/dashboard')
def view_dash():
	errmess=None
	succmess=None
	if not session.get('logged_in'):
		return redirect(url_for('landing'))
	allmeds = Full_Med.query.filter_by(owner=session['active_user']).all()
	profinfo = User.query.filter_by(username=session['active_user']).first()
	return render_template('dashboard.html', allmeds=allmeds, profinfo=profinfo)

@app.route('/<int:med_id>')
def view_med(med_id):
	med_holder = Full_Med.query.filter_by(id=med_id).first()
	if session['active_user'] == med_holder.owner:
		return render_template('med.html', med_holder=med_holder)
	else:
		return redirect(url_for('view_dash'))

@app.route('/optup')
def opt_in_change():
	if not session.get('logged_in'):
		return redirect(url_for('view_dash'))
	else:
		return render_template('update.html')

@app.route('/update', methods=['GET', 'POST'])
def update_prof():
	errmess=None
	succmess=None
	if not session['logged_in']:
		return redirect(url_for('view_dash'))
	if request.method == 'POST':
		old_data = User.query.filter_by(username=session['active_user']).first()
		old_data.get_contacts(d_phone=request.form['d_phone'], d_email=request.form['d_email'],
										ph_phone=request.form['ph_phone'], ph_email=request.form['ph_email'])
		db.session.commit()
		return render_template('dashboard.html', succmess="Account updated successfully!")
	return render_template('update.html')

@app.route("/logout")
def logout():
	session['logged_in'] = False
	session['active_user'] = None
	return redirect(url_for('landing'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.debug = True
    db.create_all()
    app.secret_key = ignoramus.appsecret
    app.run(debug=True, use_reloader=False)	
