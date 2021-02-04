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

			sql = "SELECT user_seq FROM user WHERE user_email = %s AND user_pw = %s;"
			db.cursor.execute(sql, (user_email, user_pw))
			result = db.cursor.fetchone()

			if result == None:
				return {"code":"err", "message":"Invalid Account"}	
			else:
				return {"code":"success", "data":"Token"}

		except Exception as e:
			return {"code":"err", "message":str(e)}

		return {"code":"success", "data":"token"}

# 회원가입 API
Member = Namespace('join', description='회원가입')
join_model = Member.model('join data', {
		'user_email': fields.String,
		'user_pw': fields.String,
		'user_type': fields.String,
		'user_birth': fields.String,
		'user_gender': fields.String
})

@Member.route('/join')
@Member.response(200, 'Found')
@Member.response(500, 'Internal Error')
class Join(Resource):
	@Member.expect(join_model)
	def post(self):
		try:
			db = dbHelper()

			parser = reqparse.RequestParser()
			parser.add_argument('user_email', type=str)
			parser.add_argument('user_pw', type=str)
			parser.add_argument('user_type', type=str)
			parser.add_argument('user_birth', type=str)
			parser.add_argument('user_gender', type=str)
			args = parser.parse_args()

			user_pw = encrypt(args['user_pw'])

			# 이메일 검증 실패
			if not validEmail(args['user_email']):
				return {"code":"err", "message":"Invalid Email"}


			sql = "INSERT INTO user (user_email, user_pw, user_birth, user_gender) VALUES (%s, %s, %s, %s);"
			db.cursor.execute(sql, (args['user_email'], user_pw, args['user_birth'], args['user_gender']))
			db.conn.commit()

			user_seq = db.cursor.lastrowid

		except Exception as e:
			return {"code":"err", "message":str(e)}

		return {"code":"success", "data":{"user_seq":user_seq}}

# 아이디 중복확인 API
check_model = Member.model('check_model', {
	'user_id': fields.String
})

IDCheck = Namespace('ID Check', description='아이디 중복검사')

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