from flask import Flask, Blueprint
from flask_restplus import Resource, Api
# API Import
# from apis.calculate import Calculate
from apis.calculate import Calculate
from apis.company import GetCPProfile
from apis.deposit import Deposit
from apis.employee import SetEmployeeEnd, PutEmployeeEnd
from apis.member import CPCheck, SetInterest, SetProfile, GetProfile, IDCheck, Join, Login
from apis.search import Search, Category
from apis.item import Work, Apply, Cancel
from apis.volunteer import GetVolunteer, SetVolunteer

app = Flask(__name__)

blueprint = Blueprint('api', __name__, url_prefix='/api')
api = Api(blueprint, version='1.0', title='Bongo API', )
app.register_blueprint(blueprint)

# 분류 별 Prefix로 Namespace를 추가해주세요
api.add_namespace(Login, '/member')  # 로그인
api.add_namespace(Join, '/member')  # 회원가입
api.add_namespace(IDCheck, '/member')		# 아이디 중복확인
api.add_namespace(CPCheck, '/member')       # 회사 중복확인
api.add_namespace(GetProfile, '/member')    # 프로필 조회
api.add_namespace(SetProfile, '/member')	# 프로필 등록
api.add_namespace(SetInterest, '/member')	# 관심분야 등록


api.add_namespace(Search, '/search')		# 전체 검색
api.add_namespace(Category, '/search')		# 카테고리 검색


api.add_namespace(Work, '/work')		    # 상품 단일 검색
api.add_namespace(Apply, '/work')		    # 일자리 신청
api.add_namespace(Cancel, '/work')		    # 일자리 신청 취소


api.add_namespace(GetCPProfile, '/company')	# 회사 프로필 조회

api.add_namespace(GetVolunteer, '/work')	# 지원자 조회
api.add_namespace(SetVolunteer, '/work')	# 지원자 승인

api.add_namespace(SetEmployeeEnd, '/work')	# 평점 등록
api.add_namespace(PutEmployeeEnd, '/work')	# 평점 수정

api.add_namespace(Deposit, '/deposit')	# 회사 프로필 조회

api.add_namespace(Calculate, '/calculate') # 정산
"""
api.add_namespace(Business, '/business')	# 고용주 회원 관련
api.add_namespace(Job, '/job')				# 업무 관련
api.add_namespace(Calculate, '/calculate')	# 정산 관련
api.add_namespace(Deposit, '/deposit')		# 예치금 관련
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)