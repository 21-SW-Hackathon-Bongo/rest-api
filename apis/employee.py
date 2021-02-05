import jwt
from flask import request
from flask_restplus import Namespace, fields, Resource, reqparse

import os
import sys

sys.path.append("..")

from lib.db_help import dbHelper

SetEmployeeEnd = Namespace('set employee end', description='일자리 평점 등록')

# 평점 모델
employee_end_model = SetEmployeeEnd.model('data', {
    'token': fields.String,
    'user_seq': fields.Integer,
    'score_title': fields.String,
    'score_content': fields.String,
    'score_value': fields.Integer,
    'score_type': fields.String,
    'badge_nm': fields.String
})


# 일자리 지원자 조회 API
@SetEmployeeEnd.route('/<work_seq>/employee/end')
@SetEmployeeEnd.response(200, 'OK')
@SetEmployeeEnd.response(500, 'Internal Error')
@SetEmployeeEnd.doc(params={'Authorization': {'in': 'header', 'description': 'An authorization token'}})
class Get_Employee(Resource):
    @SetEmployeeEnd.expect(employee_end_model)
    def get(self, work_seq):
        try:
            db = dbHelper()

            parser = reqparse.RequestParser()
            parser.add_argument('token', type=str)
            parser.add_argument('user_seq', type=int)
            parser.add_argument('score_title', type=str)
            parser.add_argument('score_content', type=str)
            parser.add_argument('score_value', type=int)
            parser.add_argument('score_type', type=str)
            parser.add_argument('badge_nm', type=str)  # 추후 정규화를 생각해봐야 함..
            args = parser.parse_args()

            try:
                data = jwt.decode(args['token'], "secret", algorithms=["HS256"])
            except:
                return {"code": "err", "message": "Token Expired"}

            sql = "INSERT INTO score (user_seq, score_title, score_cotent, score_value, score_type, badge_nm) VALUES (%s, %s, %s, %s, %s, %s)"

            db.cursor.execute(sql, (
                work_seq, args['user_seq'], args['score_title'], args['score_content'], args['score_value'],
                args['score_type'], args['badge_nm']))
            result = db.cursor.fetchmany()

            if result is None:
                return {"code": "err", "message": "Invalid Volunteer"}


        except Exception as e:
            return {"code": "err", "message": str(e)}

        return {"code": "success"}


PutEmployeeEnd = Namespace('put employee end', description='일자리 평점 수정')


# 일자리 지원자 승인 API
@PutEmployeeEnd.route('/<work_seq>/employee/<employee_seq>')
@PutEmployeeEnd.response(200, 'OK')
@PutEmployeeEnd.response(500, 'Internal Error')
@PutEmployeeEnd.doc(params={'Authorization': {'in': 'header', 'description': 'An authorization token'}})
class Put_Employee(Resource):
    @PutEmployeeEnd.expect(employee_end_model)
    def put(self, work_seq, employee_seq):
        try:
            db = dbHelper()

            parser = reqparse.RequestParser()
            parser.add_argument('token', type=str)
            parser.add_argument('user_seq', type=int)
            parser.add_argument('score_title', type=str)
            parser.add_argument('score_content', type=str)
            parser.add_argument('score_value', type=int)
            parser.add_argument('score_type', type=str)
            parser.add_argument('badge_nm', type=str)  # 추후 정규화를 생각해봐야 함..
            args = parser.parse_args()

            try:
                data = jwt.decode(args['token'], "secret", algorithms=["HS256"])
            except:
                return {"code": "err", "message": "Token Expired"}
            args = parser.parse_args()

            sql = "UPDATE score SET score_title = %s, score_content = %s, score_value = %s, score_type = %s, badge_nm = %s where employee_seq = %s;"

            db.cursor.execute(sql, ('Y', args['score_title'], args['score_content'], args['score_value'], args['score_type'], args['badge_nm']))
            db.cursor.commit()

        except Exception as e:
            return {"code": "err", "message": str(e)}

        return {"code": "success"}
