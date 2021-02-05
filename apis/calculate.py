from bson import json_util
import json
from flask import request
from flask_restplus import Namespace, fields, Resource, reqparse

import os
import sys

from jsonsir.contrib.datetimeencoder import DateTimeEncoder

sys.path.append("..")

from lib.db_help import dbHelper

# 검색 파라미터 정보
Calculate = Namespace('calculate', description='정산')
calculate_model = Calculate.model('calculate data', {
    'user_seq': fields.Integer,
})
# 검색 API
@Calculate.route('/')
@Calculate.response(200, 'OK')
@Calculate.response(500, 'Internal Error')
class Get_Calculate(Resource):
    @Calculate.expect(calculate_model)
    def post(self):
        try:
            db = dbHelper()

            parser = reqparse.RequestParser()
            parser.add_argument('user_seq', type=int)
            args = parser.parse_args()

            sql = "SELECT TIMESTAMPDIFF(minute, now(), MIN(a.work_endAt)) AS deadline FROM bongo.work a, bongo.volunteer b WHERE a.work_seq = b.work_seq AND b.user_seq = %s ORDER BY a.work_endAt ASC";

            db.cursor.execute(sql, args['user_seq'])
            result = db.cursor.fetchall()

            sql = "SELECT a.work_seq, a.work_title, a.work_pay, a.work_startAt, a.work_endAt FROM bongo.work a, bongo.volunteer b WHERE a.work_startAt < now() AND a.work_seq = b.work_seq AND b.user_seq = %s;"

            db.cursor.execute(sql, args['user_seq'])
            result1 = db.cursor.fetchall()

            for i in result1:
                print(result1(i))

        except Exception as e:
            return {"code": "err", "message": str(e)}

        return {"code": "success", "data": result}



# # 정산 완료 후 평가
# Calculate_judge = Namespace('calculate judge', description='정산 완료 후 평가')
#
# # 검색 API
# @Calculate_judge.route('/judge')
# @Calculate_judge.response(200, 'OK')
# @Calculate_judge.response(500, 'Internal Error')
# class Calculate_judge(Resource):
#     def post(self):
#         try:
#             db = dbHelper()
#
#             sql = "SELECT * FROM volunteer a WHERE "
#
#             db.cursor.execute(sql, )
#             result = db.cursor.fetchall()
#
#
#         except Exception as e:
#             return {"code": "err", "message": str(e)}
#
#         return {"code": "success", "data": result}