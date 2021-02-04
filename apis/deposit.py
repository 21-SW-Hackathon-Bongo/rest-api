import jwt
import json
import hashlib
from flask_restful import request
from flask_restplus import Namespace, fields, Resource, reqparse

import os
import sys
sys.path.append("..")

from lib.db_help import dbHelper

# 예치금 조회 API
Deposit = Namespace('Deposit', description='예치금')

charge_model = Deposit.model('deposit charge', {
		'amount': fields.Integer
})

@Deposit.route('/')
@Deposit.response(200, 'Found')
@Deposit.response(500, 'Internal Error')
@Deposit.doc(params={'Authorization': {'in': 'header', 'description': 'An authorization token'}})
class DepositProcess(Resource):
	# 예치금 조회
	def get(self):
		try:
			header = request.headers.get('Authorization')
				
			if header is None:
				return {"code": "err", "message": "Not Allow Authorization"}
			try:
				data = jwt.decode(header, "secret", algorithms=["HS256"])
			except Exception as e:
				return {"code":"err", "message":"Token Expired"}

			user_seq = data['user_seq']

			db = dbHelper()

			sql = "SELECT user_deposit FROM user WHERE user_seq = %s;"
			db.cursor.execute(sql, (user_seq))
			deposit = db.cursor.fetchone()

			if deposit == None:
				return {"code":"err", "message":"Unexpected Error"}

		except Exception as e:
			return {"code":"err", "message":str(e)}

		return {"code":"success", "data":{"deposit":deposit}}

	# 예치금 충전
	@Deposit.expect(charge_model)
	def post(self):
		try:
			db = dbHelper()

			parser = reqparse.RequestParser()
			parser.add_argument('amount', type=int)
			args = parser.parse_args()

			if args['amount'] == None:
				return {"code":"err", "message":"Invalid Parameter amount"}

			header = request.headers.get('Authorization')
			
			if header is None:
				return {"code": "err", "message": "Not Allow Authorization"}
			try:
				data = jwt.decode(header, "secret", algorithms=["HS256"])
			except Exception as e:
				return {"code":"err", "message":"Token Expired"}

			user_seq = data['user_seq']

			# 일반회원은 충전 불가
			if data['user_type'] == "N":
				return {"code":"err", "message":"Permission Denied"}

			sql = "SELECT user_deposit FROM user WHERE user_seq = %s;"
			db.cursor.execute(sql, (user_seq))
			deposit = db.cursor.fetchone()

			if deposit == None:
				deposit = 0
			else:
				deposit = deposit['user_deposit']

			deposit += int(args['amount'])

			sql = "UPDATE user SET user_deposit = %s WHERE user_seq = %s;"
			db.cursor.execute(sql, (deposit, user_seq))
			db.conn.commit()

		except Exception as e:
			return {"code":"err", "message":str(e)}

		return {"code":"success", "data":{"deposit":deposit}}
