import jwt
import hashlib
from flask import request
from flask_restplus import Namespace, fields, Resource, reqparse

import os
import sys

sys.path.append("..")

from lib.db_help import dbHelper


# 회사 프로필 파라미터 정보
GetCPProfile = Namespace('get cp_profile', description='회사 프로필 조회')
default_model = GetCPProfile.model('data', {
    'token': fields.String,
})


# 회사 프로필 조회 API
@GetCPProfile.route('/<company_seq>')
@GetCPProfile.response(200, 'OK')
@GetCPProfile.response(500, 'Internal Error')
class Get_Profile(Resource):
    # @Search.expect(default_model)
    def get(self, company_seq):
        try:
            db = dbHelper()

            parser = reqparse.RequestParser()
            parser.add_argument('token', type=str)
            args = parser.parse_args()

            try:
                data = jwt.decode(args['token'], "secret", algorithms=["HS256"])
            except:
                return {"code": "err", "message": "Token Expired"}

            sql = "SELECT a.* b.user_nm AS owner_nm FROM company a, user b WHERE a.onwer_seq = b.user_seq AND company_seq = %s;"

            db.cursor.execute(sql, company_seq)
            result = db.cursor.fetchone()

            if result is None:
                return {"code": "err", "message": "Invalid User"}

            profile_data = {"company_nm": result['company_nm'], "company_intro": result['company_intro'],
                            "company_img": result['company_img'], "ower_nm": result['owner_nm']
                            }

        except Exception as e:
            return {"code": "err", "message": str(e)}

        return {"code": "success", "data": profile_data}



