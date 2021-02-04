from flask import request
from flask_restplus import Namespace, fields, Resource, reqparse

import os
import sys

sys.path.append("..")

from lib.db_help import dbHelper

# 검색 파라미터 정보
Search = Namespace('search', description='아이템 이름 검색')


# 검색 API
@Search.route('/<work_nm>')
@Search.response(200, 'OK')
@Search.response(500, 'Internal Error')
class Search_nm(Resource):
    def get(self, work_nm):
        try:
            db = dbHelper()

            sql = "SELECT * FROM work a, work_type b, company c WHERE c.company_seq = a.company_seq AND a.work_type_seq = b.work_type_seq AND a.work_title LIKE %s AND a.work_deposit_yn = 'Y'";

            db.cursor.execute(sql, '%' + work_nm)
            result = db.cursor.fetchall()

        except Exception as e:
            return {"code": "err", "message": str(e)}

        return {"code": "success", "data": result}


# 아이템 카테고리 파라미터 정보
Category = Namespace('category', description='카테고리를 통한 아이템 검색')


# 아이템 카테고리 검색 API
@Category.route('/category/<work_type_seq>')
@Category.response(200, 'OK')
@Category.response(500, 'Internal Error')
class Search_category(Resource):
    def get(self, work_type_seq):
        try:
            db = dbHelper()

            sql = "SELECT * FROM work a WHERE AND a.work_deposit_yn = 'Y' AND a.work_type_seq = %s AND a.isDeleted = %s";
            db.cursor.execute(sql, work_type_seq, 'N')
            result = db.cursor.fetchall()

        except Exception as e:
            return {"code": "err", "message": str(e)}

        return {"code": "success", "data": result}
