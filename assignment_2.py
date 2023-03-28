from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import uuid
from pydantic import BaseModel

from flask_pydantic import validate

import jwt
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.debug = True

app.config['SECRET_KEY'] = 'YW1pdHNpbmdo'

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:8969037429@localhost:5432/ta_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)


class Course(db.Model):
    __tablename__ = "TA"

    id = db.Column(db.Integer, primary_key=True)
    native_english_speaker = db.Column(db.String(250), nullable=False)
    course_instructor = db.Column(db.String(250), nullable=False)
    course = db.Column(db.String(250), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    class_size = db.Column(db.Integer, nullable=False)
    performance_score = db.Column(db.Float, nullable=False)


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key = True)
    public_id = db.Column(db.String(50), unique = True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(70), unique = True)
    password = db.Column(db.String(80))

class RequestBodyModel(BaseModel):
  native_english_speaker: int
  course_instructor: int
  course: str
  semester: int 
  class_size: int  
  performance_score: float 

def token_required(f):
	@wraps(f)
	def token_verify(*args, **kwargs):
		token = None
		if 'access-token' in request.headers:
			token = request.headers['access-token']
            
		if not token:
			return jsonify({'message' : 'Token is required.'}), 401
        
		try:
			data = jwt.decode(token, app.config['SECRET_KEY'])
			current_user = User.query.filter_by(public_id = data['public_id']).first()
		except:
			return jsonify({
				'message' : 'Token is invalid !!'
			}), 401
		return f(current_user, *args, **kwargs)

	return token_verify


@app.route('/cource/<id>', methods=['GET'])
@token_required
def get_course_list(current_user,id):
  course = Course.query.get(id)
  if course is None:
     return f"Id {id} does not exsit."
  
  del course.__dict__['_sa_instance_state']
  
  return jsonify(course.__dict__)


@app.route('/cource', methods=['GET'])
@token_required
def get_course(current_user):
  course_list = []
  for course in db.session.query(Course).all():
    del course.__dict__['_sa_instance_state']
    course_list.append(course.__dict__)
  return jsonify(course_list)


@app.route('/course', methods=['POST'])
# @token_required
@validate()
def create_course(body: RequestBodyModel):
	# body = request.get_json()
	# body = RequestBodyModel
	print("body====",body)
	native_english_speaker = body.native_english_speaker
	course_instructor = body.course_instructor
	course = body.course
	semester = body.semester
	class_size = body.class_size
	performance_score = body.performance_score
	data =Course(
		native_english_speaker=native_english_speaker,
		course_instructor=course_instructor,
		course=course,
		semester=semester,
		class_size=class_size,
		performance_score=performance_score
	)
	db.session.add(data)
	db.session.commit()

	return jsonify({
		'id': data.id,
		'native_english_speaker': data.native_english_speaker,
		'course_instructor': data.course_instructor,
		'course' : data.course,
		'semester' : data.semester,
		'class_size' : data.class_size,
		'performance_score' : data.performance_score
	}
	),201


@app.route('/course/<id>', methods=['PUT'])
@token_required
def update_course(current_user,id):
  body = request.get_json()
  db.session.query(Course).filter_by(id=id).update(
    dict(title=body['title'], content=body['content']))
  db.session.commit()
  return "course updated"


@app.route('/course/<id>', methods=['DELETE'])
@token_required
def delete_course(current_user,id):
  db.session.query(Course).filter_by(id=id).delete()
  db.session.commit()
  return "deleted"


@app.route('/user-list', methods =['GET'])
@token_required
def get_all_users(current_user):
	users = User.query.all()
	users_list = []
	for user in users:
		users_list.append({
			'public_id': user.public_id,
			'name' : user.name,
			'email' : user.email
		})

	return jsonify({'users_list': users_list})


@app.route('/user/login', methods =['POST'])
def login():
	auth = request.form
	if not auth.get('email') or not auth.get('password'):
		return jsonify(
			{'massage': "Email and password missing."}
		),401

	user = User.query.filter_by(email = auth.get('email')).first()

	if not user:
		return jsonify(
			{'massage': "Email does not exist."}
		),401
	
	password = User.query.filter_by(password = auth.get('password')).first()	
	if password:
		token = jwt.encode({
			'public_id': user.public_id,
			'exp' : datetime.utcnow() + timedelta(minutes = 30)
		}, app.config['SECRET_KEY'])
		return make_response(jsonify({'token' : token.decode('UTF-8')}), 201)
	
	return jsonify(
		{'massage': "Wrong password."}
	),401


@app.route('/signup', methods =['POST'])
def signup():
	data = request.form
	name, email = data.get('name'), data.get('email')
	password = data.get('password')

	user = User.query.filter_by(email = email).first()
	if not user:
		user = User(
			public_id = str(uuid.uuid4()),
			name = name,
			email = email,
			password = password
		)
		db.session.add(user)
		db.session.commit()
		return jsonify({
			'id': user.id,
    		'email': user.email,
		    'name': user.name
		}
		),201
	else:
		return make_response('User already exists. Please Log in.', 202)


if __name__ == "__main__":
	app.run(debug = True)