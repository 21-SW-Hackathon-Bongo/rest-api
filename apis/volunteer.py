import jwt
from flask import request
from flask_restplus import Namespace, fields, Resource, reqparse

import os
import sys

sys.path.append("..")

from lib.db_help import dbHelper

GetVolunteer = Namespace('get volunteer', description='일자리 지원자 목록 조회')

# 토큰
default_model = GetVolunteer.model('data', {
    'token': fields.String,
})


# 일자리 지원자 조회 API
@GetVolunteer.route('/<work_seq>/volunteer')
@GetVolunteer.response(200, 'OK')
@GetVolunteer.response(500, 'Internal Error')
@GetVolunteer.doc(params={'Authorization': {'in': 'header', 'description': 'An authorization token'}})
class Get_Volunteer(Resource):
    def get(self, work_seq):
        try:
            db = dbHelper()

            parser = reqparse.RequestParser()
            parser.add_argument('token', type=str)
            args = parser.parse_args()

            try:
                data = jwt.decode(args['token'], "secret", algorithms=["HS256"])
            except:
                return {"code": "err", "message": "Token Expired"}

            sql = "SELECT * from volunteer a, user b WHERE a.user_seq = b.user_seq AND work_seq = %s;"

            db.cursor.execute(sql, work_seq)
            result = db.cursor.fetchmany()

            if result is None:
                return {"code": "err", "message": "Invalid Volunteer"}

            volunteer_data = {"company_nm": result['company_nm'], "company_intro": result['company_intro'],
                              "company_img": result['company_img'], "ower_nm": result['owner_nm']
                              }

        except Exception as e:
            return {"code": "err", "message": str(e)}

        return {"code": "success", "data": volunteer_data}


SetVolunteer = Namespace('set volunteer', description='일자리 지원자 승인')

# 토큰
default_model = SetVolunteer.model('data', {
    'token': fields.String,
})


# 일자리 지원자 승인 API
@SetVolunteer.route('/volunteer')
@SetVolunteer.response(200, 'OK')
@SetVolunteer.response(500, 'Internal Error')
@SetVolunteer.doc(params={'Authorization': {'in': 'header', 'description': 'An authorization token'}})
class Set_Volunteer(Resource):
    def put(self):
        try:
            db = dbHelper()

            parser = reqparse.RequestParser()
            parser.add_argument('volunteer_seq', type=int)
            parser.add_argument('token', type=str)
            args = parser.parse_args()

            try:
                data = jwt.decode(args['token'], "secret", algorithms=["HS256"])
            except:
                return {"code": "err", "message": "Token Expired"}

            sql = "UPDATE volunteer SET employee_yn = %s where volunteer_seq = %s;"

            db.cursor.execute(sql, ('Y', args['volunteer_seq']))
            db.cursor.commit()

        except Exception as e:
            return {"code": "err", "message": str(e)}

        return {"code": "success"}
