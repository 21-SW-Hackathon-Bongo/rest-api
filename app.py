from flask import Flask, Blueprint
from flask_restplus import Resource, Api
# API Import
from apis.member import Login, Member, IDCheck

app = Flask(__name__)

blueprint = Blueprint('api', __name__, url_prefix='/api')
api = Api(blueprint, version='1.0', title='Bongo API', )
app.register_blueprint(blueprint)

# 분류 별 Prefix로 Namespace를 추가해주세요
api.add_namespace(Login, '/member')			# 로그인
api.add_namespace(Member, '/member')		# 회원가입
api.add_namespace(IDCheck, '/member')		# 아이디 중복확인
"""
api.add_namespace(Business, '/business')	# 고용주 회원 관련
api.add_namespace(Job, '/job')				# 업무 관련
api.add_namespace(Calculate, '/calculate')	# 정산 관련
api.add_namespace(Deposit, '/deposit')		# 예치금 관련
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)