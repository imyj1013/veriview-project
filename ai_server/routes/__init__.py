"""
API 라우터 패키지
Flask API 엔드포인트 라우팅 모듈
"""

from .common_routes import register_common_routes
from .debate_routes import register_debate_routes
from .interview_routes import register_interview_routes
from .job_routes import register_job_routes

def register_all_routes(app):
    """
    모든 라우트 등록
    
    Args:
        app: Flask 앱 인스턴스
    """
    register_common_routes(app)
    register_debate_routes(app)
    register_interview_routes(app)
    register_job_routes(app)
