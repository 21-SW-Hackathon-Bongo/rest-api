from flask import request
from flask_restplus import Namespace, fields, Resource, reqparse

import os
import sys

sys.path.append("..")

from lib.db_help import dbHelper

# 검색 파라미터 정보
Search = Namespace('search', description='일자리 이름 검색')


# 현재 Like문 버그 있음 수정해야 함
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

            # # 추후 수정
            # search_data = {"work_seq": result['work_seq'], "work_type_seq": result['work_type_seq'],
            #                "company_seq": result['company_seq'], "work_title": result['work_title'], "work_pay": result['work_pay'],
            #                "work_deposit_yn": result['work_deposit_yn'], "isDeleted": result['isDeleted']}

        except Exception as e:
            return {"code": "err", "message": str(e)}

        return {"code": "success", "data": result}


# 아이템 카테고리 파라미터 정보
Category = Namespace('category', description='일자리 카테고리 검색')


# 아이템 카테고리 검색 API
@Category.route('/category/<work_type_seq>')
@Category.response(200, 'OK')
@Category.response(500, 'Internal Error')
class Search_category(Resource):
    def get(self, work_type_seq):
        try:
            db = dbHelper()

            sql = "SELECT * FROM work " \
                  "WHERE work_deposit_yn = %s " \
                  "AND work_type_seq = %s AND isDeleted = %s";
            db.cursor.execute(sql, ('Y', work_type_seq, 'N'))
            result = db.cursor.fetchall()

        except Exception as e:
            return {"code": "err", "message": str(e)}

        return {"code": "success", "data": result}
