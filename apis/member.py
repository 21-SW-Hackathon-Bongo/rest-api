import json
from flask_restful import request
from flask_restplus import Namespace, fields, Resource, reqparse

import os
import sys
sys.path.append("..")

from lib.db_help import dbHelper

Member = Namespace('member', description='일반회원')

# 결과값 정보
res_model = Member.model('response', {
	'code': fields.String(description='성공 여부'),
	'data': fields.String(description='결과 값'),
	'message': fields.String(description='오류 메세지'),
})

# 로그인 API
# 로그인 파라미터 정보
login_model = Member.model('login data', {
		'user_id': fields.String,
		'user_pw': fields.String
})

@Member.route('/login')
@Member.response(200, 'OK', model=res_model)
@Member.response(500, 'Internal Error')
class Login(Resource):
	@Member.expect(login_model)
	def post(self):
		try:
			db = dbHelper()
			print(db.tables())

			parser = reqparse.RequestParser()
			parser.add_argument('user_id', type=str)
			parser.add_argument('user_pw', type=str)
			args = parser.parse_args()

			__userID = args['user_id']
			__userPW = args['user_pw']
		except Exception as e:
			return {"code":"err", "message":str(e)}

		return {"code":"success", "data":"token"}

# 회원가입 API
join_model = Member.model('join data', {
		'user_id': fields.String,
		'user_pw': fields.String
})

@Member.route('/join')
@Member.response(200, 'Found')
@Member.response(500, 'Internal Error')
class Join(Resource):
	@Member.expect(join_model)
	def post(self):
		return {"text":"join"}