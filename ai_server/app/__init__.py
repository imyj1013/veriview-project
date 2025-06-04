from flask import Flask
from flask_cors import CORS
import os
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    CORS(app)  # 모든 도메인에서의 요청 허용
    
    # 블루프린트 또는 라우터 등록
    from .routes import debate_bp
    app.register_blueprint(debate_bp, url_prefix='/ai')
    
    # 인터뷰 라우트 등록
    from .routes.interview import interview_bp
    app.register_blueprint(interview_bp, url_prefix='/ai/interview')
    
    # 기업공고 추천 라우트 등록
    from .routes.recruitment import recruitment_bp
    app.register_blueprint(recruitment_bp, url_prefix='/ai/recruitment')
    
    return app

# 앱 인스턴스 생성
app = create_app()
