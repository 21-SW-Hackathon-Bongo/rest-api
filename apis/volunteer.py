import jwt
from flask import request
from flask_restplus import Namespace, fields, Resource, reqparse

import os
import sys

sys.path.append("..")

from lib.db_help import dbHelper

GetVolunteer = Namespace('get volunteer', description='구직 지원자 목록 조회')

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

            header = request.headers.get('Authorization')

            if header is None:
                return {"code": "err", "message": "Not Allow Authorization"}
            try:
                data = jwt.decode(header, "secret", algorithms=["HS256"])
            except Exception as e:
                return {"code": "err", "message": "Token Expired"}

            sql = "SELECT a.volunteer_seq, a.user_seq, b.user_nm, b.user_gender, a.volunteer_content FROM volunteer a, user b WHERE a.user_seq = b.user_seq AND work_seq = %s;"

            db.cursor.execute(sql, work_seq)
            result = db.cursor.fetchall()
            print(result)
            if result is None:
                return {"code": "err", "message": "Invalid Volunteer"}

        except Exception as e:
            return {"code": "err", "message": str(e)}

        return {"code": "success", "data": result}


SetVolunteer = Namespace('set volunteer', description='구직 지원자 승인 처리')

# 토큰
setVolunteer_model = SetVolunteer.model('apply volunteer data', {
    'volunteer_seq': fields.Integer,
})


# 일자리 지원자 승인 API
@SetVolunteer.route('/volunteer')
@SetVolunteer.response(200, 'OK')
@SetVolunteer.response(500, 'Internal Error')
@SetVolunteer.doc(params={'Authorization': {'in': 'header', 'description': 'An authorization token'}})
class Set_Volunteer(Resource):
    @SetVolunteer.expect(setVolunteer_model)
    def put(self):
        try:
            db = dbHelper()

            header = request.headers.get('Authorization')

            if header is None:
                return {"code": "err", "message": "Not Allow Authorization"}
            try:
                data = jwt.decode(header, "secret", algorithms=["HS256"])
            except Exception as e:
                return {"code": "err", "message": "Token Expired"}

            parser = reqparse.RequestParser()
            parser.add_argument('volunteer_seq', type=int)
            parser.add_argument('token', type=str)
            args = parser.parse_args()

            sql = "UPDATE volunteer SET employee_yn = %s WHERE volunteer_seq = %s;"

            db.cursor.execute(sql, ('Y', args['volunteer_seq']))
            db.conn.commit()

            sql = "SELECT work_seq FROM volunteer WHERE volunteer_seq = %s;"

            db.cursor.execute(sql, args['volunteer_seq'])
            result = db.cursor.fetchone()

            data['work_seq'] = str(result['work_seq'])

            sql = "UPDATE work SET work_recruit = work_recruit - 1 WHERE work_seq = %s"
            db.cursor.execute(sql, data['work_seq'])
            db.conn.commit()

        except Exception as e:
            return {"code": "err", "message": str(e)}

        return {"code": "success"}
