from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app


from . import db


class BaseModel(db.Model):
	__abstract__ = True
	id = db.Column(db.Integer, primary_key=True,unique=True)
	date_created = db.Column(db.DateTime, index=True, default=datetime.now())
	date_modified = db.Column(db.DateTime, index=True, default=datetime.now(), onupdate=datetime.now())

class Item(BaseModel):
	__tablename__ = "items"
	name = db.Column(db.String(100))
	done = db.Column(db.Boolean, default=False)
	bucketlist_id = db.Column(db.Integer, db.ForeignKey('bucketlists.id'), nullable=False)
	pass

class User(BaseModel):

	__tablename__ = "users"
	username = db.Column(db.String(64), unique=True)
	email = db.Column(db.Text, nullable=False)
	password_hash = db.Column(db.Text, nullable=False)
	bucketlists = db.relationship('Bucketlist', lazy='dynamic', backref=db.backref('owned_by', lazy='select'),cascade='all, delete-orphan')

	def __str__(self):
		return self.email if self.email else self.username

	def verify_password(self,password):
		return check_password_hash(self.password_hash, password)

	def to_json(self):
		json = {
		'username': self.username,
		'email': self.email,
		'date_registered': self.date_created,
		'no_of_bucket_list': self.bucketlists.count()
		}
		return json

	def get_bucketlists(self):
		bucketlists = Bucketlist.query.filter_by(
                user_id=self.id)
		return bucketlists

	@property
	def password(self):
	    raise AttributeError("This attribute is not readbale")
	
	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def generate_auth_token(self, expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'id': self.id})

	@staticmethod
	def verify_auth_token(token):
		s = Serializer(current_app.config['SECRET_KEY']) 
		try:
			data = s.loads(token)
			print data
		except:
			return None
		return User.query.get(data['id'])

class Bucketlist(BaseModel):
	__tablename__ = "bucketlists"
	name = db.Column(db.String(100))
	items = db.relationship('Item', lazy='dynamic', backref=db.backref('bucketlist', lazy='select'),cascade='all, delete-orphan')
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

	def __repr__(self):
		return self.name
	pass