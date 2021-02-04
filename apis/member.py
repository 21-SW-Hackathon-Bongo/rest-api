import jwt
import json
import hashlib
from flask_restful import request
from flask_restplus import Namespace, fields, Resource, reqparse

import os
import sys
sys.path.append("..")

from lib.db_help import dbHelper

# 이메일 검증
def validEmail(user_email):
	# @ 검증
	if "@" not in user_email:
		return False

	db = dbHelper()
	sql = "SELECT user_seq FROM user WHERE user_email = %s;"
	db.cursor.execute(sql, (user_email))
	result = db.cursor.fetchone()

	if result == None:
		# 중복 없음
		return True

	# 중복 존재
	return False

# 패스워드 암호화
def encrypt(user_pw):
	user_pw = user_pw.encode('utf-8')
	enc = hashlib.md5()
	enc.update(user_pw)
	encText = enc.hexdigest()

	return encText

# 사용자 프로필 등록
def setProfile(key, value, user_seq):
	db = dbHelper()
	sql = "UPDATE user SET "+str(key)+" = %s, user_status = '1' WHERE user_seq = %s;"
	db.cursor.execute(sql, (value, user_seq))
	db.conn.commit()

	return True

# 관심분야 등록
def resetInterest(user_seq):
	db = dbHelper()
	sql = "DELETE FROM user_interest WHERE user_seq = %s;"
	db.cursor.execute(sql, (user_seq))
	db.conn.commit()

	return True	

# 관심분야 등록
def setInterest(user_seq, work_type_seq):
	db = dbHelper()
	sql = "INSERT INTO user_interest (user_seq, work_type_seq) VALUES (%s, %s);"
	db.cursor.execute(sql, (user_seq, work_type_seq))
	db.conn.commit()

	return True	

# 로그인 API
# 로그인 파라미터 정보
Login = Namespace('login', description='로그인')
login_model = Login.model('login data', {
		'user_email': fields.String,
		'user_pw': fields.String
})

@Login.route('/login')
@Login.response(200, 'OK')
@Login.response(500, 'Internal Error')
class LoginProcess(Resource):
	@Login.expect(login_model)
	def post(self):
		try:
			db = dbHelper()

			parser = reqparse.RequestParser()
			parser.add_argument('user_email', type=str)
			parser.add_argument('user_pw', type=str)
			args = parser.parse_args()

			user_email = args['user_email']
			user_pw = encrypt(args['user_pw'])

			sql = "SELECT user_seq, user_nm, user_type FROM user WHERE user_email = %s AND user_pw = %s;"
			db.cursor.execute(sql, (user_email, user_pw))
			result = db.cursor.fetchone()

			if result == None:
				return {"code":"err", "message":"Invalid Account"}	
			else:
				encoded_jwt = jwt.encode(result, "secret", algorithm="HS256")

				return {"code":"success", "data":{"token":encoded_jwt}}

		except Exception as e:
			return {"code":"err", "message":str(e)}

		return {"code":"success", "data":"token"}

# 회원가입 API
Join = Namespace('join', description='회원가입')
join_model = Join.model('join data', {
		'user_email': fields.String,
		'user_pw': fields.String,
		'user_type': fields.String,
		'user_birth': fields.String,
		'user_gender': fields.String,
		'user_nm': fields.String
})

@Join.route('/join')
@Join.response(200, 'Found')
@Join.response(500, 'Internal Error')
class JoinProcess(Resource):
	@Join.expect(join_model)
	def post(self):
		try:
			db = dbHelper()

			parser = reqparse.RequestParser()
			parser.add_argument('user_email', type=str)
			parser.add_argument('user_pw', type=str)
			parser.add_argument('user_type', type=str)
			parser.add_argument('user_birth', type=str)
			parser.add_argument('user_gender', type=str)
			parser.add_argument('user_nm', type=str)
			args = parser.parse_args()

			user_pw = encrypt(args['user_pw'])

			# 이메일 검증 실패
			if not validEmail(args['user_email']):
				return {"code":"err", "message":"Invalid Email"}

			# 파라미터 검증
			for key in args:
				if args[key] == None:
					return {"code":"err", "message":"Invalid Parameter "+str(key)}

			sql = "INSERT INTO user (user_email, user_pw, user_birth, user_gender, user_nm) VALUES (%s, %s, %s, %s, %s);"
			db.cursor.execute(sql, (args['user_email'], user_pw, args['user_birth'], args['user_gender'], args['user_nm']))
			db.conn.commit()

			user_seq = db.cursor.lastrowid

		except Exception as e:
			return {"code":"err", "message":str(e)}

		encoded_jwt = jwt.encode({"user_seq":user_seq}, "secret", algorithm="HS256")

		return {"code":"success", "data":{"token":encoded_jwt}}

# 프로필 등록 API
SetProfile = Namespace('set profile', description='프로필 설정')
join_model = SetProfile.model('set profile data', {
		'user_banknm': fields.String,
		'user_account': fields.String,
		'user_intro': fields.String
})

@SetProfile.route('/profile')
@SetProfile.response(200, 'Found')
@SetProfile.response(500, 'Internal Error')
@SetProfile.doc(params={'Authorization': {'in': 'header', 'description': 'An authorization token'}})
class ProfileProcess(Resource):
	@SetProfile.expect(join_model)
	def post(self):
		try:
			db = dbHelper()

			parser = reqparse.RequestParser()
			parser.add_argument('user_banknm', type=str)
			parser.add_argument('user_account', type=str)
			parser.add_argument('user_intro', type=str)
			args = parser.parse_args()

			header = request.headers.get('Authorization')
			
			if header is None:
				return {"code": "err", "message": "Not Allow Authorization"}
			try:
				data = jwt.decode(header, "secret", algorithms=["HS256"])
			except Exception as e:
				return {"code":"err", "message":"Token Expired"}

			user_seq = data['user_seq']

			# 프로필 정보 등록
			updatedProfile = []

			for key in args:
				if args[key] != None and key != 'token':
					setProfile(key, args[key], user_seq)
					updatedProfile.append(key)

		except Exception as e:
			return {"code":"err", "message":str(e)}

		return {"code":"success", "data":{"updated":updatedProfile}}


# 관심분야 등록 API
SetInterest = Namespace('set interest', description='관심분야 등록')
interest_model = SetInterest.model('profile data', {
		'interests': fields.List(fields.Integer)
})

@SetInterest.route('/interest')
@SetInterest.response(200, 'Found')
@SetInterest.response(500, 'Internal Error')
@SetInterest.doc(params={'Authorization': {'in': 'header', 'description': 'An authorization token'}})
class InterestProcess(Resource):
	@SetInterest.expect(interest_model)
	def post(self):
		try:
			db = dbHelper()

			parser = reqparse.RequestParser()
			parser.add_argument('interests', type=int, action='append')
			args = parser.parse_args()

			header = request.headers.get('Authorization')
			
			if header is None:
				return {"code": "err", "message": "Not Allow Authorization"}
			try:
				data = jwt.decode(header, "secret", algorithms=["HS256"])
			except Exception as e:
				return {"code":"err", "message":"Token Expired"}

			user_seq = data['user_seq']

			interests = args['interests']
			
			# 관심분야 초기화
			resetInterest(user_seq)

			# 관심분야 추가
			for work_type_seq in interests:
				setInterest(user_seq, work_type_seq)

		except Exception as e:
			return {"code":"err", "message":str(e)}

		return {"code":"success", "data":{"updated":interests}}


IDCheck = Namespace('ID Check', description='아이디 중복검사')

# 아이디 중복확인 API
check_model = IDCheck.model('check_model', {
	'user_id': fields.String
})

@IDCheck.route('/check')
class Check(Resource):
	@IDCheck.expect(check_model)
	def post(self):
		try:
			db = dbHelper()

			parser = reqparse.RequestParser()
			parser.add_argument('user_id', type=str)
			args = parser.parse_args()

			__userID = args['user_id']

			if validEmail(__userID):
				# 중복 존재 X
				return {"code":"success", "data":{"isDuplicate":"n"}, "message":"n"}
			else:
				# 중복 존재
				return {"code":"success", "data":{"isDuplicate":"y"}, "message":"y"}
		except Exception as e:
			return {"code":"err", "message":str(e)}

		return {"code":"success", "data":"token"}

# 프로필 조회 API
GetProfile = Namespace('get profile', description='프로필 조회')

@GetProfile.route('/<user_seq>')
@GetProfile.response(200, 'Found')
@GetProfile.response(500, 'Internal Error')
@GetProfile.doc(params={'Authorization': {'in': 'header', 'description': 'An authorization token'}})
class GetProfileProcess(Resource):
	def get(self, user_seq):
		try:
			db = dbHelper()

			# Authorization 헤더로 담음
			header = request.headers.get('Authorization')
			
			if header is None:
				return {"code": "err", "message": "Not Allow Authorization"}

			try:
				data = jwt.decode(header, "secret", algorithms=["HS256"])
			except Exception as e:
				return {"code":"err", "message":"Token Expired"}

			sql = "SELECT * FROM user WHERE user_seq = %s;"

			db.cursor.execute(sql, (user_seq))
			result = db.cursor.fetchone()

			if result == None:
				return {"code":"err", "message":"Invalid User"}

			profile_data = {"user_nm":result['user_nm'], "user_email":result['user_email'], "user_birth":str(result['user_birth'])}

		except Exception as e:
			return {"code":"err", "message":str(e)}

		return {"code":"success", "data":profile_data}