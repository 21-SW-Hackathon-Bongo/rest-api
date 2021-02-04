from flask import request
from flask_restplus import Namespace, fields, Resource, reqparse
import jwt

import os
import sys

from markupsafe import escape

sys.path.append("..")

from lib.db_help import dbHelper


# 아이템 파라미터 정보
Work = Namespace('work', description='일자리 단일 검색')


# 아이템 단일 검색 API
@Work.route('/<work_seq>')
@Work.response(200, 'OK')
@Work.response(500, 'Internal Error')
class Single_Work(Resource):
    # @Work.expect(work_model)
    def get(self, work_seq):
        try:
            db = dbHelper()

            sql = "SELECT * FROM work a, work_type b, company c WHERE c.company_seq = a.company_seq AND a.work_type_seq = b.work_type_seq AND a.work_seq = %s";

            db.cursor.execute(sql, work_seq)
            result = db.cursor.fetchone()

        except Exception as e:
            return {"code": "err", "message": str(e)}

        return {"code": "success", "data": result}


# 등록 파라미터 정보
Apply = Namespace('apply', description='일차리 신청')
apply_work_model = Apply.model('apply data', {
    'user_seq': fields.Integer,
    'work_seq': fields.Integer,
    'volunteer_content': fields.String,
})


# 아이템 신청 API
@Apply.route('/apply')
@Apply.response(200, 'OK')
@Apply.response(500, 'Internal Error')
class Apply_Work(Resource):
    @Apply.expect(apply_work_model)
    def post(self):
        try:
            db = dbHelper()

            # # Authorization 헤더로 담음
            # header = request.headers.get('Authorization')
            # if header is None:
            #     return {"code": "err", "message": "Not Allow Authorization"}
            #
            # data = jwt.decode(header, "secret", algorithm="HS256")

            parser = reqparse.RequestParser()
            parser.add_argument('user_seq', type=int)
            parser.add_argument('work_seq', type=int)
            parser.add_argument('volunteer_content', type=str)
            args = parser.parse_args()

            sql = "INSERT into volunteer(user_seq, work_seq, volunteer_content) VALUES (%s, %s, %s)"
            db.cursor.execute(sql, (args['user_seq'], args['work_seq'], args['volunteer_content']))
            db.conn.commit()

        except Exception as e:
            return {"code": "err", "message": str(e)}

        return {"code": "success"}


# 취소 파라미터 정보
Cancel = Namespace('cancel', description='일자리 신청 취소')


# 아이템 취소 API
@Cancel.route('/cancel')
@Cancel.response(200, 'OK')
@Cancel.response(500, 'Internal Error')
class Cancel_Work(Resource):
    # @Cancel.expect()
    def update(self):
        try:
            db = dbHelper()
            # Authorization 헤더로 담음
            header = request.headers.get('Authorization')
            if header is None:
                return {"code": "err", "message": "Not Allow Authorization"}

            data = jwt.decode(header, "secret", algorithm="HS256")

            work_seq = request.GET['work_seq']
            sql = "UPDATE volunteer SET volunteer_yn = param['work_type_seq']"
            # db.cursor.execute(sql, (param['work_type_seq'])
            db.conn.commit()

        except Exception as e:
            return {"code": "err", "message": str(e)}

        return {"code": "success"}


