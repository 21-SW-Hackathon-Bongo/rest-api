import jwt
from flask import request
from flask_restplus import Namespace, fields, Resource, reqparse

import os
import sys

sys.path.append("..")

from lib.db_help import dbHelper

SetEmployeeEnd = Namespace('set employee end', description='단기 알바 종료 후 업체 평가')

# 평점 모델
employee_end_model = SetEmployeeEnd.model('employee score data', {
    'user_seq': fields.Integer,
    'company_seq': fields.Integer,
    'volunteer_seq': fields.Integer,
    'score_title': fields.String,
    'score_content': fields.String,
    'score_value': fields.Integer,
    'score_type': fields.String,
})



@SetEmployeeEnd.route('/<work_seq>/employee/end')
@SetEmployeeEnd.response(200, 'OK')
@SetEmployeeEnd.response(500, 'Internal Error')
@SetEmployeeEnd.doc(params={'Authorization': {'in': 'header', 'description': 'An authorization token'}})
class Get_Employee(Resource):
    @SetEmployeeEnd.expect(employee_end_model)
    def post(self, work_seq):
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
            parser.add_argument('user_seq', type=int)
            parser.add_argument('company_seq', type=int)
            parser.add_argument('volunteer_seq', type=int)
            parser.add_argument('score_title', type=str)
            parser.add_argument('score_content', type=str)
            parser.add_argument('score_value', type=int)
            parser.add_argument('score_type', type=str)
            # parser.add_argument('badge_nm', type=str)  # 추후 정규화를 생각해봐야 함..
            args = parser.parse_args()

            sql = "INSERT INTO score (volunteer_seq, work_seq, company_seq, score_title, score_content, score_value, score_type) VALUES (%s, %s, %s, %s, %s, %s, %s)"

            db.cursor.execute(sql, (
                args['volunteer_seq'], work_seq, args['company_seq'], args['score_title'], args['score_content'], args['score_value'], args['score_type']))

            sql = "SELECT sum(a.score_value) / count(a.company_seq) AS score_sum FROM bongo.score a, bongo.company b WHERE a.company_seq = b.company_seq AND a.company_seq = %s";

            db.cursor.execute(sql, args['company_seq'])
            result = db.cursor.fetchone()

            result['score_sum'] = str(result['score_sum'])

            sql = "UPDATE company SET company_score = %s WHERE company_seq = %s";
            db.cursor.execute(sql, (result['score_sum'], args['company_seq']))

            sql = "UPDATE volunteer SET isDeleted = %s WHERE volunteer_seq = %s";
            db.cursor.execute(sql, ('Y', args['volunteer_seq']))

            db.conn.commit()

        except Exception as e:
            return {"code": "err", "message": str(e)}

        return {"code": "success"}


SetCompanyEnd = Namespace('set company end', description='단기 알바 종료 후 직원 평가')

# 평점 모델
company_end_model = SetCompanyEnd.model('company score data', {
    'user_seq': fields.Integer,
    'volunteer_seq': fields.Integer,
    'score_title': fields.String,
    'score_content': fields.String,
    'score_value': fields.Integer,
    'score_type': fields.String,
})



@SetCompanyEnd.route('/<work_seq>/company/end')
@SetCompanyEnd.response(200, 'OK')
@SetCompanyEnd.response(500, 'Internal Error')
@SetCompanyEnd.doc(params={'Authorization': {'in': 'header', 'description': 'An authorization token'}})
class Get_Company(Resource):
    @SetCompanyEnd.expect(company_end_model)
    def post(self, work_seq):
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
            parser.add_argument('user_seq', type=int)
            parser.add_argument('volunteer_seq', type=int)
            parser.add_argument('score_title', type=str)
            parser.add_argument('score_content', type=str)
            parser.add_argument('score_value', type=int)
            parser.add_argument('score_type', type=str)
            # parser.add_argument('badge_nm', type=str)  # 추후 정규화를 생각해봐야 함..
            args = parser.parse_args()

            sql = "INSERT INTO score (user_seq, volunteer_seq, work_seq, score_title, score_content, score_value, score_type) VALUES (%s, %s, %s, %s, %s, %s, %s)"

            db.cursor.execute(sql, (
                args['user_seq'], args['volunteer_seq'], work_seq, args['score_title'], args['score_content'], args['score_value'], args['score_type']))

            sql = "SELECT sum(b.score_value) / count(b.score_seq) AS score_sum FROM bongo.user a, bongo.score b WHERE a.user_seq = b.user_seq AND a.user_seq = %s";

            db.cursor.execute(sql, args['user_seq'])
            result = db.cursor.fetchone()

            result['score_sum'] = str(result['score_sum'])

            sql = "UPDATE user SET user_score = %s WHERE user_seq = %s";
            db.cursor.execute(sql, (result['score_sum'], args['user_seq']))

            db.conn.commit()

        except Exception as e:
            return {"code": "err", "message": str(e)}

        return {"code": "success"}



PutEmployeeEnd = Namespace('put employee end', description='단기 알바 업체 평가 수정')
# 평점 수정 모델
put_employee_end_model = SetEmployeeEnd.model('put employee score data', {
    'user_seq': fields.Integer,
    'score_title': fields.String,
    'score_content': fields.String,
    'score_value': fields.Integer,
    'score_type': fields.String,
})

# 일자리 지원자 승인 API
@PutEmployeeEnd.route('/<work_seq>/employee/<volunteer_seq>')
@PutEmployeeEnd.response(200, 'OK')
@PutEmployeeEnd.response(500, 'Internal Error')
@PutEmployeeEnd.doc(params={'Authorization': {'in': 'header', 'description': 'An authorization token'}})
class Put_Employee(Resource):
    @PutEmployeeEnd.expect(put_employee_end_model)
    def put(self, work_seq, volunteer_seq):
        try:
            db = dbHelper()

            # Authorization 헤더로 담음
            header = request.headers.get('Authorization')

            if header is None:
                return {"code": "err", "message": "Not Allow Authorization"}

            try:
                data = jwt.decode(header, "secret", algorithms=["HS256"])
            except Exception as e:
                return {"code": "err", "message": "Token Expired"}

            parser = reqparse.RequestParser()
            parser.add_argument('user_seq', type=int)
            parser.add_argument('score_title', type=str)
            parser.add_argument('score_content', type=str)
            parser.add_argument('score_value', type=int)
            parser.add_argument('score_type', type=str)
            # parser.add_argument('badge_nm', type=str)  # 추후 정규화를 생각해봐야 함..

            args = parser.parse_args()

            sql = "UPDATE score SET score_title = %s, score_content = %s, score_value = %s, score_type = %s WHERE volunteer_seq = %s AND work_seq = %s";

            db.cursor.execute(sql, (args['score_title'], args['score_content'], args['score_value'], args['score_type'], volunteer_seq, work_seq))

            sql = "SELECT sum(a.score_value) / count(c.user_seq) AS score_sum FROM score a, volunteer b, user c WHERE a.volunteer_seq = b.volunteer_seq " \
                  "AND b.user_seq = c.user_seq AND b.user_seq = %s"
            db.cursor.execute(sql, args['user_seq'])
            result = db.cursor.fetchone()

            result['score_sum'] = str(result['score_sum'])

            sql = "UPDATE user SET user_score = %s WHERE user_seq = %s";
            db.cursor.execute(sql, (result['score_sum'], args['user_seq']))

            db.conn.commit()

        except Exception as e:
            return {"code": "err", "message": str(e)}

        return {"code": "success"}
