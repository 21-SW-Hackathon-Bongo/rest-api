from flask import request
from flask_restplus import Namespace, fields, Resource, reqparse

import os
import sys

sys.path.append("..")

from lib.db_help import dbHelper

# 검색 파라미터 정보
Search = Namespace('search', description='아이템 이름 검색')
# search_model = Search.model('search data', {
#     'work_title': fields.String,
#     'work_intro': fields.String,
#     'work_img': fields.String,
#     'work_startAt': fields.datetime,
#     'work_endAt': fields.datetime,
#     'work_recruit': fields.Integer,
#     'work_pay': fields.Integer,
#     'work_deposit_yn': fields.String,
# })


# 검색 API
@Search.route('/<work_nm>')
@Search.response(200, 'OK')
@Search.response(500, 'Internal Error')
class Search_nm(Resource):
    # @Search.expect(search_model)
    def get(self, work_nm):
        try:
            db = dbHelper()

            sql = "SELECT * FROM work a, work_type b, company c WHERE c.company_seq = a.company_seq AND a.work_type_seq = b.work_type_seq AND a.work_title LIKE %s AND a.work_deposit_yn = 'Y'";

            db.cursor.execute(sql, '%' + work_nm)
            result = db.cursor.fetchone()

        except Exception as e:
            return {"code": "err", "message": str(e)}

        return {"code": "success", "data": result}


# 아이템 카테고리 파라미터 정보
Category = Namespace('category', description='카테고리를 통한 아이템 검색')
# category_work_model = Category.model('data', {
#     'work_title': fields.String,
#     'work_img': fields.String,
#     'work_pay': fields.Integer,
#     'work_deposit_yn': fields.String,
# })


# 아이템 카테고리 검색 API
@Category.route('/category/<work_type_seq>')
@Category.response(200, 'OK')
@Category.response(500, 'Internal Error')
class Search_category(Resource):
    # @Category.expect(category_work_model)
    def get(self, work_type_seq):
        try:
            db = dbHelper()

            sql = "SELECT * FROM work a, work_type b WHERE a.work_type_seq = b.work_type_seq AND a.work_deposit_yn = 'Y' AND a.work_type_seq = %s";
            db.cursor.execute(sql, work_type_seq)
            result = db.cursor.fetchmany()

        except Exception as e:
            return {"code": "err", "message": str(e)}

        return {"code": "success", "data": result}
