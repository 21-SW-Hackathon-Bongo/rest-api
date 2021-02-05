from bson import json_util
import json
from flask import request
from flask_restplus import Namespace, fields, Resource, reqparse

import os
import sys

from jsonsir.contrib.datetimeencoder import DateTimeEncoder

sys.path.append("..")

from lib.db_help import dbHelper

Calculate = Namespace('calculate', description='일일 정산')
calculate_model = Calculate.model('calculate data', {
    'user_seq': fields.Integer,
})


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

            sql = "SELECT TIMESTAMPDIFF(minute, now(), MAX(a.work_endAt)) AS deadline FROM bongo.work a, bongo.volunteer b WHERE a.work_seq = b.work_seq AND b.user_seq = %s ORDER BY a.work_endAt ASC";

            db.cursor.execute(sql, args['user_seq'])
            result = db.cursor.fetchall()

            # JSON오류..
            # sql = "SELECT a.work_seq, a.work_title, a.work_pay, a.work_startAt, a.work_endAt FROM bongo.work a, bongo.volunteer b WHERE a.work_startAt < now() AND a.work_seq = b.work_seq AND b.user_seq = %s;"
            #
            # db.cursor.execute(sql, args['user_seq'])
            result1 = db.cursor.fetchall()

            # for i in result1:
            #     print(result1(i))

        except Exception as e:
            return {"code": "err", "message": str(e)}

        return {"code": "success", "data": result}


Calculate_price = Namespace('calculate price', description='일일 총 금액')


@Calculate_price.route('/price')
@Calculate_price.response(200, 'OK')
@Calculate_price.response(500, 'Internal Error')
class Get_Calculate_Price(Resource):
    @Calculate_price.expect(calculate_model)
    def post(self):
        try:
            db = dbHelper()

            parser = reqparse.RequestParser()
            parser.add_argument('user_seq', type=int)
            args = parser.parse_args()

            sql = "SELECT sum(a.work_pay) AS total_price FROM bongo.work a, bongo.volunteer b WHERE b.user_seq = %s AND b.work_seq = a.work_seq AND b.volunteer_createAt BETWEEN DATE_ADD(NOW(),INTERVAL -1 DAY ) AND NOW()";

            db.cursor.execute(sql, args['user_seq'])
            result = db.cursor.fetchone()

            result['total_price'] = str(result['total_price'])

        except Exception as e:
            return {"code": "err", "message": str(e)}

        return {"code": "success", "data": result['total_price']}




