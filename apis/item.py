
import pandas as pd
from flask import request
from flask_restplus import Namespace, fields, Resource, reqparse
from datetime import datetime
import jwt

import os
import sys

from markupsafe import escape

sys.path.append("..")

from lib.db_help import dbHelper


# 아이템 파라미터 정보
Work = Namespace('work', description='일자리 등록 및 단일 검색')


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

            data = {
                "work_seq": result['work_seq'], "work_type_nm": result['work_type_nm'], "company_seq": result['company_seq'], "company_nm": result['company_nm'],
                "work_title": result['work_title'], "work_intro": result['work_intro'], "work_img": result['work_img'], "work_startAt": str(result['work_startAt']),
                "work_endAt": str(result['work_endAt']), "work_recruit": result['work_recruit'], "work_pay": result['work_pay'], "work_deposit_yn": result['work_deposit_yn'],
                "isDeleted": result['isDeleted']
            }
        except Exception as e:
            return {"code": "err", "message": str(e)}

        return {"code": "success", "data": data}


# 등록 파라미터 정보
Apply = Namespace('apply', description='일차리 신청')
apply_work_model = Apply.model('apply work data', {
    'user_seq': fields.Integer,
    'work_seq': fields.Integer,
    'volunteer_content': fields.String,
})


# 아이템 신청 API
@Apply.route('/apply')
@Apply.response(200, 'OK')
@Apply.response(500, 'Internal Error')
@Apply.doc(params={'Authorization': {'in': 'header', 'description': 'An authorization token'}})
class Apply_Work(Resource):
    @Apply.expect(apply_work_model)
    def post(self):
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
            parser.add_argument('work_seq', type=int)
            parser.add_argument('volunteer_content', type=str)
            args = parser.parse_args()

            # sql = "SELECT * FROM volunteer where user_seq = %s AND work_seq = %s AND volunteer_yn = %s"
            # db.cursor.execute(sql, args['user_seq'], args['work_seq'], 'Y')
            # result = db.cursor.fetchall()
            #
            # if result is not None:
            #     return {"code": "err", "message": "Already have an apply"}

            sql = "INSERT into volunteer(user_seq, work_seq, volunteer_content, volunteer_yn) VALUES (%s, %s, %s, %s)"
            db.cursor.execute(sql, (args['user_seq'], args['work_seq'], args['volunteer_content'], 'Y'))

            # sql = "UPDATE work SET work_recruit = work_recruit - 1 WHERE work_seq = %s"
            # db.consuor.execute(sql, args['work_seq'])
            db.conn.commit()

        except Exception as e:
            return {"code": "err", "message": str(e)}

        return {"code": "success"}


# 취소 파라미터 정보
Cancel = Namespace('cancel', description='일자리 신청 취소')

cancle_work_model = Apply.model('cancle work data', {
    'user_seq': fields.Integer,
})


# 아이템 취소 API
@Cancel.route('/cancel/<work_seq>')
@Cancel.response(200, 'OK')
@Cancel.response(500, 'Internal Error')
@Cancel.doc(params={'Authorization': {'in': 'header', 'description': 'An authorization token'}})
class Cancel_Work(Resource):
    @Apply.expect(cancle_work_model)
    def put(self, work_seq):
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
            args = parser.parse_args()

            sql = "UPDATE volunteer SET volunteer_yn = %s WHERE work_seq = %s AND user_seq = %s AND volunteer_yn = 'Y'"
            db.cursor.execute(sql, ('N', work_seq, args['user_seq']))
            # sql = "UPDATE work SET work_recruit = work_recruit + 1 WHERE work_seq = %s"
            # db.consuor.execute(sql, args['work_seq'])
            db.conn.commit()

        except Exception as e:
            return {"code": "err", "message": str(e)}

        return {"code": "success"}


# 일자리 신규 등록 파라미터
# Work = Namespace('work', description='일자리 신규 등록')

post_work_model = Apply.model('post work data', {
    'work_type_seq': fields.Integer,
    'company_seq': fields.Integer,
    'work_title': fields.String,
    'work_startAt': fields.Integer,
    'work_endAt': fields.Integer,
    'work_recruit': fields.Integer,
    'work_pay': fields.Integer,
    'work_intro': fields.String,
})


# 일자리 신규 등록 API
@Work.route('/')
@Work.response(200, 'OK')
@Work.response(500, 'Internal Error')
@Work.doc(params={'Authorization': {'in': 'header', 'description': 'An authorization token'}})
class Apply_Work(Resource):
    @Apply.expect(post_work_model)
    def post(self):
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
            parser.add_argument('work_type_seq', type=int)
            parser.add_argument('company_seq', type=int)
            parser.add_argument('work_title', type=str)
            parser.add_argument('work_startAt', type=int)
            parser.add_argument('work_endAt', type=int)
            parser.add_argument('work_recruit', type=int)
            parser.add_argument('work_pay', type=int)
            parser.add_argument('work_intro', type=str)

            args = parser.parse_args()

            sql = "INSERT into work(work_type_seq, company_seq, work_title, work_recruit, work_pay, work_intro, work_startAt, work_endAt) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

            db.cursor.execute(sql, (args['work_type_seq'], args['company_seq'], args['work_title'], args['work_recruit'], args['work_pay'], args['work_intro'], args['work_startAt'], args['work_endAt']))
            db.conn.commit()
        except Exception as e:
            return {"code": "err", "message": str(e)}

        return {"code": "success"}


